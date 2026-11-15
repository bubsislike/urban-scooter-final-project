# Urban Scooter — Full-Stack QA Automation Suite

Automated Web UI, mobile environment, and REST API test suites for the **Urban Scooter** delivery application, built in Python to validate order form validation rules, Android emulator configuration, and courier API endpoints.

## Tech Stack
* **Language:** Python 3.13
* **Web UI Automation:** Selenium WebDriver, Pytest (parametrized tests, fixtures), webdriver-manager
* **API Automation:** Python requests
* **Mobile Environment:** Android Studio Emulator / ADB
* **Defect Tracking:** Jira

## Repository Structure
* `conftest.py` — Pytest configuration and shared fixture setup for browser test execution.
* `test_urban_scooter.py` — 42 automated Web UI tests (`TC-01`–`TC-42`) covering boundary value analysis, field validation (First Name, Last Name, Address auto-trim, Subway Station dropdown, Phone format), and multi-step navigation on the `/order` workflow.
* `task2_mobile_setup.py` — Automated environment and device configuration script for Android mobile testing.
* `run_api_tests.py` — 16-case REST API test runner (`TC-01`–`TC-16`) validating `POST /api/v1/courier`, `POST /api/v1/courier/login`, and `DELETE /api/v1/courier/:id` across positive, boundary, and negative scenarios.
* `requirements.txt` — Python package dependencies.

## Setup & Execution

1. **Clone the repository and create a virtual environment:**

        git clone https://github.com/bubsislike/urban-scooter-final-project.git
        cd urban-scooter-final-project
        python -m venv .venv

2. **Activate the virtual environment and install dependencies:**

        .\.venv\Scripts\Activate.ps1
        pip install -r requirements.txt

3. **Run the test suites:**

        pytest test_urban_scooter.py -v
        python run_api_tests.py

## Key Defects Uncovered by API Automation
Running `run_api_tests.py` (14 passed, 2 failed) isolated two backend validation defects logged in Jira:
1. **`POST /api/v1/courier/login` Server Hang (`TC-11`):** Omitting the mandatory `password` field causes the server to hang until client timeout instead of returning `400 Bad Request` (`{"code": 400, "message": "Not enough data to log in."}`).
2. **`DELETE /api/v1/courier/` Missing ID Status Mismatch (`TC-16`):** Sending a `DELETE` request without a courier `:id` path parameter returns `404 Not Found` instead of `400 Bad Request` (`{"code": 400, "message": "Not enough data to delete a courier."}`).
