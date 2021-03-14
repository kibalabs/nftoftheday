import React from 'react';

import { dateToString, Requester } from '@kibalabs/core';
import { LoadingSpinner } from '@kibalabs/ui-react';

import { retrieveAsset } from '../assetUtil';
import { TokenTransfer } from '../client/resources';
import { Asset } from '../model';
import { NftCard } from './nftCard';

export type RandomTokenTransferCardProps = {
  tokenTransfer: TokenTransfer | null;
}

export const RandomTokenTransferCard = (props: RandomTokenTransferCardProps): React.ReactElement => {
  const [asset, setAsset] = React.useState<Asset | null>(null);

  const updateAsset = React.useCallback(async (): Promise<void> => {
    retrieveAsset(new Requester(), props.tokenTransfer.registryAddress, props.tokenTransfer.tokenId).then((retrievedAsset: Asset): void => {
      setAsset(retrievedAsset);
    });
  }, [props.tokenTransfer]);

  React.useEffect((): void => {
    if (!props.tokenTransfer) {
      setAsset(null);
      return;
    }
    updateAsset();
  }, [props.tokenTransfer, updateAsset]);

  return (
    <React.Fragment>
      { !asset ? (
        <LoadingSpinner variant='light' />
      ) : (
        <NftCard
          label='Random'
          title={asset.name}
          subtitle={`Sold at ${dateToString(props.tokenTransfer.blockDate, 'HH:mm')} for Ξ${props.tokenTransfer.value / 1000000000000000000.0}`}
          imageUrl={asset.imageUrl || asset.collection.imageUrl}
          collectionImage={asset.collection.imageUrl}
          collectionTitle={asset.collection.name}
          collectionUrl={asset.collection.externalUrl ?? asset.collection.openSeaUrl}
          primaryButtonText='View Token'
          primaryButtonTarget={asset.openSeaUrl}
          secondaryButtonText='View Tx'
          secondaryButtonTarget={`https://etherscan.io/tx/${props.tokenTransfer.transactionHash}`}
          extraLabelVariants={['cardLabelRandom']}
          extraLabelBoxVariants={['cardLabelBoxRandom']}
        />
      )}
    </React.Fragment>
  );
};
