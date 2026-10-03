from harness.base import HttpClient, idempotency_header
from harness.constants import constant_data, environment_data
from harness.endpoints import RewardsEndpoint, WalletEndpoint


class WalletClient(HttpClient):
    def __init__(self):
        super().__init__(environment_data["wallet_url"])

    def create_wallet(self, user_id, currency=constant_data["default_currency"]):
        return self.post(
            WalletEndpoint.create_wallet, json={"userId": user_id, "currency": currency}
        )

    def get_wallet(self, wallet_id):
        return self.get(WalletEndpoint.get_wallet.format(wallet_id=wallet_id))

    def credit(self, wallet_id, amount, idempotency_key=None):
        return self.post(
            WalletEndpoint.credit.format(wallet_id=wallet_id),
            json={"amount": amount},
            headers=idempotency_header(idempotency_key),
        )

    def debit(self, wallet_id, amount, idempotency_key=None):
        return self.post(
            WalletEndpoint.debit.format(wallet_id=wallet_id),
            json={"amount": amount},
            headers=idempotency_header(idempotency_key),
        )

    def transactions(self, wallet_id):
        return self.get(WalletEndpoint.transactions.format(wallet_id=wallet_id))

    # only the debit entries of the ledger, oldest first
    def debits(self, wallet_id):
        response = self.transactions(wallet_id)
        response.expect(200)
        debits = []
        for transaction in response.body["transactions"]:
            if transaction["type"] == "DEBIT":
                debits.append(transaction)
        return debits

    # test only, wipes all state of the wallet service, not just this test's
    def reset(self):
        return self.post(WalletEndpoint.reset)


class RewardsClient(HttpClient):
    def __init__(self):
        super().__init__(environment_data["rewards_url"])

    def get_reward(self, reward_id):
        return self.get(RewardsEndpoint.get_reward.format(reward_id=reward_id))

    def stock(self, reward_id):
        response = self.get_reward(reward_id)
        response.expect(200)
        return response.body["stock"]

    # same idempotency_key again replays the request
    def claim_reward(self, reward_id, *, user_id, wallet_id, idempotency_key=None):
        return self.post(
            RewardsEndpoint.claim_reward.format(reward_id=reward_id),
            json={"userId": user_id, "walletId": wallet_id},
            headers=idempotency_header(idempotency_key),
        )

    def get_claim(self, claim_id):
        return self.get(RewardsEndpoint.get_claim.format(claim_id=claim_id))

    def user_claims(self, user_id):
        return self.get(RewardsEndpoint.user_claims.format(user_id=user_id))

    # claim ids of the user, optionally only those with this status
    def claim_ids(self, user_id, status=None):
        response = self.user_claims(user_id)
        response.expect(200)
        ids = []
        for claim in response.body["claims"]:
            if status is None or claim["status"] == status:
                ids.append(claim["claimId"])
        return ids

    # test only, wipes all state of the rewards service, not just this test's
    def reset(self):
        return self.post(RewardsEndpoint.reset)
