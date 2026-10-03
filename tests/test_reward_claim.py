def test_claiming_affordable_reward_debits_wallet_and_fulfils_claim(
    testdata,
    api,
    assertion,
    logger,
):
    wallet_id = testdata.create_funded_wallet(testdata.enough_balance)

    stock_before = api.rewards_client.stock(testdata.coffee_id)

    wallet_response = api.wallet_client.get_wallet(wallet_id)
    version_before = wallet_response.expect(200).body["version"]

    claim_response = api.rewards_client.claim_reward(
        testdata.coffee_id,
        user_id=testdata.user_id,
        wallet_id=wallet_id,
    )
    claim = claim_response.expect(201).body
    assertion.assert_equal(
        actual_result=claim["status"],
        expected_result="FULFILLED",
        what_proven="the customer gets the reward when the wallet can pay for it",
        label="claim status",
    )
    assertion.assert_equal(
        actual_result=claim["debitedAmount"],
        expected_result=testdata.coffee_cost,
        what_proven="the claim records the price the customer was charged",
        label="claim debitedAmount",
    )

    logger.warning("checking rewards service: claim stored and listed, one stock used")
    stored_response = api.rewards_client.get_claim(claim["claimId"])
    stored_claim = stored_response.expect(200).body
    assertion.assert_equal(
        actual_result=stored_claim["status"],
        expected_result="FULFILLED",
        what_proven="the rewards service keeps the claim as fulfilled",
        label="stored claim status",
    )

    user_claim_ids = api.rewards_client.claim_ids(testdata.user_id)
    assertion.assert_equal(
        actual_result=user_claim_ids,
        expected_result=[claim["claimId"]],
        what_proven="the claim is listed in the customer's claims",
        label="user claims",
    )

    stock_after = api.rewards_client.stock(testdata.coffee_id)
    assertion.assert_equal(
        actual_result=stock_after,
        expected_result=stock_before - 1,
        what_proven="one unit of stock is used for the claim",
        label="reward stock",
    )

    logger.warning(
        "checking wallet service: balance dropped, ledger links to the claim"
    )
    wallet_response = api.wallet_client.get_wallet(wallet_id)
    wallet_after = wallet_response.expect(200).body
    assertion.assert_equal(
        actual_result=wallet_after["balance"],
        expected_result=testdata.enough_balance - testdata.coffee_cost,
        what_proven="the wallet is charged the reward price",
        label="wallet balance",
    )
    assertion.assert_equal(
        actual_result=wallet_after["version"],
        expected_result=version_before + 1,
        what_proven="the wallet changed exactly once",
        label="wallet version",
    )

    debits = api.wallet_client.debits(wallet_id)
    assertion.assert_length(
        actual_array=debits,
        expected_length=1,
        what_proven="the customer is charged one time only",
        label="wallet debits",
    )
    debit = debits[0]
    assertion.assert_equal(
        actual_result=debit["transactionId"],
        expected_result=claim["walletTransactionId"],
        what_proven="the wallet ledger entry belongs to this claim",
        label="debit transaction id",
    )
    assertion.assert_equal(
        actual_result=debit["amount"],
        expected_result=testdata.coffee_cost,
        what_proven="the ledger shows the reward price as the charge",
        label="debit amount",
    )
    assertion.assert_equal(
        actual_result=debit["reference"],
        expected_result=f"claim:{claim['claimId']}",
        what_proven="the ledger entry can be traced back to the claim",
        label="debit reference",
    )


