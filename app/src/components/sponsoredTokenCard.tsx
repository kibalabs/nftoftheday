import React from 'react';

import { LoadingSpinner } from '@kibalabs/ui-react';

import { Collection, CollectionToken, Token } from '../client/resources';
import { useGlobals } from '../globalsContext';
import { ErrorCard } from './errorCard';
import { NftCard } from './nftCard';

export type SponsoredTokenCardProps = {
  token: Token | null;
}

export const SponsoredTokenCard = (props: SponsoredTokenCardProps): React.ReactElement => {
  const { notdClient } = useGlobals();
  const [asset, setAsset] = React.useState<CollectionToken | null>(null);
  const [collection, setCollection] = React.useState<Collection | null>(null);
  const [isLoading, setIsLoading] = React.useState<boolean>(false);
  const [error, setError] = React.useState<Error | null>(null);

  const updateAsset = React.useCallback(async (): Promise<void> => {
    setIsLoading(true);
    try {
      const tokenPromise = notdClient.retrieveCollectionToken(props.token.registryAddress, props.token.tokenId);
      const collectionPromise = notdClient.retrieveCollection(props.token.registryAddress);
      setAsset(await tokenPromise);
      setCollection(await collectionPromise);
    } catch (apiError: unknown) {
      setError(apiError as Error);
    }
    setIsLoading(false);
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
      {error ? (
        <ErrorCard error={error} label='Sponsored' />
      ) : (
        !props.token || isLoading || !asset || !collection) ? (
          <LoadingSpinner variant='light' />
        ) : (
          <NftCard
            token={asset}
            collection={collection}
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
        )}
    </React.Fragment>
  );
};
