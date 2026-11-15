import requests

BASE_URL = "https://cnt-f1f08941-3da3-4b1b-9bd9-5798f1c40467.containerhub.tripleten-services.com"

# 1. Create Courier
r_courier = requests.post(f"{BASE_URL}/api/v1/courier", json={
    "login": "gregtest",
    "password": "1234",
    "firstName": "Greg"
})
print("Courier:", r_courier.status_code, r_courier.text)

# 2. Create Today's Order
r_order = requests.post(f"{BASE_URL}/api/v1/orders", json={
    "firstName": "Alex",
    "lastName": "Mercer",
    "address": "State St 1214",
    "metroStation": 4,
    "phone": "+18005553535",
    "rentTime": 3,
    "deliveryDate": "2026-11-12",
    "comment": "Mobile test order",
    "color": ["BLACK"]
})
print("Order:", r_order.status_code, r_order.text)