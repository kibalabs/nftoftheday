import eth_utils


def normalize_32_byte_hex_address(value):
    as_bytes = eth_utils.to_bytes(hexstr=value)
    return str(eth_utils.to_normalized_address(as_bytes[-20:]))