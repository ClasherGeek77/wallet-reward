import os

# dynamic, changes between runs or environments
environment_data = {
    "wallet_url": os.environ.get("WALLET_URL", "http://127.0.0.1:8081"),
    "rewards_url": os.environ.get("REWARDS_URL", "http://127.0.0.1:8082"),
    "timeout": int(os.environ.get("API_TIMEOUT", "10")),  # seconds per request
    "reset_services": os.environ.get("RESET_SERVICES", "1") == "1",
}

# static, never changes between runs or environments
constant_data = {
    "default_currency": "IDR",
    "coffee_id": "rw-coffee",
    "coffee_cost": 25000,
    "balance_enough_for_coffee": 100000,
    "balance_too_low_for_coffee": 10000,
}
