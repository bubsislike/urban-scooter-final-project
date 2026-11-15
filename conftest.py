import os
import re
import pytest

SCREENSHOTS_DIR = "screenshots"


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Hooks into Pytest to automatically capture and save 1280x720 screenshots on assertion failure."""
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        driver = item.funcargs.get("driver")
        if driver:
            os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
            raw_name = item.nodeid.split("::")[-1]
            clean_name = re.sub(r'[\\/*?:"<>|]', "_", raw_name)
            file_path = os.path.join(SCREENSHOTS_DIR, f"FAIL_{clean_name}.png")
            driver.save_screenshot(file_path)
            print(f"\n[DEFECT CAPTURED] Screenshot saved: {file_path}")