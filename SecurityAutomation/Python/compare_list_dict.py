"""
normalize and standardize dictionary keys between two lists of dictionaries.


It is particularly useful when you're dealing with inconsistent key naming, such as:

"North" in one dataset

"US North" in another dataset

By normalizing keys, you ensure data consistency across lists — an essential step for data integration, 
enrichment, or correlation tasks (e.g., in security automation, ETL pipelines, or configuration validation).
"""


#### Example Data
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


def normalize_keys(list_a, list_b, prefix="US "):
    """
    Normalize dictionary keys from list_a to ensure they match the
    prefixed key pattern found in list_b.

    Args:
        list_a (list[dict]): Source list of dictionaries (e.g., [{"North": "ip"}]).
        list_b (list[dict]): Reference list with standardized keys (e.g., [{"US North": "ip"}]).
        prefix (str): Optional prefix to prepend to keys (default: "US ").

    Returns:
        list[dict]: A new list with normalized keys (e.g., [{"US North": "ip"}]).
    """
    keys_b = {k for d in list_b for k in d.keys()}
    updated = []

    for d in list_a:
        for k, v in d.items():
            prefixed = f"{prefix}{k}"
            if prefixed in keys_b:
                updated.append({prefixed: v})
            else:
                updated.append({prefixed: v})
    return updated

normalized = normalize_keys(list1, list2)
print(normalized)

