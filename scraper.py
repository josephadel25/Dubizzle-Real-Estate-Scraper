import os
import csv
import time
from random import uniform
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def scrape_realstate(number):
    apartment_number = number
    output_file = f"dubizzle_realstate_{number}.csv"

    options = uc.ChromeOptions()
    user_data_dir = os.path.abspath("profile")
    options.add_argument(f"--user-data-dir={user_data_dir}")
    options.add_argument("--disable-popup-blocking")
    driver = uc.Chrome(options=options)
    wait = WebDriverWait(driver, 15)

    with open(output_file, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["Title", "Price", "Location", "Bedrooms", "Bathrooms", "Area", "Property Type", "Furnished"])

    try:
        driver.get("https://www.dubizzle.com.eg/en/properties/apartments-duplex-for-sale")
        time.sleep(5)

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        results = []
        seen_links = set()

        while apartment_number > 0:
            wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "a")))
            links = driver.find_elements(By.TAG_NAME, "a")

            current_page_links = []
            for a in links:
                href = a.get_attribute("href")
                if href and "/en/ad/" in href and href not in seen_links:
                    seen_links.add(href)
                    current_page_links.append(href)

            print(f"Found {len(current_page_links)} new apartment links on this page")

            # Visit each link in a new tab
            for link in current_page_links:
                if apartment_number <= 0:
                    break

                try:
                    driver.execute_script(f"window.open('{link}', '_blank');")
                    time.sleep(1)
                    driver.switch_to.window(driver.window_handles[-1])

                    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '[aria-label="Wallpaper Ad Body"]')))
                    print(f"Scraping: {link}")

                    element = driver.find_element(By.CSS_SELECTOR, '[aria-label="Wallpaper Ad Body"]')
                    title = element.find_element(By.CLASS_NAME, '_75bce902').text
                    price = element.find_element(By.CSS_SELECTOR, '[aria-label="Price"]').text
                    location = element.find_element(By.CSS_SELECTOR, '[aria-label="Location"]').text
                    details = element.find_element(By.CSS_SELECTOR, '[aria-label="Highlighted Details"]').text.split()
                    property_type = 'N/A' if 'Type' not in details else details[details.index('Type') + 1]
                    area = 'N/A' if 'Area' not in details else details[details.index('Area') + 2]
                    bedrooms = 'N/A' if 'Bedrooms' not in details else details[details.index('Bedrooms') + 1]
                    bathrooms = 'N/A' if 'Bathrooms' not in details else details[details.index('Bathrooms') + 1]
                    furnished = 'N/A' if 'Furnished' not in details else details[details.index('Furnished') + 1]

                    results.append([title, price, location, bedrooms, bathrooms, area, property_type, furnished])
                    apartment_number -= 1

                except Exception as e:
                    print(f"Error scraping {link}: {e}")

                finally:
                    if len(driver.window_handles) > 1:
                        driver.close()
                        driver.switch_to.window(driver.window_handles[0])
                    time.sleep(1)

            with open(output_file, "a", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                writer.writerows(results)
                results = []

            try:
                next_button = driver.find_element(By.XPATH, '//li/a[div[@title="Next"]]')
                next_href = next_button.get_attribute("href")
                if not next_href:
                    print("No next page link found.")
                    break

                print("➡️ Moving to next page...")
                driver.get(next_href)
                time.sleep(uniform(3, 5))

            except Exception as e:
                print("No more pages or error during next button navigation:", e)
                break

    finally:
        print("Scraping completed.")
        driver.quit()

    return output_file