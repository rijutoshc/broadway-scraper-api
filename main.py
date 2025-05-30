from flask import Flask, request, jsonify
from playwright.sync_api import sync_playwright
from urllib.parse import urlparse, parse_qs
import re
import requests
import os

# Set your Google API Key here or as an environment variable
GOOGLE_API_KEY = os.environ.get("GOOGLE_GEOCODING_API_KEY", "AIzaSyChZE0eDh14KYRXlZmWK3cXSbo94iW88-o")

app = Flask(__name__)

@app.route('/')
def home():
    return "Broadway Scraper API with Playwright + Geocoding is live!"

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

            # Extract venue name
            theatre_element = page.query_selector('#venue a')
            theatre_name = theatre_element.inner_text().strip() if theatre_element else ""

            # Extract Google Maps link
            link = page.query_selector('a[href*="maps.google.com"]')
            venue_link = link.get_attribute('href') if link else None

            if not venue_link:
                browser.close()
                return jsonify({"error": "Venue link not found"}), 404

            # Extract raw address from GMaps link
            parsed_url = urlparse(venue_link)
            query = parse_qs(parsed_url.query)
            raw_address = query.get('q', [None])[0]

            # Default values
            address_line_1 = theatre_name
            address_line_2 = ''
            city = None
            state = None
            pincode = None
            x_coord = None
            y_coord = None

            if raw_address:
                # Regex pattern: e.g., "200 West 45 Street New York,NY 10036"
                match = re.match(r"(.+?)\s+([A-Za-z\s]+),([A-Z]{2})\s+(\d{5})", raw_address)
                if match:
                    address_line_2 = match.group(1).strip()         # e.g. 200 West 45 Street
                    city = match.group(2).strip()                   # e.g. New York
                    state = match.group(3).strip()                  # e.g. NY
                    pincode = match.group(4).strip()                # e.g. 10036
                else:
                    address_line_2 = raw_address

                # === Geocoding API to fetch coordinates ===
                geocode_url = (
                    f"https://maps.googleapis.com/maps/api/geocode/json?address={raw_address}&key={GOOGLE_API_KEY}"
                )
                response = requests.get(geocode_url)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("results"):
                        location = data["results"][0]["geometry"]["location"]
                        x_coord = location.get("lat")
                        y_coord = location.get("lng")

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
