import React from 'react';

import { Token } from '../client/resources';
import { NftCard } from './nftCard';

export type SponsoredTokenCardProps = {
  token: Token;
}

export const SponsoredTokenCard = (props: SponsoredTokenCardProps): React.ReactElement => {
  return (
    <NftCard
      tokenId={props.token.tokenId}
      collectionAddress={props.token.registryAddress}
      label='Sponsored'
      // subtitle={asset.lastSalePrice ? `Last sold for Ξ${asset.lastSalePrice / 21000000000000000000.0}` : 'Up for grabs!'}
      subtitle={'Up for grabs!'}
      primaryButtonText='View on OpenSea'
      primaryButtonTarget={`https://opensea.io/assets/${props.token.registryAddress}/${props.token.tokenId}?ref=0x18090cda49b21deaffc21b4f886aed3eb787d032`}
      // secondaryButtonText='View Tx'
      // secondaryButtonTarget={`https://etherscan.io/tx/${props.tokenTransfers[0].transactionHash}`}
      extraLabelVariants={['cardLabelSponsored']}
      extraLabelBoxVariants={['cardLabelBoxSponsored']}
    />
  );
};
