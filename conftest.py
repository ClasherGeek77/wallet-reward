import logging

import pytest  # ty: ignore[unresolved-import]

from harness.assertion import Assertion
from harness.utils import create_funded_wallet, new_idempotency_key, unique_user_id
from harness.clients import RewardsClient, WalletClient
from harness.constants import constant_data, environment_data

logger = logging.getLogger(__name__)


class ApiClient:
    def __init__(self):
        self.wallet_client = WalletClient()
        self.rewards_client = RewardsClient()


class TestData:
    def __init__(self, api):
        self.api = api
        self.user_id = unique_user_id()
        self.coffee_id = constant_data["coffee_id"]
        self.coffee_cost = constant_data["coffee_cost"]
        self.enough_balance = constant_data["balance_enough_for_coffee"]
        self.low_balance = constant_data["balance_too_low_for_coffee"]

    # fresh key each call, reuse one to replay a request
    def new_idempotency_key(self):
        return new_idempotency_key()

    # wallet for this test's user holding amount, returns the walletId
    def create_funded_wallet(self, amount):
        return create_funded_wallet(self.api.wallet_client, self.user_id, amount)


def reset_both_services():
    api = ApiClient()
    api.wallet_client.reset().expect(204)
    api.rewards_client.reset().expect(204)


# runs once before the first test and once after the last test
@pytest.fixture(autouse=True, scope="session")
def setup_session():
    if environment_data["reset_services"]:
        logger.info("setting up, resetting both services before the first test")
        reset_both_services()

    yield

    if environment_data["reset_services"]:
        logger.info("tearing down, resetting both services after the last test")
        reset_both_services()


@pytest.fixture
def api():
    return ApiClient()


@pytest.fixture
def testdata(api):
    return TestData(api)


@pytest.fixture
def assertion():
    return Assertion()


@pytest.fixture(name="logger")
def step_logger():
    return logging.getLogger("test")
