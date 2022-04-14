import React from 'react';

import { Alignment, Direction, PaddingSize, Stack, Text } from '@kibalabs/ui-react';

import { useAccount } from '../../AccountContext';
import { CollectionToken } from '../../client/resources';
import { TokenCard } from '../../components/TokenCard';
import { useGlobals } from '../../globalsContext';

export const UserPage = (): React.ReactElement => {
  const account = useAccount();
  const { notdClient } = useGlobals();

  const [ownerTokens, setOwnerTokens] = React.useState<CollectionToken[] | undefined | null>(undefined);

  const refreshOwnerTokens = React.useCallback(async (): Promise<void> => {
    if (!account) {
      return;
    }
    setOwnerTokens(undefined);
    notdClient.getOwnerTokens(account.address).then((tokens: CollectionToken[]): void => {
      setOwnerTokens(tokens);
    }).catch((error: unknown): void => {
      console.error(error);
      setOwnerTokens(null);
    });
  }, [notdClient, account]);

  React.useEffect((): void => {
    refreshOwnerTokens();
  }, [refreshOwnerTokens]);

  return (
    <Stack direction={Direction.Vertical} isFullWidth={true} childAlignment={Alignment.Center} shouldAddGutters={true} paddingVertical={PaddingSize.Wide2} isScrollableHorizontally={true}>
      <Text variant='header3'>Your Tokens</Text>
      <Stack direction={Direction.Horizontal}contentAlignment={Alignment.Center} childAlignment={Alignment.Center} shouldAddGutters={true}>
        {ownerTokens && ownerTokens.map((ownerToken: CollectionToken, index: number) : React.ReactElement => (
          <TokenCard
            key={index}
            collectionToken={ownerToken}
            target={`/collections/${ownerToken.registryAddress}/tokens/${ownerToken.tokenId}`}
          />
        ))}
      </Stack>
    </Stack>
  );
};
