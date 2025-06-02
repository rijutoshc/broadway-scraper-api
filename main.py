from flask import Flask, request, jsonify
from playwright.sync_api import sync_playwright
import re

app = Flask(__name__)

@app.route('/')
def home():
    return "Broadway Scraper Address Extractor is live!"

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

            # Extract the full address block text from #venue
            venue_el = page.query_selector('#venue')
            if not venue_el:
                browser.close()
                return jsonify({"error": "Venue block not found"}), 404

            venue_text = venue_el.inner_text().strip()
            lines = [line.strip() for line in venue_text.split('\n') if line.strip()]

            # Expecting at least 3 lines
            if len(lines) < 3:
                browser.close()
                return jsonify({"error": "Incomplete address format"}), 500

            address_line_1 = lines[0]  # Theatre name
            address_line_2 = lines[1]  # Street
            city = state = pincode = None

            # Parse city/state/pincode from third line
            last_line = lines[2]
            match = re.match(r"(.+),\s*([A-Z]{2})\s*(\d{5})", last_line)
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
                    "pincode": pincode
                }
            })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
