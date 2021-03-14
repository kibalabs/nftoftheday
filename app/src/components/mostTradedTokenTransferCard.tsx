import React from 'react';

import { Requester } from '@kibalabs/core';
import { LoadingSpinner } from '@kibalabs/ui-react';

import { retrieveAsset } from '../assetUtil';
import { TokenTransfer } from '../client/resources';
import { Asset } from '../model';
import { NftCard } from './nftCard';

export type MostTradedTokenTransferCardProps = {
  tokenTransfers: TokenTransfer[] | null;
}

export const MostTradedTokenTransferCard = (props: MostTradedTokenTransferCardProps): React.ReactElement => {
  const [asset, setAsset] = React.useState<Asset | null>(null);

  const updateAsset = React.useCallback(async (): Promise<void> => {
    retrieveAsset(new Requester(), props.tokenTransfers[0].registryAddress, props.tokenTransfers[0].tokenId).then((retrievedAsset: Asset): void => {
      setAsset(retrievedAsset);
    });
  }, [props.tokenTransfers]);

  React.useEffect((): void => {
    if (!props.tokenTransfers) {
      setAsset(null);
      return;
    }
    updateAsset();
  }, [props.tokenTransfers, updateAsset]);

  return (
    <React.Fragment>
      { !asset ? (
        <LoadingSpinner variant='light' />
      ) : (
        <NftCard
          label='Most Traded'
          title={asset.name}
          subtitle={`Sold ${props.tokenTransfers.length} times today`}
          imageUrl={asset.imageUrl || asset.collection.imageUrl}
          collectionImage={asset.collection.imageUrl}
          collectionTitle={asset.collection.name}
          collectionUrl={asset.collection.externalUrl ?? asset.collection.openSeaUrl}
          primaryButtonText='View Token'
          primaryButtonTarget={asset.openSeaUrl}
          secondaryButtonText='View Tx'
          secondaryButtonTarget={`https://etherscan.io/tx/${props.tokenTransfers[0].transactionHash}`}
          extraLabelVariants={['cardLabelSponsored']}
          extraLabelBoxVariants={['cardLabelBoxSponsored']}
        />
      )}
    </React.Fragment>
  );
};
