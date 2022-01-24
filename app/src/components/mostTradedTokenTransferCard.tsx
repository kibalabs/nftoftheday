import React from 'react';

import { TokenTransfer } from '../client/resources';
import { NftCard } from './nftCard';

export type MostTradedTokenTransferCardProps = {
  tokenTransfers: TokenTransfer[];
}

export const MostTradedTokenTransferCard = (props: MostTradedTokenTransferCardProps): React.ReactElement => {
  return (
    <NftCard
      tokenId={props.tokenTransfers[0].tokenId}
      collectionAddress={props.tokenTransfers[0].registryAddress}
      label='Most Traded'
      subtitle={`Traded ${props.tokenTransfers.length} times today`}
      primaryButtonText='View on OpenSea'
      primaryButtonTarget={`https://opensea.io/assets/${props.tokenTransfers[0].registryAddress}/${props.tokenTransfers[0].tokenId}?ref=0x18090cda49b21deaffc21b4f886aed3eb787d032`}
      secondaryButtonText='View Tx'
      secondaryButtonTarget={`https://etherscan.io/tx/${props.tokenTransfers[0].transactionHash}`}
    />
  );
};
