from flask import Flask, request, jsonify
from playwright.sync_api import sync_playwright
from urllib.parse import urlparse, parse_qs

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

            # Locate venue link
            page.wait_for_selector('a[href*="maps.google.com"]', timeout=10000)
            link = page.query_selector('a[href*="maps.google.com"]')

            if not link:
                browser.close()
                return jsonify({"error": "Venue link not found"}), 404

            venue_link = link.get_attribute('href')

            # Extract address from ?q= in URL
            parsed_url = urlparse(venue_link)
            query = parse_qs(parsed_url.query)
            raw_address = query.get('q', [None])[0]

            # Default values
            address_line_1 = ''
            address_line_2 = ''
            city = None
            state = None
            pincode = None
            x_coord = None
            y_coord = None

            # === Improved address parser ===
            if raw_address:
                parts = raw_address.replace(',', '').split()

                try:
                    if len(parts) >= 5:
                        # Assume last two parts are state and pincode
                        pincode = parts[-1]
                        state = parts[-2]

                        # Detect 2-word city names like "New York"
                        possible_city_parts = parts[-4:-2]
                        if (
                            len(possible_city_parts) == 2 and 
                            possible_city_parts[0][0].isupper() and 
                            possible_city_parts[1][0].isupper()
                        ):
                            city = ' '.join(possible_city_parts)
                            address_line_1 = ' '.join(parts[:-4])
                        else:
                            city = parts[-3]
                            address_line_1 = ' '.join(parts[:-3])
                    else:
                        address_line_1 = raw_address
                except Exception:
                    address_line_1 = raw_address

            # === Open Google Maps URL in a new tab and fetch coordinates ===
            try:
                new_page = browser.new_page()
                new_page.goto(venue_link, timeout=15000, wait_until="domcontentloaded")
                new_page.wait_for_timeout(5000)  # wait 5 seconds

                final_url = new_page.url
                if '@' in final_url:
                    coords = final_url.split('@')[-1].split(',')[:2]
                    x_coord, y_coord = coords[0].strip(), coords[1].strip()

                new_page.close()
            except Exception:
                pass  # skip errors silently

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
