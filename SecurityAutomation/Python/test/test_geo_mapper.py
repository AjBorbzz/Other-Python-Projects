# test_geo_mapper.py
import pytest

from geo_mapper import (
    extract_keys,
    normalize_keys,
    map_if_missing,
    inverse_mapping,
    auto_detect_prefix,
)


@pytest.fixture
def list_a_unprefixed():
    # Source list with raw keys
    return [
        {"North": "208.127.241.247"},
        {"South": "165.1.201.45"},
        {"Central": "130.41.64.241"},
    ]


@pytest.fixture
def list_b_prefixed():
    # Reference list with prefixed keys
    return [
        {"US North": "208.127.241.247"},
        {"US South": "165.1.201.45"},
        {"US Central": "130.41.64.241"},
    ]


@pytest.fixture
def list_b_prefixed_partial():
    # Reference list missing one key
    return [
        {"US South": "165.1.201.45"},
        {"US Central": "130.41.64.241"},
    ]


def test_extract_keys_basic(list_b_prefixed):
    keys = extract_keys(list_b_prefixed)
    assert keys == {"US North", "US South", "US Central"}


def test_extract_keys_empty():
    assert extract_keys([]) == set()


def test_auto_detect_prefix_detects(list_b_prefixed):
    prefix = auto_detect_prefix(list_b_prefixed)
    assert prefix == "US "


def test_auto_detect_prefix_none_when_unprefixed(list_a_unprefixed):
    prefix = auto_detect_prefix(list_a_unprefixed)
    # Keys like "North" (no space-separated prefix) → None
    assert prefix is None


def test_auto_detect_prefix_works_with_other_prefix():
    data = [{"EU West": 1}, {"EU Central": 2}]
    assert auto_detect_prefix(data) == "EU "



def test_inverse_mapping_basic(list_b_prefixed):
    out = inverse_mapping(list_b_prefixed, prefix="US ")
    # Expect removal of "US " prefix
    assert out == [
        {"North": "208.127.241.247"},
        {"South": "165.1.201.45"},
        {"Central": "130.41.64.241"},
    ]


def test_inverse_mapping_no_prefix_present():
    data = [{"North": 1}, {"South": 2}]
    # No change if prefix not present
    assert inverse_mapping(data, prefix="US ") == data


def test_normalize_keys_maps_all_with_detected_prefix(list_a_unprefixed, list_b_prefixed):
    prefix = auto_detect_prefix(list_b_prefixed)
    out = normalize_keys(list_a_unprefixed, list_b_prefixed, prefix=prefix)
    # normalize_keys always maps to prefixed keys (even if not found in list_b)
    assert out == [
        {"US North": "208.127.241.247"},
        {"US South": "165.1.201.45"},
        {"US Central": "130.41.64.241"},
    ]


def test_normalize_keys_with_manual_prefix(list_a_unprefixed, list_b_prefixed):
    out = normalize_keys(list_a_unprefixed, list_b_prefixed, prefix="US ")
    assert out == [
        {"US North": "208.127.241.247"},
        {"US South": "165.1.201.45"},
        {"US Central": "130.41.64.241"},
    ]


def test_normalize_keys_handles_missing_in_reference(list_a_unprefixed, list_b_prefixed_partial):
    # list_b is missing "US North"; normalize still maps "North" -> "US North"
    out = normalize_keys(list_a_unprefixed, list_b_prefixed_partial, prefix="US ")
    assert out == [
        {"US North": "208.127.241.247"},  # mapped even though missing in reference
        {"US South": "165.1.201.45"},
        {"US Central": "130.41.64.241"},
    ]



def test_map_if_missing_only_maps_when_absent(list_a_unprefixed, list_b_prefixed_partial):
    # "US North" missing in list_b_prefixed_partial, so only that one gets mapped
    out = map_if_missing(list_a_unprefixed, list_b_prefixed_partial, prefix="US ")
    # The function appends mapped dicts for missing keys, and keeps originals for present keys
    assert out == [
        {"US North": "208.127.241.247"},    # mapped because missing
        {"South": "165.1.201.45"},          # kept as original (US South exists)
        {"Central": "130.41.64.241"},       # kept as original (US Central exists)
    ]


def test_map_if_missing_keeps_all_when_present(list_a_unprefixed, list_b_prefixed):
    # All prefixed forms exist in list_b_prefixed → no mapping needed
    out = map_if_missing(list_a_unprefixed, list_b_prefixed, prefix="US ")
    assert out == list_a_unprefixed


def test_normalize_then_inverse_roundtrip(list_a_unprefixed, list_b_prefixed):
    prefix = auto_detect_prefix(list_b_prefixed)
    normalized = normalize_keys(list_a_unprefixed, list_b_prefixed, prefix=prefix)
    roundtrip = inverse_mapping(normalized, prefix=prefix)
    assert roundtrip == list_a_unprefixed


def test_empty_inputs_behave_safely():
    assert normalize_keys([], [], prefix="US ") == []
    assert map_if_missing([], [], prefix="US ") == []
    assert inverse_mapping([], prefix="US ") == []


def test_case_sensitivity_behavior():
    # Keys are compared exactly; "north" != "North"
    a = [{"north": 1}]
    b = [{"US North": 1}]
    prefix = auto_detect_prefix(b)
    out = normalize_keys(a, b, prefix=prefix)
    # Since "north" is not "North", it still maps with exact lower-case:
    assert out == [{"US north": 1}]
