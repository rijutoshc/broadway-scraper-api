from flask import Flask, request, jsonify
from playwright.sync_api import sync_playwright

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
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=15000)

            # Wait for the venue section to load
            page.wait_for_selector('a[href*="maps.google.com"]', timeout=10000)
            link = page.query_selector('a[href*="maps.google.com"]')

            if not link:
                return jsonify({"error": "Venue link not found"}), 404

            venue_link = link.get_attribute('href')

            if '@' in venue_link:
                coords = venue_link.split('@')[-1]
                x_coord, y_coord = coords.split(',')[:2]
            else:
                x_coord = y_coord = None

            browser.close()

            return jsonify({
                "show": show_name,
                "venue_link": venue_link,
                "x_coord": x_coord.strip() if x_coord else None,
                "y_coord": y_coord.strip() if y_coord else None
            })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
