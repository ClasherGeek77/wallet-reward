import logging
import time

logger = logging.getLogger(__name__)

# last number handed out, so two ids made in the same millisecond still differ
last_number = {"value": 0}


# the timestamp keeps runs apart, the counter keeps ids apart inside a run
def unique_number():
    last_number["value"] = last_number["value"] + 1
    number = last_number["value"]
    timestamp = int(time.time() * 1000)
    return f"{timestamp}-{number}"


# api needs a string id
def unique_user_id():
    return "autotest-" + unique_number()


def new_idempotency_key():
    return "idem-" + unique_number()


# each step checks its status, so a bad setup fails here and not inside the test
def create_funded_wallet(wallet_client, user_id, amount):
    logger.info(f"setting up a wallet for {user_id} with {amount}")
    created = wallet_client.create_wallet(user_id)
    created.expect(201)
    wallet_id = created.body["walletId"]
    if amount > 0:
        wallet_client.credit(wallet_id, amount).expect(200)
    return wallet_id
