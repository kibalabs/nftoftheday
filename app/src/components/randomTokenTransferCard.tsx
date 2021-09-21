import React from 'react';

import { dateToString } from '@kibalabs/core';
import { LoadingSpinner } from '@kibalabs/ui-react';

import { retrieveAsset } from '../assetUtil';
import { RegistryToken, TokenTransfer } from '../client/resources';
import { useGlobals } from '../globalsContext';
import { NftCard } from './nftCard';

export type RandomTokenTransferCardProps = {
  tokenTransfer: TokenTransfer | null;
}

export const RandomTokenTransferCard = (props: RandomTokenTransferCardProps): React.ReactElement => {
  const { requester } = useGlobals();
  const [asset, setAsset] = React.useState<RegistryToken | null>(null);
  const [isLoading, setIsLoading] = React.useState<boolean>(false);
  const [error, setError] = React.useState<Error | null>(null);

  const updateAsset = React.useCallback(async (): Promise<void> => {
    retrieveAsset(requester, props.tokenTransfer.registryAddress, props.tokenTransfer.tokenId).then((registryToken: RegistryToken): void => {
      setAsset(registryToken);
      setIsLoading(false);
    }).catch((e) => {
      setError(e);
      setIsLoading(false);
    });
  }, [requester, props.tokenTransfer]);

  React.useEffect((): void => {
    if (!props.tokenTransfer) {
      setAsset(null);
      return;
    }
    updateAsset();
  }, [props.tokenTransfer, updateAsset]);

  return (
    <React.Fragment>
      { !props.tokenTransfer || isLoading || !asset ? (
        <LoadingSpinner variant='light' />
      ) : (
        <NftCard
          nft={asset}
          label='Random'
          subtitle={`Sold at ${dateToString(props.tokenTransfer.blockDate, 'HH:mm')} for Ξ${props.tokenTransfer.value / 1000000000000000000.0}`}
          primaryButtonText='View Token'
          primaryButtonTarget={asset.openSeaUrl}
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
