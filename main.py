from flask import Flask, request, jsonify
from playwright.sync_api import sync_playwright
import re

app = Flask(__name__)

@app.route('/')
def home():
    return "Broadway Address Scraper is live!"

@app.route('/get_address')
def get_address():
    show_name = request.args.get('show')
    if not show_name:
        return jsonify({"error": "Missing 'show' query parameter"}), 400

    slug = show_name.lower().replace(' ', '-')
    url = f"https://www.broadwayinbound.com/shows/{slug}"

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
            page = browser.new_page()
            page.goto(url, timeout=30000, wait_until="domcontentloaded")

            venue_blocks = page.query_selector_all('div.col-sm-4.col-xs-6')
            venue_block = None
            for block in venue_blocks:
                if "Venue" in block.inner_text() and "maps.google.com" in block.inner_html():
                    venue_block = block
                    break

            if not venue_block:
                return jsonify({"error": "Venue block not found"}), 404

            # Theatre name and venue link
            theatre_el = venue_block.query_selector('a[href*="maps.google.com"]')
            address_line_1 = theatre_el.inner_text().strip() if theatre_el else ""
            venue_link = theatre_el.get_attribute('href') if theatre_el else ""

            lines = [line.strip().strip('"') for line in venue_block.inner_text().split('\n') if line.strip()]
            address_line_2 = lines[2] if len(lines) > 2 else ""
            city_line = lines[3] if len(lines) > 3 else ""

            city, state, pincode = None, None, None
            match = re.match(r'(.+),\s*([A-Z]{2})\s+(\d{5})', city_line)
            if match:
                city = match.group(1).strip()
                state = match.group(2).strip()
                pincode = match.group(3).strip()

            browser.close()

            return jsonify({
                "address": {
                    "address_line_1": address_line_1,
                    "address_line_2": address_line_2,
                    "city": city,
                    "state": state,
                    "pincode": pincode,
                    "venue_link": venue_link
                }
            })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
