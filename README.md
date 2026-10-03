# Wallet + Rewards: cross-service API tests

Python and pytest. `mock_services.py`, one folder up, is untouched.

## How to run it

```bash
# terminal 1 - the services (leave running), from the folder above this one
cd ..
python3 -m venv .venv && source .venv/bin/activate
python -m pip install -r requirements.txt
python mock_services.py

# terminal 2 - from this folder
./first_setup.sh                                          # once
./run_test.sh                                             # all 3 tests
./run_test.sh tests/test_reward_claim.py::test_name       # one test
./checks.sh                                               # bandit, black and pylint
```

engineer no need to remember any pytest cli syntax. `first_setup.sh` builds `.venv`, `run_test.sh` runs the tests and `run_engine.sh` is the machinery behind it.

`run_test.sh` config the test path and the report name, with the example of each variant in a comment. report name default has the timestamp when it is run and what test path is being run, dynamically: `reports/report_<timestamp>_<test path>.html`.

settings are plain `KEY=value` lines in `test.env`, like `WALLET_URL=http://127.0.0.1:8081`. if we add a new env, it is shown automatically at the start of every run. `run_test.sh` is a bash script; on Windows use Git Bash or WSL.

## The tests

each one verifies the effect in both services.

1. `test_claiming_affordable_reward_debits_wallet_and_fulfils_claim`
2. `test_claim_with_insufficient_balance_is_rejected_and_wallet_untouched`
3. `test_replayed_claim_request_charges_wallet_only_once`

a new test asks for the fixtures it needs: `testdata`, `api`, `assertion` and `logger`, no import needed. to add an endpoint, put its path in `harness/endpoints.py` and write a one or two line method in `harness/clients.py` that calls `get` or `post`.

## Design decisions

- **keep the code minimal, but a pattern:** a post to an endpoint can reuse the already made function. every client method reuses `HttpClient.get` or `post`.
- **even though the path is the same, each service has its own** `reset` endpoint. it is ok to be duplicate, so it is commented.
- **non changing data is static, in `constant_data`.** what depends on the environment is in `environment_data`, filled from `test.env`. no magic numbers inside a test.
- **setup and teardown at the start and end of all tests, not every test.** 
- **unix timestamp for better uniqueness, with a prefix.** 
- **assertion is a fixture** so no need to import it. every business check has to say `what_proven`, shown as a warning in the log, so a test cannot pass by only checking that the call returned 2xx. a check without it is refused.
- **steps are logged in human language.**
- **HTML report is just a config file** (`pytest.ini`), minimal to include, no custom reporting code.
- **static versions:** `.python-version` is 3.12.15 and every tool in `requirements.pip` is pinned.
- **lint:** Bandit, black and pylint. no lint plugins, no flake8. just pip install on the go. no breaking ur rule at all but satisfy my standard of coding.
- **human readable code even without comment:** `#` comments only, all lower caps, minimal and only enough for people to know. no `"""`. plain steps over advanced syntax. no one liner syntax even if on the "return this if x; then y" friendly to new engineer to start.
- **good names:** `testdata`, `api`, `assertion`, not short ones like `ass` over simplified.

## Left out on purpose

lint plugins, Docker, UI and load tests, a CI pipeline and reporting dashboards. parallel runs, because of the global reset.

## With another day

1. add more testcases; just tell other engineers to do it since the design system work is done and easy to build new autotest alrd lah.
2. docker build is mandatory for next day since ppl are not good with setup most of the time than not able to code new autotest.
3. make class of autotestcases so its like sequential for a longer integration test api.

## Findings in the mock

from reading the spec and the source i got the wallet `currency` is stored but never checked (ya hardcoded to IDR). a USD wallet pays the 25000 IDR coffee price with no error, and so does any text.
