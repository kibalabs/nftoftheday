import React from 'react';

import { dateToString } from '@kibalabs/core';
import { ethers } from 'ethers';

import { TokenTransfer } from '../client/resources';
import { NftCard } from './nftCard';

export type RandomTokenTransferCardProps = {
  tokenTransfer: TokenTransfer;
}

export const RandomTokenTransferCard = (props: RandomTokenTransferCardProps): React.ReactElement => {
  return (
    <NftCard
      label='Random'
      subtitle={`Sold at ${dateToString(props.tokenTransfer.blockDate, 'HH:mm')} for Ξ${ethers.utils.formatEther(props.tokenTransfer.value)}`}
      primaryButtonText='View Token'
      secondaryButtonText='View Tx'
      secondaryButtonTarget={`https://etherscan.io/tx/${props.tokenTransfer.transactionHash}`}
      extraLabelVariants={['cardLabelRandom']}
      extraLabelBoxVariants={['cardLabelBoxRandom']}
      token={props.tokenTransfer.token}
      collection={props.tokenTransfer.collection}
    />
  );
};
