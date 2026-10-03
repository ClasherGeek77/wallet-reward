#!/bin/bash
# run the tests without remembering any pytest syntax, needs ./first_setup.sh once
#   ./run_test.sh                                       run what TEST_PATH says below
#   ./run_test.sh tests/test_reward_claim.py            an argument replaces TEST_PATH
# the machinery lives in run_engine.sh, this file is only the two settings to edit
cd "$(dirname "$0")"

# base test path, edit this line to change what runs by default, variants:
#   TEST_PATH="tests/"                                                                  everything
#   TEST_PATH="tests/test_reward_claim.py"                                              one file
#   TEST_PATH="tests/test_reward_claim.py::test_replayed_claim_request_charges_wallet_only_once"   one test
#   TEST_PATH="tests/ -k insufficient"                                                  tests whose name contains "insufficient"
#   TEST_PATH="tests/ -x"                                                               stop at the first failure
TEST_PATH="tests/"

# report file name, written to reports/, edit this line to change it, variants:
#   REPORT_NAME=""                  default: report_<run timestamp>_<test path>.html, filled in at run time
#                                   e.g. report_2024-01-30_16-15-42_tests-test_reward_claim.py.html
#   REPORT_NAME="smoke.html"        a fixed name (overwritten by the next run)
REPORT_NAME=""

export TEST_PATH REPORT_NAME
exec ./run_engine.sh "$@"
