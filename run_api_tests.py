import random
import string
import time
import requests

BASE_URL = "https://cnt-1d14c11d-d487-41ef-b6fb-618c8b03a449.containerhub.tripleten-services.com"
COURIER_URL = f"{BASE_URL}/api/v1/courier"
LOGIN_URL = f"{BASE_URL}/api/v1/courier/login"
TIMEOUT = 10


def generate_random_string(length=10):
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for _ in range(length))


def generate_courier_payload(include_first_name=True):
    payload = {
        "login": f"qa_courier_{int(time.time())}_{generate_random_string(5)}",
        "password": generate_random_string(12),
    }
    if include_first_name:
        payload["firstName"] = generate_random_string(8).capitalize()
    return payload


def login_and_get_id(login, password):
    response = requests.post(
        LOGIN_URL,
        json={"login": login, "password": password},
        timeout=TIMEOUT,
    )
    if response.status_code == 200:
        return response.json().get("id")
    return None


def cleanup_courier(courier_id):
    if courier_id:
        requests.delete(f"{COURIER_URL}/{courier_id}", timeout=TIMEOUT)


def record_result(results, tc_id, description, method, endpoint, expected_status, response=None, error=None, extra_check=True):
    if error:
        results.append({
            "tc_id": tc_id,
            "description": description,
            "method": method,
            "endpoint": endpoint,
            "expected": expected_status,
            "actual": "ERR/TIMEOUT",
            "status": "FAIL",
            "body": str(error),
        })
        return

    passed = (response.status_code == expected_status) and extra_check
    results.append({
        "tc_id": tc_id,
        "description": description,
        "method": method,
        "endpoint": endpoint,
        "expected": expected_status,
        "actual": response.status_code,
        "status": "PASS" if passed else "FAIL",
        "body": response.text,
    })


