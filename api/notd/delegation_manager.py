from __future__ import annotations

import dataclasses
import json
import typing
from typing import List
from typing import Optional

from core.exceptions import BadRequestException
from core.util import chain_util
from core.web3.eth_client import EthClientInterface
from web3.auto import w3


class DelegationType:
    NONE = 'NONE'
    ALL = 'ALL'
    CONTRACT = 'CONTRACT'
    TOKEN = 'TOKEN'

    @classmethod
    def from_raw(cls, value: int) -> str:
        if value == 0:
            return DelegationType.NONE
        if value == 1:
            return DelegationType.ALL
        if value == 2:
            return DelegationType.CONTRACT
        if value == 3:
            return DelegationType.TOKEN
        raise BadRequestException('Unknown DelegationType value')

@dataclasses.dataclass
class Delegation:
    delegationType: str
    vaultAddress: str
    delegateAddress: str
    contractAddress: Optional[str]
    tokenId: Optional[str]


DEPOSIT_CASH_ADDRESS = '0x00000000000076A84feF008CDAbe6409d2FE638B'


class DelegationManager:

    def __init__(self, ethClient: EthClientInterface) -> None:
        self.ethClient = ethClient
        with open('./contracts/DelegationRegistry.json') as contractJsonFile:
            contractJson = json.load(contractJsonFile)
        self.depositCashContract = w3.eth.contract(address=DEPOSIT_CASH_ADDRESS, abi=contractJson['abi'])  # type: ignore[call-overload]

    async def get_delegations(self, delegateAddress: str) -> List[Delegation]:
        response = await self.ethClient.call_contract_function(contract=self.depositCashContract, functionName='getDelegationsByDelegate', arguments={'delegate': delegateAddress})
        delegations = []
        for ((delegationTypeValue, vaultAddressRaw, delegateAddressRaw, contractAddressRaw, tokenIdRaw), ) in response:
            delegation = Delegation(
                delegationType=DelegationType.from_raw(value=delegationTypeValue),
                vaultAddress=chain_util.normalize_address(vaultAddressRaw),
                delegateAddress=chain_util.normalize_address(delegateAddressRaw),
                contractAddress=None if contractAddressRaw == chain_util.BURN_ADDRESS else chain_util.normalize_address(contractAddressRaw),
                tokenId=None if tokenIdRaw == 0 else typing.cast(str, tokenIdRaw),
            )
            if delegation.delegationType != DelegationType.NONE:
                delegations.append(delegation)
        return delegations
