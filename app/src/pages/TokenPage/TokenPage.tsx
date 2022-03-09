import React from 'react';

import { dateToString, isToday } from '@kibalabs/core';
import { useInitialization, useNavigator, useRouteParams } from '@kibalabs/core-react';
import { Alignment, Box, Button, ContainingView, Direction, KibaIcon, LoadingSpinner, Media, PaddingSize, ResponsiveHidingView, ScreenSize, Spacing, Stack, Text, TextAlignment } from '@kibalabs/ui-react';
import { ethers } from 'ethers';

import { Collection, CollectionToken, TokenAttribute, TokenTransfer } from '../../client/resources';
import { Account } from '../../components/Account';
import { CollectionView } from '../../components/CollectionView';
import { MetricView } from '../../components/MetricView';
import { TokenSaleRow } from '../../components/TokenSaleRow';
import { useGlobals } from '../../globalsContext';

const TOKEN_DATE = new Date('2022-03-08T03:23:35');
const COLLECTION = new Collection('0x1A257a5b37AC944DeF62b28cC5ec6c437178178c', '38123', 'Robo Ooga #38123', 'https://mekaapes.s3.amazonaws.com/images/38123.png', '', '', '', '', '', '');
const COLLECTIONTOKEN = new CollectionToken('0x1A257a5b37AC944DeF62b28cC5ec6c437178178c', '38123', 'Robo Ooga #38123', 'https://mekaapes.s3.amazonaws.com/images/38123.png', '', []);
const TOKEN_TRANSFER = new TokenTransfer(86323519, '0x4de7e4cbaac06e3a4fa55b8af17bf72d23f90d9d6ccace517928bd3dbb8fbf2b', '0x7Bd29408f11D2bFC23c34f18275bBf23bB716Bc7', '0xEC1B09e43100957D7623661F43364e65175eeC08', '0xEC1B09e43100957D7623661F43364e65175eeC08', '0', 650000000000000000000, 6500000, 98, 98889, 89889, '0x923dec2cb340dbd22a861070bb321752abec2416f24135bf473ce66fcb9479d4', TOKEN_DATE, COLLECTIONTOKEN, COLLECTION);
const owner = '0x48e41913F2099300900cfcbB139F121429D38F5d';
const RECENT_SALES_PAGE_SIZE = 10;
const tokenDate = TOKEN_TRANSFER.blockDate;

const getTokenDateString = (): string => {
  if (tokenDate !== null) {
    if (isToday(tokenDate)) {
      return dateToString(tokenDate, 'HH:mm');
    }
    return dateToString(tokenDate, 'dd-MMM-yyyy');
  }
  return '';
};

