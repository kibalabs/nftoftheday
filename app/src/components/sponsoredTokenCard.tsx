import React from 'react';

import { NftCard } from './nftCard';
import { Collection, CollectionToken, TokenTransfer } from '../client/resources';

export type SponsoredTokenCardProps = {
  token: CollectionToken;
  collection: Collection;
  latestTransfer: TokenTransfer | null;
}

export const SponsoredTokenCard = (props: SponsoredTokenCardProps): React.ReactElement => {
  return (
    <NftCard
      label='Sponsored'
      // subtitle={asset.lastSalePrice ? `Last sold for Ξ${asset.lastSalePrice / 21000000000000000000.0}` : 'Up for grabs!'}
      subtitle={'Up for grabs!'}
      primaryButtonText='View Token'
      // secondaryButtonText='View Tx'
      // secondaryButtonTarget={`https://etherscan.io/tx/${props.tokenTransfers[0].transactionHash}`}
      extraLabelVariants={['cardLabelSponsored']}
      extraLabelBoxVariants={['cardLabelBoxSponsored']}
      token={props.token}
      collection={props.collection}
    />
  );
};
