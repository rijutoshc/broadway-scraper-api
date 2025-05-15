from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/')
def home():
    return "Broadway Scraper API is live!"

@app.route('/get_address')
def get_address():
    show_name = request.args.get('show')
    if not show_name:
        return jsonify({"error": "Missing 'show' query parameter"}), 400

    try:
        slug = show_name.lower().replace(' ', '-')
        url = f"https://www.broadwayinbound.com/shows/{slug}"
        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            return jsonify({"error": f"Failed to fetch page. Status code: {response.status_code}"}), 502

        soup = BeautifulSoup(response.text, 'html.parser')
        venue_link_tag = soup.select_one('#venue a')

        if not venue_link_tag:
            return jsonify({"error": "Venue link not found"}), 404

        venue_link = venue_link_tag.get('href')
        if '@' in venue_link:
            coords = venue_link.split('@')[-1]
            x_coord, y_coord = coords.split(',')[:2]
        else:
            x_coord = y_coord = None

        return jsonify({
            "show": show_name,
            "venue_link": venue_link,
            "x_coord": x_coord.strip() if x_coord else None,
            "y_coord": y_coord.strip() if y_coord else None
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