export const TokenPage = (): React.ReactElement => {
  const { notdClient } = useGlobals();
  const routeParams = useRouteParams();
  const navigator = useNavigator();

  const [collectionToken, setCollectionToken] = React.useState<CollectionToken | undefined | null>(undefined);
  const [collection, setCollection] = React.useState<Collection | undefined | null>(undefined);
  const [tokenSales, setTokenSales] = React.useState<TokenTransfer[] | undefined | null>(undefined);
  const [showLoadMore, setShowLoadMore] = React.useState<boolean>(false);
  const registryAddress = routeParams.registryAddress as string;
  const tokenId = routeParams.tokenId as string;
  const defaultImage = '/assets/icon.png';

  let imageUrl = collectionToken?.imageUrl || defaultImage;
  if (imageUrl?.startsWith('ipfs://')) {
    imageUrl = imageUrl.replace('ipfs://', 'https://ipfs.io/ipfs/');
  }

  useInitialization((): void => {
    const checksumAddress = ethers.utils.getAddress(registryAddress);
    if (registryAddress !== checksumAddress) {
      navigator.navigateTo(`/collections/${checksumAddress}/tokens/${tokenId}`);
    }
  });

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

  const updateTokenSales = React.useCallback(async (): Promise<void> => {
    setTokenSales(undefined);
    notdClient.getTokenRecentSales(registryAddress, tokenId, RECENT_SALES_PAGE_SIZE).then((tokenTransfers: TokenTransfer[]): void => {
      setTokenSales(tokenTransfers);
      setShowLoadMore(tokenTransfers.length === RECENT_SALES_PAGE_SIZE);
    }).catch((error: unknown): void => {
      console.error(error);
      setTokenSales(null);
    });
  }, [notdClient, registryAddress, tokenId]);

  React.useEffect((): void => {
    updateTokenSales();
  }, [updateTokenSales]);

  const onLoadMoreClicked = (): void => {
    const tokenSalesCount = tokenSales ? tokenSales.length : 0;
    notdClient.getTokenRecentSales(registryAddress, tokenId, RECENT_SALES_PAGE_SIZE, tokenSalesCount).then((tokenTransfers: TokenTransfer[]): void => {
      setTokenSales((prevTokenSales) => [...(prevTokenSales || []), ...tokenTransfers]);
      setShowLoadMore(tokenTransfers.length === RECENT_SALES_PAGE_SIZE);
    }).catch((error: unknown): void => {
      console.error(error);
    });
  };

  return (
    <Stack direction={ Direction.Vertical} isFullHeight={true} childAlignment={Alignment.Start} contentAlignment={Alignment.Start} isScrollableVertically={true}>
      {collectionToken === undefined ? (
        <LoadingSpinner />
      ) : collectionToken === null ? (
        <Text variant='error'>Collection Token failed to load</Text>
      ) : (
        <ContainingView>
          <Stack directionResponsive={{ base: Direction.Vertical, medium: Direction.Horizontal }} childAlignment={Alignment.Center} contentAlignment={Alignment.Center} padding={PaddingSize.Wide2}>
            <Box height='20rem' width='20rem' shouldClipContent={true}>
              <Media source={imageUrl} alternativeText='image' fitType='contain' />
            </Box>
            <ResponsiveHidingView hiddenBelow={ScreenSize.Medium}>
              <Stack direction={Direction.Vertical} childAlignment={Alignment.Start} contentAlignment={Alignment.Start} padding={PaddingSize.Wide}>
                <Text variant='header1'>{collectionToken.name}</Text>
                <Stack direction={Direction.Horizontal} childAlignment={Alignment.Start} contentAlignment={Alignment.Center} shouldAddGutters={true}>
                  <Text>Owned By</Text>
                  <Account accountId={owner} />
                </Stack>
                <Text>{`Last Bought for Ξ${TOKEN_TRANSFER.value / 1000000000000000000.0} on ${getTokenDateString()}`}</Text>
                <Spacing variant={PaddingSize.Wide} />
                {collection === undefined ? (
                  <LoadingSpinner />
                ) : collection === null ? (
                  <Text variant='error'>Collection failed to load</Text>
                ) : (
                  <Stack direction={Direction.Horizontal} childAlignment={Alignment.Center} contentAlignment={Alignment.Center} shouldAddGutters={true}>
                    <Text>Part of</Text>
                    <CollectionView
                      collection={collection}
                      target={`/collections/${collection.address}`}
                    />
                  </Stack>
                )}
                <Stack direction={Direction.Horizontal} shouldAddGutters={true} contentAlignment={Alignment.Center} shouldWrapItems={true}>
                  <Button variant='tertiary' text={'Opensea'} target={`https://opensea.io/assets/${collectionToken.registryAddress}/${tokenId}`} iconLeft={<KibaIcon iconId='ion-globe' />} />
                  <Button variant='tertiary' text={'Looksrare'} target={`https://looksrare.org/collections/${collectionToken.registryAddress}/${tokenId}`} iconLeft={<KibaIcon iconId='ion-eye' />} />
                </Stack>
              </Stack>
            </ResponsiveHidingView>
            <ResponsiveHidingView hiddenAbove={ScreenSize.Medium}>
              <Stack direction={Direction.Vertical} childAlignment={Alignment.Center} contentAlignment={Alignment.Center}>
                <Text alignment={TextAlignment.Center} variant='header1'>{collectionToken.name}</Text>
                <Stack direction={Direction.Horizontal} childAlignment={Alignment.Center} contentAlignment={Alignment.Center}>
                  <Text>Owned By</Text>
                  <Account accountId={owner} />
                </Stack>
                <Text>{`Last Bought for Ξ${TOKEN_TRANSFER.value / 1000000000000000000.0} on ${getTokenDateString()}`}</Text>
                {collection === undefined ? (
                  <LoadingSpinner />
                ) : collection === null ? (
                  <Text variant='error'>Collection failed to load</Text>
                ) : (
                  <Stack direction={Direction.Horizontal} childAlignment={Alignment.Center} contentAlignment={Alignment.Center} shouldAddGutters={true}>
                    <Text>Part of</Text>
                    <CollectionView
                      collection={collection}
                      target={`/collections/${collection.address}`}
                    />
                  </Stack>
                )}
                <Stack direction={Direction.Horizontal} shouldAddGutters={true} contentAlignment={Alignment.Center} shouldWrapItems={true}>
                  <Button variant='tertiary' text={'Opensea'} target={`https://opensea.io/collection/${collectionToken.registryAddress}/${tokenId}`} iconLeft={<KibaIcon iconId='ion-globe' />} />
                  <Button variant='tertiary' text={'Looksrare'} target={`https://looksrare.org/collections/${collectionToken.registryAddress}/${tokenId}`} iconLeft={<KibaIcon iconId='ion-eye' />} />
                </Stack>
              </Stack>
            </ResponsiveHidingView>
          </Stack>
          <Stack direction={Direction.Horizontal} isFullWidth={true} childAlignment={Alignment.Center} contentAlignment={Alignment.Center} shouldAddGutters={true} shouldWrapItems={true} padding={PaddingSize.Wide}>
            {collectionToken?.attributes.map((tokenAttribute: TokenAttribute, index: number) : React.ReactElement => (
              <MetricView key={index} name={tokenAttribute.traitType} value={tokenAttribute.value} />
            ))}
          </Stack>
          <Stack directionResponsive={{ base: Direction.Vertical, medium: Direction.Horizontal }} shouldWrapItems={true} isFullWidth={true} childAlignment={Alignment.Center} contentAlignment={Alignment.Center}>
            <Text variant='header3'>Sales history</Text>
            {tokenSales && tokenSales.map((tokenTransfer: TokenTransfer, index: number) : React.ReactElement => (
              <TokenSaleRow
                tokenTransfer={tokenTransfer}
                key={index}
              />
            ))}
            { showLoadMore && (
              <Button variant='small' text={'load more'} onClicked={onLoadMoreClicked} />
            )}
          </Stack>
        </ContainingView>
      )}
    </Stack>
  );
};
