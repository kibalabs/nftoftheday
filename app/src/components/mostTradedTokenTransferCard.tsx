import React from 'react';

import { LoadingSpinner } from '@kibalabs/ui-react';

import { RegistryToken, TokenTransfer } from '../client/resources';
import { useGlobals } from '../globalsContext';
import { NftCard } from './nftCard';

export type MostTradedTokenTransferCardProps = {
  tokenTransfers: TokenTransfer[] | null;
}

export const MostTradedTokenTransferCard = (props: MostTradedTokenTransferCardProps): React.ReactElement => {
  const { notdClient } = useGlobals();
  const [asset, setAsset] = React.useState<RegistryToken | null>(null);

  const updateAsset = React.useCallback(async (): Promise<void> => {
    notdClient.retrieveRegistryToken(props.tokenTransfers[0].registryAddress, props.tokenTransfers[0].tokenId).then((registryToken: RegistryToken): void => {
      setAsset(registryToken);
    });
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
      { !props.tokenTransfers || !asset ? (
        <LoadingSpinner variant='light' />
      ) : (
        <NftCard
          label='Most Traded'
          title={asset.name}
          subtitle={`Traded ${props.tokenTransfers.length} times today`}
          imageUrl={asset.imageUrl || asset.collectionImageUrl || '/asset/icon.svg'}
          collectionImage={asset.collectionImageUrl}
          collectionTitle={asset.collectionName}
          collectionUrl={asset.collectionExternalUrl ?? asset.collectionOpenSeaUrl}
          primaryButtonText='View Token'
          primaryButtonTarget={asset.openSeaUrl}
          secondaryButtonText='View Tx'
          secondaryButtonTarget={`https://etherscan.io/tx/${props.tokenTransfers[0].transactionHash}`}
        />
      )}
    </React.Fragment>
  );
};
