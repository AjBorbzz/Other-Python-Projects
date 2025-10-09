"""
geo_mapper.py

Utility module for normalizing and mapping region-based dictionary keys
between multiple datasets (e.g., "North" ↔ "US North").

Useful for:
- Data normalization between sources
- Harmonizing keys across APIs or logs
- Security automation pipelines (e.g., region mapping in XSOAR/XSIAM)
"""

import logging
from typing import List, Dict, Set, Optional


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def extract_keys(dict_list: List[Dict]) -> Set[str]:
    """Flatten and return all keys from a list of dictionaries."""
    return {k for d in dict_list for k in d.keys()}


def normalize_keys(list_a: List[Dict], list_b: List[Dict], prefix: str = "US ") -> List[Dict]:
    """
    Normalize dictionary keys from list_a so they align with the
    prefixed format found in list_b (e.g., "North" -> "US North").

    Args:
        list_a: Source list of dictionaries (e.g., [{"North": "ip"}]).
        list_b: Reference list (e.g., [{"US North": "ip"}]).
        prefix: Prefix to prepend (default: "US ").

    Returns:
        A new list with normalized keys.
    """
    keys_b = extract_keys(list_b)
    updated = []

    for d in list_a:
        for k, v in d.items():
            prefixed = f"{prefix}{k}"
            if prefixed not in keys_b:
                logging.warning(f"Key '{k}' not found in reference list. Mapping to '{prefixed}'.")
            updated.append({prefixed: v})

    return updated


def map_if_missing(list_a: List[Dict], list_b: List[Dict], prefix: str = "US ") -> List[Dict]:
    """
    Only map keys from list_a if the prefixed version is missing in list_b.

    Args:
        list_a: Source list of dictionaries.
        list_b: Reference list.
        prefix: Prefix to prepend (default: "US ").

    Returns:
        Updated list with missing keys mapped to prefixed versions.
    """
    keys_b = extract_keys(list_b)
    result = []
    for d in list_a:
        for k, v in d.items():
            prefixed = f"{prefix}{k}"
            if prefixed not in keys_b:
                logging.info(f"Mapping missing key '{k}' → '{prefixed}'")
                result.append({prefixed: v})
            else:
                result.append(d)
    return result


def inverse_mapping(dict_list: List[Dict], prefix: str = "US ") -> List[Dict]:
    """
    Remove prefix from dictionary keys (e.g., "US North" -> "North").

    Args:
        dict_list: List of dictionaries with prefixed keys.
        prefix: Prefix string to strip (default: "US ").

    Returns:
        New list with de-prefixed keys.
    """
    stripped = []
    for d in dict_list:
        for k, v in d.items():
            if k.startswith(prefix):
                new_key = k[len(prefix):]
                stripped.append({new_key: v})
            else:
                stripped.append({k: v})
    return stripped


def auto_detect_prefix(dict_list: List[Dict]) -> Optional[str]:
    """
    Detect prefix pattern from a list of dictionaries.
    Example: {"US North"} → returns "US "

    Args:
        dict_list: List of dictionaries to scan.

    Returns:
        Detected prefix string or None.
    """
    for d in dict_list:
        for k in d.keys():
            parts = k.split(" ", 1)
            if len(parts) == 2:
                return parts[0] + " "
    return None


if __name__ == "__main__":
    list1 = [
        {"North": "208.127.241.247"},
        {"South": "165.1.201.45"},
        {"Central": "130.41.64.241"}
    ]

    list2 = [
        {"US North": "208.127.241.247"},
        {"US South": "165.1.201.45"},
        {"US Central": "130.41.64.241"}
    ]

    # Detect prefix automatically
    detected_prefix = auto_detect_prefix(list2)
    logging.info(f"Detected prefix: {detected_prefix}")

    # Normalize list1 against list2
    normalized = normalize_keys(list1, list2, prefix=detected_prefix)
    logging.info(f"Normalized: {normalized}")

    # Convert back to unprefixed keys
    unprefixed = inverse_mapping(normalized, prefix=detected_prefix)
    logging.info(f"Inverse mapped: {unprefixed}")
