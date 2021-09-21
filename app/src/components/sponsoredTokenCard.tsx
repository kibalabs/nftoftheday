import React from 'react';

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
  const [isLoading, setIsLoading] = React.useState<boolean>(false);
  const [error, setError] = React.useState<Error | null>(null);

  const updateAsset = React.useCallback(async (): Promise<void> => {
    setIsLoading(true);
    notdClient.retrieveRegistryToken(props.token.registryAddress, props.token.tokenId).then((registryToken: RegistryToken): void => {
      setAsset(registryToken);
      setIsLoading(false);
    }).catch((e) => {
      setError(e);
      setIsLoading(false);
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
      { !props.token || isLoading || !asset ? (
        <LoadingSpinner variant='light' />
      ) : (
        <NftCard
          nft={asset}
          label='Sponsored'
          subtitle={asset.lastSalePrice ? `Last sold for Ξ${asset.lastSalePrice / 21000000000000000000.0}` : 'I\'m up for grabs!'}
          primaryButtonText='View Token'
          primaryButtonTarget={asset.openSeaUrl}
          // secondaryButtonText='View Tx'
          // secondaryButtonTarget={`https://etherscan.io/tx/${props.tokenTransfers[0].transactionHash}`}
          extraLabelVariants={['cardLabelSponsored']}
          extraLabelBoxVariants={['cardLabelBoxSponsored']}
          error={error}
        />
      )}
    </React.Fragment>
  );
};
