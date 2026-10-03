import logging

logger = logging.getLogger(__name__)


# the only place with bare assert, every check is logged as a step
class Assertion:
    # only says the call worked, it proves no business outcome
    def assert_status(self, actual_status, expected_status, detail=""):
        logger.info(
            f"checking HTTP status: got {actual_status}, expected {expected_status}"
        )
        assert actual_status == expected_status, (
            f"HTTP status: actual {actual_status!r} is not equal to expected "
            f"{expected_status!r} {detail}"
        )

    # a business check must say what it proves, shown as a warning in the log
    def say_what_proven(self, what_proven):
        if not what_proven or not what_proven.strip():
            raise ValueError("what_proven must say which business outcome is proven")
        logger.warning(f"proving that {what_proven}")

    def assert_equal(
        self, actual_result, expected_result, *, what_proven, label="value", detail=""
    ):
        self.say_what_proven(what_proven)
        logger.info(
            f"checking {label}: got {actual_result}, expected {expected_result}"
        )
        assert actual_result == expected_result, (
            f"{label}: actual {actual_result!r} is not equal to expected "
            f"{expected_result!r} {detail} | not proven: {what_proven}"
        )

    def assert_is_none(self, actual_result, *, what_proven, label="value"):
        self.say_what_proven(what_proven)
        logger.info(f"checking {label}: got {actual_result}, expected none")
        assert (
            actual_result is None
        ), f"{label}: actual {actual_result!r} is not None | not proven: {what_proven}"

    def assert_length(
        self, actual_array, expected_length, *, what_proven, label="list"
    ):
        self.say_what_proven(what_proven)
        actual_length = len(actual_array)
        logger.info(
            f"checking {label}: got {actual_length}, expected {expected_length}"
        )
        assert actual_length == expected_length, (
            f"{label}: length {actual_length} is not {expected_length}: "
            f"{actual_array!r} | not proven: {what_proven}"
        )
