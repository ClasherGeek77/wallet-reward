# endpoint names match the client method that uses them
class WalletEndpoint:
    # reset is the same path on both services, kept in each on purpose
    reset = "/admin/reset"
    create_wallet = "/wallets"
    get_wallet = "/wallets/{wallet_id}"
    credit = "/wallets/{wallet_id}/credit"
    debit = "/wallets/{wallet_id}/debit"
    transactions = "/wallets/{wallet_id}/transactions"


class RewardsEndpoint:
    # same path as the wallet service, duplicated on purpose
    reset = "/admin/reset"
    get_reward = "/rewards/{reward_id}"
    claim_reward = "/rewards/{reward_id}/claims"
    get_claim = "/claims/{claim_id}"
    user_claims = "/users/{user_id}/claims"
