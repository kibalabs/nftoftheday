import React from 'react';

import { dateToString } from '@kibalabs/core';
import { LoadingSpinner } from '@kibalabs/ui-react';

import { Collection, CollectionToken, TokenTransfer } from '../client/resources';
import { useGlobals } from '../globalsContext';
import { NftCard } from './nftCard';

export type RandomTokenTransferCardProps = {
  tokenTransfer: TokenTransfer | null;
}

export const RandomTokenTransferCard = (props: RandomTokenTransferCardProps): React.ReactElement => {
  const { notdClient } = useGlobals();
  const [asset, setAsset] = React.useState<CollectionToken | null>(null);
  const [collection, setCollection] = React.useState<Collection | null>(null);
  const [isLoading, setIsLoading] = React.useState<boolean>(false);
  const [error, setError] = React.useState<Error | null>(null);

  const updateAsset = React.useCallback(async (): Promise<void> => {
    // retrieveAsset(requester, props.tokenTransfer.registryAddress, props.tokenTransfer.tokenId).then((token: CollectionToken): void => {
    //   setAsset(registryToken);
    //   setIsLoading(false);
    // }).catch((apiError : unknown) => {
    //   setError(apiError as Error);
    //   setIsLoading(false);
    // });
    setIsLoading(true);
    notdClient.retrieveCollectionToken(props.tokenTransfer.registryAddress, props.tokenTransfer.tokenId).then((token: CollectionToken): void => {
      setAsset(token);
      notdClient.retrieveCollection(props.tokenTransfer.registryAddress).then((collection: Collection): void => {
        setCollection(collection);
        setIsLoading(false);
      })
    }).catch((apiError : unknown) => {
      setError(apiError as Error);
      setIsLoading(false);
    });
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
      { !props.tokenTransfer || isLoading || !asset || !collection ? (
        <LoadingSpinner variant='light' />
      ) : (
        <NftCard
          token={asset}
          collection={collection}
          label='Random'
          subtitle={`Sold at ${dateToString(props.tokenTransfer.blockDate, 'HH:mm')} for Ξ${props.tokenTransfer.value / 1000000000000000000.0}`}
          primaryButtonText='View on OpenSea'
          primaryButtonTarget={`https://opensea.io/assets/${props.tokenTransfer.registryAddress}/${props.tokenTransfer.tokenId}?ref=0x18090cda49b21deaffc21b4f886aed3eb787d032`}
          secondaryButtonText='View Tx'
          secondaryButtonTarget={`https://etherscan.io/tx/${props.tokenTransfer.transactionHash}`}
          extraLabelVariants={['cardLabelRandom']}
          extraLabelBoxVariants={['cardLabelBoxRandom']}
          error={error}
        />
      )}
    </React.Fragment>
  );
};
