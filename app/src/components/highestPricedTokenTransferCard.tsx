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
      primaryButtonText='View Token'
      secondaryButtonText='View tx'
      secondaryButtonTarget={`https://etherscan.io/tx/${props.tokenTransfer.transactionHash}`}
      token={props.tokenTransfer.token}
      collection={props.tokenTransfer.collection}
    />
  );
};
