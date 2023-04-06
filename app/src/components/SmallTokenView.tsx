import React from 'react';

import { getClassName, truncateEnd } from '@kibalabs/core';
import { Alignment, Direction, Image, LinkBase, Stack, Text } from '@kibalabs/ui-react';

import { CollectionToken } from '../client/resources';
import { useGlobals } from '../globalsContext';

export interface SmallTokenViewProps {
  id?: string;
  className?: string;
  registryAddress: string;
  tokenId: string;
}

export const SmallTokenView = (props: SmallTokenViewProps): React.ReactElement => {
  const { notdClient } = useGlobals();
  const [token, setToken] = React.useState<CollectionToken | undefined | null>(undefined);

  const updateToken = React.useCallback(async (): Promise<void> => {
    notdClient.getCollectionToken(props.registryAddress, props.tokenId).then((retrievedToken: CollectionToken): void => {
      setToken(retrievedToken);
    });
  }, [notdClient, props.registryAddress, props.tokenId]);

  React.useEffect((): void => {
    updateToken();
  }, [updateToken]);

  return (
    <Stack
      id={props.id}
      className={getClassName(props.className, SmallTokenView.displayName)}
      key={`${props.registryAddress}-${props.tokenId}`}
      direction={Direction.Horizontal}
      isFullWidth={false}
      isFullHeight={true}
      childAlignment={Alignment.Center}
      contentAlignment={Alignment.Start}
      shouldAddGutters={true}
    >
      <Image source={token?.imageUrl || ''} alternativeText='' height='1em' width='1em' fitType='contain' />
      <Text>{truncateEnd(token?.name || '', 10)}</Text>
    </Stack>
  );
};
SmallTokenView.displayName = 'SmallTokenView';

export interface SmallTokenViewLinkProps extends SmallTokenViewProps {
  target: string;
}

export const SmallTokenViewLink = (props: SmallTokenViewLinkProps): React.ReactElement => {
  return (
    <LinkBase target={props.target} key={`${props.registryAddress}-${props.tokenId}`} isFullWidth={false}>
      <SmallTokenView {...props} className={getClassName(props.className, SmallTokenViewLink.displayName)} />
    </LinkBase>
  );
};
SmallTokenViewLink.displayName = 'SmallTokenViewLink';
