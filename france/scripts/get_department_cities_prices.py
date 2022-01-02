import argparse
from time import sleep
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys
import csv
from unidecode import unidecode
import datetime
from more_itertools import unique_everseen
import subprocess
import shutil
import os
from pathlib import Path


def check_exists_by_xpath(xpath):
    try:
        driver.find_element_by_xpath(xpath)
    except NoSuchElementException:
        return False
    return True


# remove duplicates, sort and encode CSV to UTF-8
def normalize_CSV():
    no_duplicates_csv_filename = csv_output_filename.replace(
        ".csv", "-no-duplicates.csv"
    )
    with open(csv_output_filename, "r") as f, open(
        no_duplicates_csv_filename, "w"
    ) as out_file:
        out_file.writelines(unique_everseen(f))

    os.remove(csv_output_filename)

    with open(no_duplicates_csv_filename, newline="") as csvfile:
        csvreader = csv.DictReader(csvfile)
        sortedlist = sorted(
            csvreader, key=lambda row: unidecode(row["city_name"]), reverse=False
        )

    sorted_csv_filename = no_duplicates_csv_filename.replace(".csv", "-sorted.csv")

    with open(sorted_csv_filename, "w") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in sortedlist:
            writer.writerow(row)

    os.remove(no_duplicates_csv_filename)
    subprocess.call(["php", "to_utf8_csv.php", sorted_csv_filename])
    os.remove(sorted_csv_filename)
    shutil.copyfile(
        sorted_csv_filename.replace(".csv", "-utf8.csv"), csv_output_filename
    )
    shutil.copyfile(
        sorted_csv_filename.replace(".csv", "-utf8.csv"),
        csv_output_filename.replace("-" + str(today), ""),
    )


# to call this script
# python3 get_department_cities_prices.py <department_name>
parser = argparse.ArgumentParser(
    description="Get the prices of the cities of a department of France in CSV"
)
parser.add_argument("department_name", help="department name")
parser.add_argument("price_type", choices=["buy", "rent"], help="buy or rent")

args = parser.parse_args()

if not args.department_name or not args.price_type:
    sys.exit()

department_name = args.department_name
price_type = args.price_type

today = datetime.date.today()
cities = []

with open("../data/communes-departement-region.csv", newline="") as csvfile:
    citiesreaders = csv.DictReader(csvfile)
    for row in citiesreaders:
        if row["nom_departement"] != department_name:
            continue

        cities.append(
            {"name": row["nom_commune_complet"], "zip_code": row["code_postal"]}
        )

path = Path("../prices/" + unidecode(department_name.lower().replace(" ", "-")))
path.mkdir(parents=True, exist_ok=True)

csv_output_filename = (
    "../prices/"
    + unidecode(department_name.lower().replace(" ", "-"))
    + "/prices-"
    + department_name.replace(" ", "-")
    + "-"
    + price_type
    + "-"
    + str(today)
    + ".csv"
)

fieldnames = ["city_name", "low_price", "medium_price", "high_price"]

with open(
    csv_output_filename,
    "w",
    newline="",
) as csvfile:
    cities_prices_writer = csv.writer(csvfile)
    cities_prices_writer.writerow(fieldnames)

driver = webdriver.Firefox()

try:
    for city in cities:
        city_name = city["name"]
        city_zip_code = city["zip_code"]

        driver.get("https://www.lacoteimmo.com/")

        if check_exists_by_xpath("//span[@class='didomi-continue-without-agreeing']"):
            popup_cookie_disable_link = driver.find_element_by_xpath(
                "//span[@class='didomi-continue-without-agreeing']"
            )
            popup_cookie_disable_link.click()

        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located(
                (By.XPATH, "//a[contains(text(), '" + department_name + "')]")
            )
        )

        department_link = driver.find_element_by_xpath(
            "//a[contains(text(), '" + department_name + "')]"
        )
        department_link.click()

        if price_type == "rent":
            rent_label = driver.find_element_by_xpath("//label[@class='location']")
            rent_label.click()

        search_input = driver.find_element_by_xpath(
            "//input[@placeholder='Adresse de votre bien']"
        )
        search_input.send_keys(city_name)

        WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//div[@class='slam-aui-results']//span[contains(@class, 'focus')]",
                )
            )
        )
        city_search_result = driver.find_element_by_xpath(
            "//div[@class='slam-aui-results']"
            + "//span["
            + "contains(@class, 'slam-aui-results-line')"
            + "and contains(text(), '"
            + city_zip_code
            + "')"
            + "]"
        )
        city_search_result.click()

        city_name_check = ""
        while unidecode(city_name_check) != unidecode(city_name):
            city_name_check = driver.execute_script(
                "return document.querySelector('.area-name').innerText;"
            )
            sleep(1)

        medium_price = driver.execute_script(
            "return document.querySelector('.med-price').innerText;"
        )
        medium_price = medium_price.replace("€", "").replace(" ", "")

        low_price = driver.execute_script(
            "return document.querySelector('.price .row:nth-child(3) span:nth-child(1)').innerText;"
        )
        low_price = (
            low_price.replace("Prix bas :", "").replace("€", "").replace(" ", "")
        )

        high_price = driver.execute_script(
            "return document.querySelector('.price .row:nth-child(3) span:nth-child(2)').innerText;"
        )
        high_price = (
            high_price.replace("Prix haut :", "").replace("€", "").replace(" ", "")
        )

        with open(
            csv_output_filename,
            "a",
            newline="",
        ) as csvfile:
            cities_prices_writer = csv.writer(csvfile)
            cities_prices_writer.writerow(
                [city_name, low_price, medium_price, high_price]
            )

finally:
    # driver.quit()
    normalize_CSV()
    print("end")
