import React from 'react';

import { LoadingSpinner } from '@kibalabs/ui-react';

import { Collection, CollectionToken, TokenTransfer } from '../client/resources';
import { useGlobals } from '../globalsContext';
import { ErrorCard } from './errorCard';
import { NftCard } from './nftCard';

export type MostTradedTokenTransferCardProps = {
  tokenTransfers: TokenTransfer[] | null;
}

export const MostTradedTokenTransferCard = (props: MostTradedTokenTransferCardProps): React.ReactElement => {
  const { notdClient } = useGlobals();
  const [asset, setAsset] = React.useState<CollectionToken | null>(null);
  const [collection, setCollection] = React.useState<Collection | null>(null);
  const [isLoading, setIsLoading] = React.useState<boolean>(false);
  const [error, setError] = React.useState<Error | null>(null);

  const updateAsset = React.useCallback(async (): Promise<void> => {
    setIsLoading(true);
    try {
      const tokenPromise = notdClient.retrieveCollectionToken(props.tokenTransfers[0].registryAddress, props.tokenTransfers[0].tokenId);
      const collectionPromise = notdClient.retrieveCollection(props.tokenTransfers[0].registryAddress);
      setAsset(await tokenPromise);
      setCollection(await collectionPromise);
    } catch (apiError: unknown) {
      setError(apiError as Error);
    }
    setIsLoading(false);
  }, [notdClient, props.tokenTransfers]);

  React.useEffect((): void => {
    if (!props.tokenTransfers) {
      setAsset(null);
      return;
    }
    updateAsset();
  }, [props.tokenTransfers, updateAsset]);

  return (
    <React.Fragment>
      { !error && (!props.tokenTransfers || isLoading || !asset || !collection) ? (
        <LoadingSpinner variant='light' />
      ) : error ? (<ErrorCard error={error} label='Most Traded' />)
        : (
          <NftCard
            token={asset}
            collection={collection}
            label='Most Traded'
            subtitle={`Traded ${props.tokenTransfers.length} times today`}
            primaryButtonText='View on OpenSea'
            primaryButtonTarget={`https://opensea.io/assets/${props.tokenTransfers[0].registryAddress}/${props.tokenTransfers[0].tokenId}?ref=0x18090cda49b21deaffc21b4f886aed3eb787d032`}
            secondaryButtonText='View Tx'
            secondaryButtonTarget={`https://etherscan.io/tx/${props.tokenTransfers[0].transactionHash}`}
            error={error}
          />
        )}
    </React.Fragment>
  );
};
