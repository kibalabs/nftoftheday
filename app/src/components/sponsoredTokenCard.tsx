import React from 'react';

import { dateToString } from '@kibalabs/core';
import { LoadingSpinner } from '@kibalabs/ui-react';

import { RegistryToken, Token } from '../client/resources';
import { useGlobals } from '../globalsContext';
import { NftCard } from './nftCard';

export type SponsoredTokenCardProps = {
  token: Token | null;
}

export const SponsoredTokenCard = (props: SponsoredTokenCardProps): React.ReactElement => {
  const { notdClient } = useGlobals();
  const [asset, setAsset] = React.useState<RegistryToken | null>(null);

  const updateAsset = React.useCallback(async (): Promise<void> => {
    notdClient.retrieveRegistryToken(props.token.registryAddress, props.token.tokenId).then((registryToken: RegistryToken): void => {
      setAsset(registryToken);
    });
  }, [notdClient, props.token]);

  React.useEffect((): void => {
    if (!props.token) {
      setAsset(null);
      return;
    }
    updateAsset();
  }, [props.token, updateAsset]);

  return (
    <React.Fragment>
      { !props.token || !asset ? (
        <LoadingSpinner variant='light' />
      ) : (
        <NftCard
          label='Sponsored'
          title={asset.name}
          subtitle={asset.lastSalePrice ? `Last sold on ${dateToString(asset.lastSaleDate, 'dd-MMM-YYY')} for Ξ${asset.lastSalePrice / 1000000000000000000.0}` : 'Not claimed yet'}
          imageUrl={asset.imageUrl || asset.collectionImageUrl || '/asset/icon.svg'}
          collectionImage={asset.collectionImageUrl}
          collectionTitle={asset.collectionName}
          collectionUrl={asset.collectionExternalUrl ?? asset.collectionOpenSeaUrl}
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
