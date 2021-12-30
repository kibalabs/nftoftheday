import React from 'react';

import { dateToString } from '@kibalabs/core';
import { LoadingSpinner } from '@kibalabs/ui-react';

import { Collection, CollectionToken, TokenTransfer } from '../client/resources';
import { useGlobals } from '../globalsContext';
import { NftCard } from './nftCard';

export type HighestPricedTokenTransferCardProps = {
  tokenTransfer: TokenTransfer | null;
}

export const HighestPricedTokenTransferCard = (props: HighestPricedTokenTransferCardProps): React.ReactElement => {
  const { notdClient } = useGlobals();
  const [asset, setAsset] = React.useState<CollectionToken | null>(null);
  const [collection, setCollection] = React.useState<Collection | null>(null);
  const [isLoading, setIsLoading] = React.useState<boolean>(false);
  const [error, setError] = React.useState<Error | null>(null);

  const updateAsset = React.useCallback(async (): Promise<void> => {
    setIsLoading(true);
    try {
      const tokenPromise = notdClient.retrieveCollectionToken(props.tokenTransfer.registryAddress, props.tokenTransfer.tokenId);
      const collectionPromise = notdClient.retrieveCollection(props.tokenTransfer.registryAddress);
      setAsset(await tokenPromise);
      setCollection(await collectionPromise);
    } catch (apiError: unknown) {
      setError(apiError as Error);
    }
    setIsLoading(false);
  }, [notdClient, props.tokenTransfer]);

  React.useEffect((): void => {
    if (!props.tokenTransfer) {
      setAsset(null);
      return;
    }
    updateAsset();
  }, [props.tokenTransfer, updateAsset]);

  return (
    <React.Fragment>
      { !props.tokenTransfer || isLoading ? (
        <LoadingSpinner variant='light' />
      ) : (
        <NftCard
          token={asset}
          collection={collection}
          label='Highest Priced'
          subtitle={`Sold at ${dateToString(props.tokenTransfer.blockDate, 'HH:mm')} for Ξ${props.tokenTransfer.value / 1000000000000000000.0}`}
          primaryButtonText='View on OpenSea'
          primaryButtonTarget={`https://opensea.io/assets/${props.tokenTransfer.registryAddress}/${props.tokenTransfer.tokenId}?ref=0x18090cda49b21deaffc21b4f886aed3eb787d032`}
          secondaryButtonText='View Tx'
          secondaryButtonTarget={`https://etherscan.io/tx/${props.tokenTransfer.transactionHash}`}
          error ={error}
        />
      )}
    </React.Fragment>
  );
};
