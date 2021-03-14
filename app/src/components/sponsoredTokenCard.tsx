import React from 'react';

import { dateToString, Requester } from '@kibalabs/core';
import { LoadingSpinner } from '@kibalabs/ui-react';

import { retrieveAsset } from '../assetUtil';
import { Token } from '../client/resources';
import { NftCard } from './nftCard';
import { Asset } from '../model';

export type SponsoredTokenCardProps = {
  token: Token | null;
}

export const SponsoredTokenCard = (props: SponsoredTokenCardProps): React.ReactElement => {
  const [asset, setAsset] = React.useState<Asset | null>(null);

  const updateAsset = React.useCallback(async (): Promise<void> => {
    retrieveAsset(new Requester(), props.token.registryAddress, props.token.tokenId).then((retrievedAsset: Asset): void => {
      setAsset(retrievedAsset);
    });
  }, [props.token]);

  React.useEffect((): void => {
    if (!props.token) {
      setAsset(null);
      return;
    }
    updateAsset();
  }, [props.token, updateAsset]);

  return (
    <React.Fragment>
      { !asset ? (
        <LoadingSpinner variant='light' />
      ) : (
        <NftCard
          label='Sponsored'
          title={asset.name}
          subtitle={asset.lastSalePrice ? `Last sold on ${dateToString(asset.lastSaleDate, 'dd-MMM-YYY')} for Ξ${asset.lastSalePrice / 1000000000000000000.0}` : 'Not claimed yet'}
          imageUrl={asset.imageUrl || asset.collection.imageUrl}
          collectionImage={asset.collection.imageUrl}
          collectionTitle={asset.collection.name}
          collectionUrl={asset.collection.externalUrl ?? asset.collection.openSeaUrl}
          primaryButtonText='View Token'
          primaryButtonTarget={asset.openSeaUrl}
          // secondaryButtonText='View Tx'
          // secondaryButtonTarget={`https://etherscan.io/tx/${props.tokenTransfers[0].transactionHash}`}
          extraLabelVariants={['cardLabelSponsored']}
          extraLabelBoxVariants={['cardLabelBoxSponsored']}
        />
      )}
    </React.Fragment>
  );
};
