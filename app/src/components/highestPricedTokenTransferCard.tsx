import React from 'react';

import { dateToString, shortFormatEther } from '@kibalabs/core';

import { TokenTransfer } from '../client/resources';
import { NftCard } from './nftCard';

export type HighestPricedTokenTransferCardProps = {
  tokenTransfer: TokenTransfer;
}

export const HighestPricedTokenTransferCard = (props: HighestPricedTokenTransferCardProps): React.ReactElement => {
  return (
    <NftCard
      label='Highest Priced'
      subtitle={`${dateToString(props.tokenTransfer.blockDate, 'HH:mm')} • ${shortFormatEther(props.tokenTransfer.value)}`}
      primaryButtonText='View Token'
      secondaryButtonText='View Tx'
      secondaryButtonTarget={`https://etherscan.io/tx/${props.tokenTransfer.transactionHash}`}
      token={props.tokenTransfer.token}
      collection={props.tokenTransfer.collection}
    />
  );
};
