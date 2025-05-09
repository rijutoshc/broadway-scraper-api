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


