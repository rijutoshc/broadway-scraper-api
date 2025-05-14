from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import traceback
import os
import subprocess

app = Flask(__name__)

@app.route('/')
def home():
    return "Broadway Scraper API is live!"

@app.route('/get_address')
def get_address():
    show_name = request.args.get('show')
    if not show_name:
        return jsonify({"error": "Missing 'show' query parameter"}), 400

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # Dynamically find the Chromium binary location
    chromium_path = subprocess.getoutput("which chromium")  # Search for Chromium binary path
    if not chromium_path:
        chromium_path = subprocess.getoutput("which chromium-browser")  # Search for chromium-browser path
    if not chromium_path:
        return jsonify({"error": "Chromium binary not found on the system"}), 500

    options.binary_location = chromium_path

    try:
        # Use the dynamically managed ChromeDriver
       driver = webdriver.Chrome(
    service=Service("/usr/bin/chromedriver"),
    options=options
)


        url = f"https://www.broadwayinbound.com/shows/{show_name.lower().replace(' ', '-')}"
        driver.get(url)

        venue_element = driver.find_element(By.XPATH, '//*[@id="venue"]/a')
        venue_link = venue_element.get_attribute('href')

        if '@' in venue_link:
            coordinates = venue_link.split('@')[-1]
            x_coord, y_coord = coordinates.split(',')[:2]
        else:
            x_coord, y_coord = None, None

        driver.quit()

        return jsonify({
            "show": show_name,
            "venue_link": venue_link,
            "x_coord": x_coord.strip() if x_coord else None,
            "y_coord": y_coord.strip() if y_coord else None
        })

    except Exception as e:
        error_msg = traceback.format_exc()
        print(error_msg)
        return jsonify({"error": str(e), "trace": error_msg}), 500

if __name__ == '__main__':
    app.run(debug=True)
