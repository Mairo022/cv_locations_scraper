import random
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urlparse, parse_qs

URL = "https://cv.ee/et"
SLEEP_MIN = 0.5
SLEEP_MAX = 5

locations_map = dict()


def main():
    options = webdriver.ChromeOptions()
    options.binary_location = '/usr/bin/brave-browser'
    options.page_load_strategy = 'eager'

    browser = webdriver.Chrome(options=options)
    handle_locations(browser)
    write_locations_to_file(locations_map)
    print("Program has successfully finished")


def handle_locations(browser):
    browser.get(URL)
    # Opens locations menu
    locations_menu = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".react-select__indicators")))
    locations_menu.click()
    # Find all location groups
    location_groups = WebDriverWait(browser, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".react-select__group")))
    groups_amount = len(location_groups)

    # Go through all location groups
    for i in range(1, groups_amount):
        if i > 1:
            locations_menu = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".react-select__indicators")))
            locations_menu.click()
            location_groups = WebDriverWait(browser, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".react-select__group")))

        location_group = location_groups[i]
        locations = location_group.find_elements(By.CSS_SELECTOR, ".react-select__option")
        locations_amount = len(locations)

        # Go through all locations and find ID
        for j in range(0, locations_amount):
            if j != 0:
                locations_menu = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".react-select__indicators")))
                locations_menu.click()
                location_groups = WebDriverWait(browser, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".react-select__group")))
                location_group = location_groups[i]
                locations = location_group.find_elements(By.CSS_SELECTOR, ".react-select__option")

            submit = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".link-button__narrow")))
            location = locations[j]
            area = format_area_text(location.text)

            if is_location_disabled(location.get_attribute("class")):
                print("Skipped ", area)
                locations_menu.click()
                continue

            location.click()
            submit.click()
            time.sleep(random.uniform(SLEEP_MIN, SLEEP_MAX))
            get_save_location_id(browser, area)

        # Save group's locations to a file
        write_locations_to_file(locations_map)
        locations_map.clear()


def get_save_location_id(browser, area):
    url = browser.current_url
    parsed_url = urlparse(url)
    query_parameters = parse_qs(parsed_url.query)

    if "towns[0]" in query_parameters:
        area_id = query_parameters["towns[0]"][0]
        locations_map[area] = area_id
        print(area + " " + area_id)

    browser.execute_script("window.history.go(-1)")


def write_locations_to_file(locations):
    with open("cv_locations.txt", "a") as f:
        for key, value in locations.items():
            f.write(f"{key} {value}\n")


def is_location_disabled(location):
    return "react-select__option--is-disabled" in location.split()


def format_area_text(input_area):
    return ''.join(text for text in input_area.split() if not text.startswith("("))


main()
