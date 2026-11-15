# test_urban_scooter.py
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

ORDER_URL = "https://cnt-99d06294-7826-4309-89ed-9e395e730435.containerhub.tripleten-services.com/order"


@pytest.fixture(scope="class")
def driver():
    """Initializes Chrome locked to 1280x720 desktop viewport."""
    options = webdriver.ChromeOptions()
    options.add_argument("--window-size=1280,720")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_window_size(1280, 720)
    driver.get(ORDER_URL)
    yield driver
    driver.quit()


class TestAboutCustomerValidation:

    # Locators
    FIRST_NAME_INPUT = (By.XPATH, "//input[contains(@placeholder, 'First name')]")
    LAST_NAME_INPUT = (By.XPATH, "//input[contains(@placeholder, 'Last name')]")
    ADDRESS_INPUT = (By.XPATH, "//input[contains(@placeholder, 'Address')]")
    STATION_INPUT = (By.XPATH, "//input[contains(@placeholder, 'Subway')]")
    STATION_FIRST_OPTION = (By.XPATH, "//div[contains(@class, 'select-search')]//li//button")
    PHONE_INPUT = (By.XPATH, "//input[contains(@placeholder, 'Phone')]")
    NEXT_BUTTON = (By.XPATH, "//button[contains(text(), 'Next')]")
    RENTING_HEADER = (By.XPATH, "//*[contains(text(), 'Renting')]")

    def clear_and_type(self, driver, locator, text):
        wait = WebDriverWait(driver, 5)
        element = wait.until(EC.element_to_be_clickable(locator))
        element.send_keys(Keys.CONTROL + "a")
        element.send_keys(Keys.BACKSPACE)
        if text:
            element.send_keys(text)
        return element

    def click_next(self, driver):
        """Removes cookie consent overlay and performs DOM click."""
        driver.execute_script("document.querySelectorAll('.App_CookieConsent__1yUIN').forEach(e => e.remove());")
        next_btn = driver.find_element(*self.NEXT_BUTTON)
        driver.execute_script("arguments[0].click();", next_btn)

    def select_first_station(self, driver):
        station_field = driver.find_element(*self.STATION_INPUT)
        station_field.click()
        wait = WebDriverWait(driver, 5)
        first_option = wait.until(EC.element_to_be_clickable(self.STATION_FIRST_OPTION))
        first_option.click()
        return station_field

    def has_field_error(self, driver, input_locator):
        """Evaluates whether the specific field container shows an error state."""
        field = driver.find_element(*input_locator)
        field_class = (field.get_attribute("class") or "").lower()
        if "error" in field_class:
            return True

        # Check for visible error message container inside the parent container
        parent = field.find_element(By.XPATH, "./..")
        error_msgs = parent.find_elements(By.XPATH, ".//*[contains(@class, 'ErrorMessage') or contains(@class, 'error')]")
        return any(msg.is_displayed() and msg.text.strip() != "" for msg in error_msgs)

    # ==========================================
    # 1. FIRST NAME VALIDATIONS (TC-01 - TC-10)
    # ==========================================
    @pytest.mark.parametrize("test_id, input_data, is_valid", [
        ("TC-01", "John", True),
        ("TC-02", "Jean-Luc", True),
        ("TC-03", "Ed", True),
        ("TC-04", "Alexander-James", True),
        ("TC-05", "J", False),
        ("TC-06", "Alexander-JamesX", False),
        ("TC-07", "John2", False),
        ("TC-08", "John@#$", False),
        ("TC-09", "Иван", False),
        ("TC-10", "", False),
    ])
    def test_first_name_field(self, driver, test_id, input_data, is_valid):
        self.clear_and_type(driver, self.FIRST_NAME_INPUT, input_data)
        self.click_next(driver)
        has_error = self.has_field_error(driver, self.FIRST_NAME_INPUT)

        if is_valid:
            assert not has_error, f"[{test_id}] Valid input '{input_data}' triggered unexpected error."
        else:
            assert has_error, f"[{test_id}] Invalid input '{input_data}' failed to trigger field error."

    # ==========================================
    # 2. LAST NAME VALIDATIONS (TC-11 - TC-20)
    # ==========================================
    @pytest.mark.parametrize("test_id, input_data, is_valid", [
        ("TC-11", "Smith", True),
        ("TC-12", "Smith-Jones", True),
        ("TC-13", "Li", True),
        ("TC-14", "Smith-Westbrook", True),
        ("TC-15", "K", False),
        ("TC-16", "Smith-Westbrook1", False),
        ("TC-17", "Smith123", False),
        ("TC-18", "O'Connor", False),
        ("TC-19", "Петров", False),
        ("TC-20", "", False),
    ])
    def test_last_name_field(self, driver, test_id, input_data, is_valid):
        self.clear_and_type(driver, self.LAST_NAME_INPUT, input_data)
        self.click_next(driver)
        has_error = self.has_field_error(driver, self.LAST_NAME_INPUT)

        if is_valid:
            assert not has_error, f"[{test_id}] Valid input '{input_data}' triggered unexpected error."
        else:
            assert has_error, f"[{test_id}] Invalid input '{input_data}' failed to trigger field error."

    # ==========================================
    # 3. ADDRESS VALIDATIONS (TC-21 - TC-29)
    # ==========================================
    @pytest.mark.parametrize("test_id, input_data, is_valid", [
        ("TC-21", "17th North Avenue, 46", True),
        ("TC-22", "St. 1", True),
        ("TC-23", "1234 Long Industrial Boulevard Parkway Suite 5678", True),
        ("TC-24", "St 1", False),
        ("TC-25", "1234 Long Industrial Boulevard Parkway Suite 567891", False),
        ("TC-27", "123 Main St #4B", False),
        ("TC-28", "ул. Ленина, д. 10", False),
        ("TC-29", "", False),
    ])
    def test_address_field(self, driver, test_id, input_data, is_valid):
        self.clear_and_type(driver, self.ADDRESS_INPUT, input_data)
        self.click_next(driver)
        has_error = self.has_field_error(driver, self.ADDRESS_INPUT)

        if is_valid:
            assert not has_error, f"[{test_id}] Valid input '{input_data}' triggered unexpected error."
        else:
            assert has_error, f"[{test_id}] Invalid input '{input_data}' failed to trigger field error."

    def test_address_auto_trim(self, driver):
        """TC-26: Verify leading and trailing spaces are removed upon blur."""
        raw_address = "   17th North Avenue, 46   "
        field = self.clear_and_type(driver, self.ADDRESS_INPUT, raw_address)
        driver.find_element(*self.FIRST_NAME_INPUT).click()

        current_val = field.get_attribute("value")
        assert current_val == "17th North Avenue, 46", f"[TC-26] Address not trimmed: '{current_val}'"

    # ==========================================
    # 4. SUBWAY STATION VALIDATIONS (TC-30 - TC-31)
    # ==========================================
    def test_subway_station_selection(self, driver):
        """TC-30: Open dropdown and select first available station."""
        station_field = self.select_first_station(driver)
        assert station_field.get_attribute("value") != "", "[TC-30] Station selection did not populate field."

    # ==========================================
    # 5. PHONE VALIDATIONS (TC-32 - TC-40)
    # ==========================================
    @pytest.mark.parametrize("test_id, input_data, is_valid", [
        ("TC-32", "+11111111111", True),
        ("TC-33", "+120255501", True),
        ("TC-34", "+12025550193", True),
        ("TC-35", "11111111111", False),
        ("TC-36", "+12025550", False),
        ("TC-37", "+120255501934", False),
        ("TC-38", "+1800FLOWERS", False),
        ("TC-39", "+1 202 555-01", False),
        ("TC-40", "", False),
    ])
    def test_phone_field(self, driver, test_id, input_data, is_valid):
        self.clear_and_type(driver, self.PHONE_INPUT, input_data)
        self.click_next(driver)
        has_error = self.has_field_error(driver, self.PHONE_INPUT)

        if is_valid:
            assert not has_error, f"[{test_id}] Valid input '{input_data}' triggered unexpected error."
        else:
            assert has_error, f"[{test_id}] Invalid input '{input_data}' failed to trigger field error."

    # ==========================================
    # 6. NAVIGATION TRANSITIONS (TC-41 - TC-42)
    # ==========================================
    def test_next_button_blocked_on_empty(self, driver):
        """TC-42: Ensure form does not advance when required fields are missing."""
        driver.get(ORDER_URL)
        self.click_next(driver)

        renting_headers = driver.find_elements(*self.RENTING_HEADER)
        assert len(renting_headers) == 0 or not renting_headers[0].is_displayed(), \
            "[TC-42] Form navigated to Renting screen despite blank required fields."

    def test_next_button_advances_on_valid(self, driver):
        """TC-41: Ensure form transitions to Renting stage when valid."""
        driver.get(ORDER_URL)
        self.clear_and_type(driver, self.FIRST_NAME_INPUT, "John")
        self.clear_and_type(driver, self.LAST_NAME_INPUT, "Smith")
        self.clear_and_type(driver, self.ADDRESS_INPUT, "17th North Avenue, 46")

        self.select_first_station(driver)

        self.clear_and_type(driver, self.PHONE_INPUT, "+11111111111")
        self.click_next(driver)

        wait = WebDriverWait(driver, 5)
        renting_header = wait.until(EC.visibility_of_element_located(self.RENTING_HEADER))
        assert renting_header.is_displayed(), "[TC-41] Form failed to navigate to 'Renting' screen."
