import React from 'react';

import { dateToString } from '@kibalabs/core';

import { TokenTransfer } from '../client/resources';
import { NftCard } from './nftCard';

export type HighestPricedTokenTransferCardProps = {
  tokenTransfer: TokenTransfer;
}

export const HighestPricedTokenTransferCard = (props: HighestPricedTokenTransferCardProps): React.ReactElement => {
  return (
    <NftCard
      label='Highest Priced'
      subtitle={`Sold at ${dateToString(props.tokenTransfer.blockDate, 'HH:mm')} for Ξ${props.tokenTransfer.value / 1000000000000000000.0}`}
      primaryButtonText='View on OpenSea'
      primaryButtonTarget={`https://opensea.io/assets/${props.tokenTransfer.registryAddress}/${props.tokenTransfer.tokenId}?ref=0x18090cda49b21deaffc21b4f886aed3eb787d032`}
      secondaryButtonText='View Tx'
      secondaryButtonTarget={`https://etherscan.io/tx/${props.tokenTransfer.transactionHash}`}
      token={props.tokenTransfer.token}
      collection={props.tokenTransfer.collection}
    />
  );
};
