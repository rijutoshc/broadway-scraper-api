from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

app = Flask(__name__)  # FIXED: __name__, not _name_

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
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    url = f"https://www.broadwayinbound.com/shows/{show_name.lower().replace(' ', '-')}"
    driver.get(url)

    try:
        venue_element = driver.find_element(By.XPATH, '//*[@id="venue"]/a')
        venue_link = venue_element.get_attribute('href')

        # Extract coordinates from the href (after the '@' in the URL)
        if '@' in venue_link:
            coordinates = venue_link.split('@')[-1]
            x_coord, y_coord = coordinates.split(',')[:2]
        else:
            x_coord, y_coord = None, None

    except Exception as e:
        driver.quit()
        return jsonify({"error": str(e)}), 500

    driver.quit()

    return jsonify({
        "show": show_name,
        "venue_link": venue_link,
        "x_coord": x_coord.strip() if x_coord else None,
        "y_coord": y_coord.strip() if y_coord else None
    })

if __name__ == "__main__":  # FIXED: __name__ and __main__, not _name_ or _main_
    app.run(debug=True)
from flask import Flask, request
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

app= Flask(_name_)
@app.route('/get_address')
def get_address():
show_name = request.args.get('show')

options = Options()
options.add_argument("--headless")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=options)
driver.get(f"https://www.broadwayinbound.com/shows/{show_name.lower().replace('','-')}")
venue_element = driver.find_element(By.XPATH,'//*[@id="venue"]/a')
venue_link = venue.element.get_attribute('href')
coordinates = venue.element.text.split('@')[-1]
x_coord, y_coord = coordinates. split(',')

driver.quit()

return{
"show":show_name,
"venue_link": venue_link,
"x_coord": x_coord.strip(),
"y_coord": y_coord.strip()
}

if _name_ == "_main_":
app.run(debug=True)


