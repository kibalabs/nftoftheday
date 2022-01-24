import React from 'react';

import { dateToString } from '@kibalabs/core';

import { TokenTransfer } from '../client/resources';
import { NftCard } from './nftCard';

export type RandomTokenTransferCardProps = {
  tokenTransfer: TokenTransfer;
}

export const RandomTokenTransferCard = (props: RandomTokenTransferCardProps): React.ReactElement => {
  return (
    <NftCard
      tokenId={props.tokenTransfer.tokenId}
      collectionAddress={props.tokenTransfer.registryAddress}
      label='Random'
      subtitle={`Sold at ${dateToString(props.tokenTransfer.blockDate, 'HH:mm')} for Ξ${props.tokenTransfer.value / 1000000000000000000.0}`}
      primaryButtonText='View on OpenSea'
      primaryButtonTarget={`https://opensea.io/assets/${props.tokenTransfer.registryAddress}/${props.tokenTransfer.tokenId}?ref=0x18090cda49b21deaffc21b4f886aed3eb787d032`}
      secondaryButtonText='View Tx'
      secondaryButtonTarget={`https://etherscan.io/tx/${props.tokenTransfer.transactionHash}`}
      extraLabelVariants={['cardLabelRandom']}
      extraLabelBoxVariants={['cardLabelBoxRandom']}
    />
  );
};
