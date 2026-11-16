
from hypothesis import given, strategies as st
from warranty_claims import parse_claim, age_average, payable_charge


# Test 1: Fuzz testing parse_claim()
@given(st.text() | st.none())
def test_parse_claim_no_crash(s):
    try:
        parse_claim(s)
    except Exception as e:
        assert False, f"parse_claim crashed with input {s!r}: {e}"


# Test 2: Fuzz testing age_average()
@given(st.text() | st.none())
def test_age_average_no_crash(s):
    try:
        age_average(s)
    except Exception as e:
        assert False, f"age_average crashed with input {s!r}: {e}"


# Test 3: Fuzz testing payable_charge()
@given(st.text() | st.none())
def test_payable_charge_no_crash(s):
    try:
        payable_charge(s)
    except Exception as e:
        assert False, f"payable_charge crashed with input {s!r}: {e}"
