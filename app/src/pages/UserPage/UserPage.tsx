import React from 'react';

import { truncateMiddle } from '@kibalabs/core';
import { Alignment, Box, Direction, Image, PaddingSize, Spacing, Stack, Text } from '@kibalabs/ui-react';

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
      { account?.address && (
        <Stack direction={Direction.Horizontal} childAlignment={Alignment.Center} contentAlignment={Alignment.Center} shouldAddGutters={true}>
          <Box variant='rounded' shouldClipContent={true} height='40px' width='40px'>
            <Image source={`https://web3-images-api.kibalabs.com/v1/accounts/${account?.address}/image`} alternativeText='Avatar' />
          </Box>
          <Text variant='header2'>{truncateMiddle(account?.address, 15)}</Text>
        </Stack>
      )}
      <Spacing variant={PaddingSize.Wide} />
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
