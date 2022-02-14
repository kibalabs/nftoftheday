import React from 'react';

import { useRouteParams } from '@kibalabs/core-react';
import { Alignment, Direction, PaddingSize, Stack } from '@kibalabs/ui-react';

import { CollectionToken, TokenAttribute } from '../../client/resources';
import { MetricView } from '../../components/MetricView';
import { useGlobals } from '../../globalsContext';


export const TokenPage = (): React.ReactElement => {
  const { notdClient } = useGlobals();
  const routeParams = useRouteParams();
  const registryAddress = routeParams.registryAddress as string;
  const tokenId = routeParams.tokenId as string;

  const [collectionToken, setCollectionToken] = React.useState<CollectionToken | undefined | null>(undefined);

  const updateCollectionToken = React.useCallback(async (): Promise<void> => {
    setCollectionToken(undefined);
    notdClient.retrieveCollectionToken(registryAddress, tokenId).then((retrievedCollectionToken: CollectionToken): void => {
      setCollectionToken(retrievedCollectionToken);
    }).catch((error: unknown): void => {
      console.error(error);
      setCollectionToken(null);
    });
  }, [notdClient, registryAddress, tokenId]);

  React.useEffect((): void => {
    updateCollectionToken();
  }, [updateCollectionToken]);
  return (
    <Stack direction={Direction.Horizontal} isFullWidth={true} childAlignment={Alignment.Center} contentAlignment={Alignment.Center} shouldAddGutters={true} defaultGutter={PaddingSize.Wide1} shouldWrapItems={true}>
      {collectionToken?.attributes.map((tokenAttribute: TokenAttribute, index: number) : React.ReactElement => (
        <MetricView key={index} name={tokenAttribute.traitType} value={tokenAttribute.value} />
      ))}
    </Stack>
  );
};
