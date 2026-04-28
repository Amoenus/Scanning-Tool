from scanning_tool.deposits.lookup import extract_code_from_text, lookup_deposit
from scanning_tool.deposits.scan_signatures import SCAN_SIGNATURE_REGISTRY
from scanning_tool.domain.models import ScanSignature


def test_extract_code_from_text_returns_none_for_empty_input():
    extraction = extract_code_from_text("")

    assert extraction.code is None
    assert extraction.raw is None


def test_extract_code_from_text_normalizes_alphanumeric_code():
    extraction = extract_code_from_text("Deposit A-12.34 scanned")

    assert extraction.raw == "A-12.34"
    assert extraction.code == "A-1234"


def test_extract_code_from_text_returns_none_for_unmatched_text():
    extraction = extract_code_from_text("No valid code here")

    assert extraction.code is None
    assert extraction.raw == "No valid code here"


def test_lookup_deposit_returns_none_when_code_is_missing():
    assert lookup_deposit(None) is None
    assert lookup_deposit("") is None
    assert lookup_deposit("XYZ") is None


def test_lookup_deposit_resolves_deposit_by_numeric_suffix(monkeypatch):
    signature = ScanSignature(
        name="Iron Ore",
        category="Metal",
        base_value=3,
        max_multiplier=7,
    )

    def fake_get_all():
        return {3: signature}

    monkeypatch.setattr(SCAN_SIGNATURE_REGISTRY, "get_all", fake_get_all)

    info = lookup_deposit("X-9")

    assert info is not None
    assert info.name == "Iron Ore"
    assert info.base_code == 3
    assert info.deposits == 3
    assert info.category == "Metal"
    assert info.max_multiplier == 7


def test_lookup_deposit_returns_none_for_non_matching_signature(monkeypatch):
    signature = ScanSignature(
        name="Platinum",
        category="Metal",
        base_value=5,
        max_multiplier=2,
    )

    def fake_get_all():
        return {5: signature}

    monkeypatch.setattr(SCAN_SIGNATURE_REGISTRY, "get_all", fake_get_all)

    assert lookup_deposit("A-9") is None
