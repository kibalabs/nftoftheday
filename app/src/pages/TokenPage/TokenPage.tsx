import React from 'react';

import { dateToString, truncateMiddle } from '@kibalabs/core';
import { useRouteParams } from '@kibalabs/core-react';
import { Alignment, Box, Button, Direction, Image, KibaIcon, LoadingSpinner, Media, PaddingSize, Spacing, Stack, Text } from '@kibalabs/ui-react';

import { Collection, CollectionToken, TokenTransfer } from '../../client/resources';
import { useGlobals } from '../../globalsContext';

const TOKEN_TRANSFER = new TokenTransfer(86323519, '0x4de7e4cbaac06e3a4fa55b8af17bf72d23f90d9d6ccace517928bd3dbb8fbf2b', '0x7Bd29408f11D2bFC23c34f18275bBf23bB716Bc7', '0xEC1B09e43100957D7623661F43364e65175eeC08', '0xEC1B09e43100957D7623661F43364e65175eeC08', '0', 6, 8999999, 98, 98889, 89889, '0x923dec2cb340dbd22a861070bb321752abec2416f24135bf473ce66fcb9479d4', new Date());
const owner = '0x48e41913F2099300900cfcbB139F121429D38F5d';

export const TokenPage = (): React.ReactElement => {
  const { notdClient } = useGlobals();
  const routeParams = useRouteParams();

  const [collectionToken, setCollectionToken] = React.useState<CollectionToken | undefined | null>(undefined);
  const [collection, setCollection] = React.useState<Collection | undefined | null>(undefined);
  const registryAddress = routeParams.registryAddress as string;
  const tokenId = routeParams.tokenId as string;
  const defaultImage = '/assets/icon.png';

  let imageUrl = collectionToken?.imageUrl || defaultImage;
  if (imageUrl?.startsWith('ipfs://')) {
    imageUrl = imageUrl.replace('ipfs://', 'https://ipfs.io/ipfs/');
  }
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

  const updateCollection = React.useCallback(async (): Promise<void> => {
    setCollection(undefined);
    notdClient.retrieveCollection(registryAddress).then((retrievedCollection: Collection): void => {
      setCollection(retrievedCollection);
    }).catch((error: unknown): void => {
      console.error(error);
      setCollection(null);
    });
  }, [notdClient, registryAddress]);

  React.useEffect((): void => {
    updateCollection();
  }, [updateCollection]);

  return (
    <Stack direction={Direction.Vertical} isFullWidth={true} isFullHeight={true} childAlignment={Alignment.Start} contentAlignment={Alignment.Start} isScrollableVertically={true}>
      {collectionToken === undefined ? (
        <LoadingSpinner />
      ) : collectionToken === null ? (
        <Text variant='error'>Collection Token failed to load</Text>
      ) : (
        <Stack direction={Direction.Horizontal} childAlignment={Alignment.Start} contentAlignment={Alignment.Start} shouldAddGutters={true}defaultGutter={PaddingSize.Wide2} padding={PaddingSize.Wide2}>
          <Box height='20rem' width='20rem' shouldClipContent={true}>
            <Media source={imageUrl} alternativeText='image' fitType='contain' />
          </Box>
          <Stack direction={Direction.Vertical} isFullHeight={true} childAlignment={Alignment.Start} contentAlignment={Alignment.Center}>
            <Text variant='header1'>{collectionToken.name}</Text>
            <Stack direction={Direction.Horizontal} childAlignment={Alignment.Center} contentAlignment={Alignment.Center} shouldAddGutters={true}>
              <Text>Owned By</Text>
              <Box variant='rounded-borderColored' shouldClipContent={true} height='20px' width='20px'>
                <Image source={`https://web3-images-api.kibalabs.com/v1/accounts/${owner}/image` || defaultImage} alternativeText='Avatar' />
                {/* TODO(Ajad-Abiola): implement Owned By: */}
              </Box>
              <Text>{truncateMiddle(owner, 10)}</Text>
            </Stack>
            <Text>{`Last Bought for Ξ${TOKEN_TRANSFER.value / 1000000000000000000.0} at ${dateToString(TOKEN_TRANSFER.blockDate, 'HH:mm:yyyy')}`}</Text>
            <Spacing variant={PaddingSize.Wide} />
            <Stack direction={Direction.Horizontal} childAlignment={Alignment.Center} contentAlignment={Alignment.Center} shouldAddGutters={true}>
              <Text>Part of</Text>
              <Box variant='rounded-borderColored' shouldClipContent={true} height='20px' width='20px'>
                <Image source= {collection?.imageUrl || defaultImage} alternativeText='Avatar' />
              </Box>
              <Text>{collection?.name}</Text>
            </Stack>
            <Stack direction={Direction.Horizontal} shouldAddGutters={true} contentAlignment={Alignment.Center} shouldWrapItems={true}>
              <Button variant='tertiary' text={'Opensea'} target={`https://opensea.io/collection/${collectionToken.registryAddress}/${tokenId}`} iconLeft={<KibaIcon iconId='ion-globe' />} />
              <Button variant='tertiary' text={'Lookrare'} target={`https://looksrare.org/collections/${collectionToken.registryAddress}/${tokenId}`} iconLeft={<KibaIcon iconId='ion-eye' />} />
            </Stack>
          </Stack>
        </Stack>
      )}
    </Stack>
  );
};