def run_all_tests():
    results = []
    created_ids = []

    # ---------------------------------------------------------
    # 1. POST /api/v1/courier (Create Courier)
    # ---------------------------------------------------------

    # TC-01: Create courier with all valid fields
    valid_courier = generate_courier_payload(include_first_name=True)
    r = requests.post(COURIER_URL, json=valid_courier, timeout=TIMEOUT)
    ok_flag = r.status_code == 201 and r.json().get("ok") is True
    record_result(results, "TC-01", "Create courier with all valid fields", "POST", "/api/v1/courier", 201, r, extra_check=ok_flag)

    courier_id = login_and_get_id(valid_courier["login"], valid_courier["password"])
    if courier_id:
        created_ids.append(courier_id)

    # TC-02: Create courier with required fields only (omit firstName)
    required_only = generate_courier_payload(include_first_name=False)
    r = requests.post(COURIER_URL, json=required_only, timeout=TIMEOUT)
    ok_flag = r.status_code == 201 and r.json().get("ok") is True
    record_result(results, "TC-02", "Create courier without optional firstName", "POST", "/api/v1/courier", 201, r, extra_check=ok_flag)

    req_only_id = login_and_get_id(required_only["login"], required_only["password"])
    if req_only_id:
        created_ids.append(req_only_id)

    # TC-03: Create duplicate courier (same login)
    duplicate_payload = {
        "login": valid_courier["login"],
        "password": "AnotherPassword123",
        "firstName": "Duplicate",
    }
    r = requests.post(COURIER_URL, json=duplicate_payload, timeout=TIMEOUT)
    record_result(results, "TC-03", "Create courier with duplicate login", "POST", "/api/v1/courier", 409, r)

    # TC-04: Create courier missing login
    r = requests.post(COURIER_URL, json={"password": "Password123", "firstName": "NoLogin"}, timeout=TIMEOUT)
    record_result(results, "TC-04", "Create courier missing login field", "POST", "/api/v1/courier", 400, r)

    # TC-05: Create courier missing password
    r = requests.post(COURIER_URL, json={"login": f"nologin_{generate_random_string(6)}", "firstName": "NoPass"}, timeout=TIMEOUT)
    record_result(results, "TC-05", "Create courier missing password field", "POST", "/api/v1/courier", 400, r)

    # TC-06: Create courier with empty JSON body
    r = requests.post(COURIER_URL, json={}, timeout=TIMEOUT)
    record_result(results, "TC-06", "Create courier with empty body {}", "POST", "/api/v1/courier", 400, r)

    # TC-07: Create courier with empty strings
    r = requests.post(COURIER_URL, json={"login": "", "password": "", "firstName": ""}, timeout=TIMEOUT)
    record_result(results, "TC-07", "Create courier with empty string values", "POST", "/api/v1/courier", 400, r)

    # ---------------------------------------------------------
    # 2. POST /api/v1/courier/login (Courier Login)
    # ---------------------------------------------------------

    # TC-08: Login with valid credentials
    r = requests.post(LOGIN_URL, json={"login": valid_courier["login"], "password": valid_courier["password"]}, timeout=TIMEOUT)
    has_id = r.status_code == 200 and isinstance(r.json().get("id"), int)
    record_result(results, "TC-08", "Login with valid credentials", "POST", "/api/v1/courier/login", 200, r, extra_check=has_id)

    # TC-09: Login with wrong password
    r = requests.post(LOGIN_URL, json={"login": valid_courier["login"], "password": "WrongPassword999"}, timeout=TIMEOUT)
    record_result(results, "TC-09", "Login with incorrect password", "POST", "/api/v1/courier/login", 404, r)

    # TC-10: Login with non-existent login
    r = requests.post(LOGIN_URL, json={"login": f"ghost_{generate_random_string(8)}", "password": "Password123"}, timeout=TIMEOUT)
    record_result(results, "TC-10", "Login with non-existent username", "POST", "/api/v1/courier/login", 404, r)

    # TC-11: Login missing password
    try:
        r = requests.post(LOGIN_URL, json={"login": valid_courier["login"]}, timeout=TIMEOUT)
        record_result(results, "TC-11", "Login missing password field", "POST", "/api/v1/courier/login", 400, r)
    except requests.exceptions.RequestException as exc:
        record_result(results, "TC-11", "Login missing password field", "POST", "/api/v1/courier/login", 400, error=exc)

    # TC-12: Login missing login
    try:
        r = requests.post(LOGIN_URL, json={"password": valid_courier["password"]}, timeout=TIMEOUT)
        record_result(results, "TC-12", "Login missing login field", "POST", "/api/v1/courier/login", 400, r)
    except requests.exceptions.RequestException as exc:
        record_result(results, "TC-12", "Login missing login field", "POST", "/api/v1/courier/login", 400, error=exc)

    # ---------------------------------------------------------
    # 3. DELETE /api/v1/courier/:id (Delete Courier)
    # ---------------------------------------------------------

    # TC-13: Delete existing courier with valid ID
    if courier_id:
        r = requests.delete(f"{COURIER_URL}/{courier_id}", timeout=TIMEOUT)
        ok_flag = r.status_code == 200 and r.json().get("ok") is True
        record_result(results, "TC-13", "Delete existing courier by valid ID", "DELETE", f"/api/v1/courier/{courier_id}", 200, r, extra_check=ok_flag)
        if ok_flag and courier_id in created_ids:
            created_ids.remove(courier_id)

        # TC-14: Verify deleted courier can no longer log in
        r = requests.post(LOGIN_URL, json={"login": valid_courier["login"], "password": valid_courier["password"]}, timeout=TIMEOUT)
        record_result(results, "TC-14", "Verify deleted courier cannot log in", "POST", "/api/v1/courier/login", 404, r)

    # TC-15: Delete courier with non-existent ID
    r = requests.delete(f"{COURIER_URL}/999999999", timeout=TIMEOUT)
    record_result(results, "TC-15", "Delete courier with non-existent ID", "DELETE", "/api/v1/courier/999999999", 404, r)

    # TC-16: Delete courier without ID in path
    r = requests.delete(f"{COURIER_URL}/", timeout=TIMEOUT)
    record_result(results, "TC-16", "Delete courier without ID parameter", "DELETE", "/api/v1/courier/", 400, r)

    # Cleanup any remaining test accounts
    for leftover_id in created_ids:
        cleanup_courier(leftover_id)

    # ---------------------------------------------------------
    # Print Test Execution Report
    # ---------------------------------------------------------
    print("\n" + "=" * 105)
    print(f"URBAN SCOOTER API TEST RESULTS | SERVER: {BASE_URL}")
    print("=" * 105)
    print(f"{'ID':<7} | {'STATUS':<6} | {'EXP':<4} | {'ACT':<11} | {'TEST CASE':<42} | RESPONSE BODY")
    print("-" * 105)

    passed_count = 0
    for item in results:
        if item["status"] == "PASS":
            passed_count += 1
        print(
            f"{item['tc_id']:<7} | {item['status']:<6} | {str(item['expected']):<4} | "
            f"{str(item['actual']):<11} | {item['description']:<42} | {item['body']}"
        )

    print("=" * 105)
    print(f"TOTAL: {len(results)} | PASSED: {passed_count} | FAILED: {len(results) - passed_count}")
    print("=" * 105 + "\n")


if __name__ == "__main__":
    run_all_tests()