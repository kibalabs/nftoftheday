from eth_typing.encoding import HexStr
import eth_utils


def normalize_address(value:HexStr)->str:
    address = eth_utils.to_bytes(hexstr=value)
    return str(eth_utils.to_normalized_address(address[-20:]))
