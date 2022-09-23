import json
from typing import Optional

from core.util import chain_util
from core.web3.eth_client import EthClientInterface
from ens.utils import normal_name_to_hash as ens_name_to_hash
from ens.utils import normalize_name as ens_normalize_name


class AccountEnsNameProcessor:

    def __init__(self, ethClient: EthClientInterface) -> None:
        self.ethClient = ethClient
        with open('./contracts/ENSRegistry.json') as contractJsonFile:
            ensRegistryContractJson = json.load(contractJsonFile)
        self.ensRegistryContractAddress = ensRegistryContractJson['address']
        self.ensRegistryContractAbi = ensRegistryContractJson['abi']
        self.ensRegistryResolveFunctionAbi = [internalAbi for internalAbi in self.ensRegistryContractAbi if internalAbi.get('name') == 'resolver'][0]
        with open('./contracts/ENSDefaultReverseResolver.json') as contractJsonFile:
            ensReverseResolverContractJson = json.load(contractJsonFile)
        self.ensReverseResolverContractAbi = ensReverseResolverContractJson['abi']
        self.ensReverseResolverNameFunctionAbi = [internalAbi for internalAbi in self.ensReverseResolverContractAbi if internalAbi.get('name') == 'name'][0]

    async def get_ens_name(self, accountAddress: str) -> Optional[str]:
        accountAddress = chain_util.normalize_address(value=accountAddress)
        ensNormalizedAddress = ens_normalize_name(f'{accountAddress.lower().replace("0x", "", 1)}.addr.reverse')
        ensNormalizedHashedAddress = ens_name_to_hash(ensNormalizedAddress)
        addressNodeResult = await self.ethClient.call_function(toAddress=self.ensRegistryContractAddress, contractAbi=self.ensRegistryContractAbi, functionAbi=self.ensRegistryResolveFunctionAbi, arguments={'node': ensNormalizedHashedAddress})
        addressNode = addressNodeResult[0]
        normalizedName = None
        if addressNode and addressNode != chain_util.BURN_ADDRESS:
            nameResult = await self.ethClient.call_function(toAddress=addressNode, contractAbi=self.ensReverseResolverContractAbi, functionAbi=self.ensReverseResolverNameFunctionAbi, arguments={'': ensNormalizedHashedAddress})
            name = nameResult[0]
            normalizedName = ens_normalize_name(name)
        return normalizedName