def test_claim_with_insufficient_balance_is_rejected_and_wallet_untouched(
    testdata,
    api,
    assertion,
    logger,
):
    wallet_id = testdata.create_funded_wallet(testdata.low_balance)

    stock_before = api.rewards_client.stock(testdata.coffee_id)

    wallet_response = api.wallet_client.get_wallet(wallet_id)
    version_before = wallet_response.expect(200).body["version"]

    claim_response = api.rewards_client.claim_reward(
        testdata.coffee_id,
        user_id=testdata.user_id,
        wallet_id=wallet_id,
    )
    error = claim_response.expect_error(
        409,
        "INSUFFICIENT_BALANCE",
        what_proven="the claim is refused because the balance is too low",
    )
    assertion.assert_equal(
        actual_result=error["cost"],
        expected_result=testdata.coffee_cost,
        what_proven="the customer is told the reward price",
        label="error cost",
    )

    logger.warning("checking rewards service: claim rejected, nothing consumed")
    rejected_response = api.rewards_client.get_claim(error["claimId"])
    rejected_claim = rejected_response.expect(200).body
    assertion.assert_equal(
        actual_result=rejected_claim["status"],
        expected_result="REJECTED",
        what_proven="the refused claim is recorded as rejected",
        label="claim status",
    )
    assertion.assert_equal(
        actual_result=rejected_claim["rejectionReason"],
        expected_result="INSUFFICIENT_BALANCE",
        what_proven="the rejection reason says the balance was too low",
        label="rejection reason",
    )
    assertion.assert_equal(
        actual_result=rejected_claim["debitedAmount"],
        expected_result=0,
        what_proven="a rejected claim charges nothing",
        label="claim debitedAmount",
    )
    assertion.assert_is_none(
        actual_result=rejected_claim["walletTransactionId"],
        what_proven="a rejected claim has no wallet transaction",
        label="claim walletTransactionId",
    )

    fulfilled_ids = api.rewards_client.claim_ids(
        testdata.user_id,
        status="FULFILLED",
    )
    assertion.assert_length(
        actual_array=fulfilled_ids,
        expected_length=0,
        what_proven="the customer has no fulfilled claim after a rejection",
        label="fulfilled claims",
    )

    stock_after = api.rewards_client.stock(testdata.coffee_id)
    assertion.assert_equal(
        actual_result=stock_after,
        expected_result=stock_before,
        what_proven="a rejected claim does not use stock",
        label="reward stock",
    )

    logger.warning("checking wallet service: balance, version and ledger untouched")
    wallet_response = api.wallet_client.get_wallet(wallet_id)
    wallet_after = wallet_response.expect(200).body
    assertion.assert_equal(
        actual_result=wallet_after["balance"],
        expected_result=testdata.low_balance,
        what_proven="the wallet balance is untouched",
        label="wallet balance",
    )
    assertion.assert_equal(
        actual_result=wallet_after["version"],
        expected_result=version_before,
        what_proven="the wallet was not changed at all",
        label="wallet version",
    )

    debits = api.wallet_client.debits(wallet_id)
    assertion.assert_length(
        actual_array=debits,
        expected_length=0,
        what_proven="no debit is recorded in the ledger",
        label="wallet debits",
    )


def test_replayed_claim_request_charges_wallet_only_once(
    testdata,
    api,
    assertion,
    logger,
):
    wallet_id = testdata.create_funded_wallet(testdata.enough_balance)

    stock_before = api.rewards_client.stock(testdata.coffee_id)

    idempotency_key = testdata.new_idempotency_key()

    first_response = api.rewards_client.claim_reward(
        testdata.coffee_id,
        user_id=testdata.user_id,
        wallet_id=wallet_id,
        idempotency_key=idempotency_key,
    )
    claim_id = first_response.expect(201).body["claimId"]

    replay_response = api.rewards_client.claim_reward(
        testdata.coffee_id,
        user_id=testdata.user_id,
        wallet_id=wallet_id,
        idempotency_key=idempotency_key,
    )
    replay_claim_id = replay_response.expect(201).body["claimId"]
    assertion.assert_equal(
        actual_result=replay_claim_id,
        expected_result=claim_id,
        what_proven="the same request sent again returns the same claim",
        label="replayed claimId",
    )

    logger.warning("sending the same key with another payload, must be refused")
    mismatch_response = api.rewards_client.claim_reward(
        testdata.coffee_id,
        user_id=f"{testdata.user_id}-other",
        wallet_id=wallet_id,
        idempotency_key=idempotency_key,
    )
    mismatch_response.expect_error(
        422,
        "IDEMPOTENCY_MISMATCH",
        what_proven="the same key with another payload is refused",
    )

    logger.warning("checking rewards service: one claim, one unit of stock")
    user_claim_ids = api.rewards_client.claim_ids(testdata.user_id)
    assertion.assert_equal(
        actual_result=user_claim_ids,
        expected_result=[claim_id],
        what_proven="the replay did not create a second claim",
        label="user claims",
    )

    stock_after = api.rewards_client.stock(testdata.coffee_id)
    assertion.assert_equal(
        actual_result=stock_after,
        expected_result=stock_before - 1,
        what_proven="the replay used only one unit of stock",
        label="reward stock",
    )

    logger.warning("checking wallet service: charged exactly once")
    wallet_response = api.wallet_client.get_wallet(wallet_id)
    wallet_after = wallet_response.expect(200).body
    assertion.assert_equal(
        actual_result=wallet_after["balance"],
        expected_result=testdata.enough_balance - testdata.coffee_cost,
        what_proven="the customer is charged the reward price once",
        label="wallet balance",
    )

    debits = api.wallet_client.debits(wallet_id)
    assertion.assert_length(
        actual_array=debits,
        expected_length=1,
        what_proven="the ledger has one debit, not two",
        label="wallet debits",
    )
