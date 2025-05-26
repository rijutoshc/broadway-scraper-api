from flask import Flask, request, jsonify
from playwright.sync_api import sync_playwright
from urllib.parse import urlparse, parse_qs
import re

app = Flask(__name__)

@app.route('/')
def home():
    return "Broadway Scraper API with Playwright is live!"

@app.route('/get_address')
def get_address():
    show_name = request.args.get('show')
    if not show_name:
        return jsonify({"error": "Missing 'show' query parameter"}), 400

    slug = show_name.lower().replace(' ', '-')
    url = f"https://www.broadwayinbound.com/shows/{slug}"

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=["--disable-dev-shm-usage", "--no-sandbox"])
            page = browser.new_page()
            page.goto(url, timeout=30000, wait_until="domcontentloaded")

            # Extract theatre name
            theatre_element = page.query_selector('#venue strong')
            theatre_name = theatre_element.inner_text().strip() if theatre_element else None

            # Locate Google Maps link
            link = page.query_selector('a[href*="maps.google.com"]')
            venue_link = link.get_attribute('href') if link else None

            if not venue_link:
                browser.close()
                return jsonify({"error": "Venue link not found"}), 404

            # Parse raw address from the URL
            parsed_url = urlparse(venue_link)
            query = parse_qs(parsed_url.query)
            raw_address = query.get('q', [None])[0]

            # Initialize output fields
            address_line_1 = theatre_name or ""
            address_line_2 = ''
            city = None
            state = None
            pincode = None
            x_coord = None
            y_coord = None

            if raw_address:
                # Use regex to extract address components
                match = re.match(r"(.+?)\s+([A-Za-z\s]+),([A-Z]{2})\s+(\d{5})", raw_address)
                if match:
                    address_line_2 = match.group(1).strip()
                    city = match.group(2).strip()
                    state = match.group(3).strip()
                    pincode = match.group(4).strip()
                else:
                    address_line_2 = raw_address

            # === Open Google Maps in new tab and extract coordinates ===
            try:
                new_page = browser.new_page()
                new_page.goto(venue_link, timeout=15000, wait_until="domcontentloaded")
                new_page.wait_for_timeout(5000)  # wait for map to load

                final_url = new_page.url
                if '@' in final_url:
                    coords = final_url.split('@')[-1].split(',')[:2]
                    x_coord = coords[0].strip()
                    y_coord = coords[1].strip()

                new_page.close()
            except Exception:
                pass  # ignore map failures

            browser.close()

            return jsonify({
                "show": show_name,
                "venue_link": venue_link,
                "address": {
                    "address_line_1": address_line_1,
                    "address_line_2": address_line_2,
                    "city": city,
                    "state": state,
                    "pincode": pincode
                },
                "x_coord": x_coord,
                "y_coord": y_coord
            })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
