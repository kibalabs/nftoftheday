import React from 'react';

import { dateToString, isToday } from '@kibalabs/core';
import { useInitialization, useNavigator, useStringRouteParam } from '@kibalabs/core-react';
import { Alignment, Box, Button, ContainingView, Direction, KibaIcon, LoadingSpinner, Media, PaddingSize, ResponsiveTextAlignmentView, Spacing, Stack, Text, TextAlignment } from '@kibalabs/ui-react';
import { ethers } from 'ethers';
import { toast } from 'react-toastify';

import { useAccount } from '../../AccountContext';
import { Collection, CollectionToken, TokenAttribute, TokenTransfer } from '../../client/resources';
import { Account } from '../../components/Account';
import { CollectionView } from '../../components/CollectionView';
import { MetricView } from '../../components/MetricView';
import { TokenSaleRow } from '../../components/TokenSaleRow';
import { useGlobals } from '../../globalsContext';

const RECENT_SALES_PAGE_SIZE = 10;

export const TokenPage = (): React.ReactElement => {
  const { notdClient } = useGlobals();
  const account = useAccount();
  const registryAddress = useStringRouteParam('registryAddress');
  const tokenId = useStringRouteParam('tokenId');
  const navigator = useNavigator();
  const [isRefreshClicked, setIsRefreshClicked] = React.useState<boolean>(false);
  const [collectionToken, setCollectionToken] = React.useState<CollectionToken | undefined | null>(undefined);
  const [collection, setCollection] = React.useState<Collection | undefined | null>(undefined);
  const [tokenSales, setTokenSales] = React.useState<TokenTransfer[] | undefined | null>(undefined);
  const [showLoadMore, setShowLoadMore] = React.useState<boolean>(false);
  const defaultImage = '/assets/icon.png';

  let imageUrl = collectionToken?.imageUrl || defaultImage;
  if (imageUrl?.startsWith('ipfs://')) {
    imageUrl = imageUrl.replace('ipfs://', 'https://pablo-images.kibalabs.com/v1/ipfs/');
  }

  useInitialization((): void => {
    const checksumAddress = ethers.utils.getAddress(registryAddress);
    if (registryAddress !== checksumAddress) {
      navigator.navigateTo(`/collections/${checksumAddress}/tokens/${tokenId}`);
    }
  });

  const updateCollectionToken = React.useCallback(async (): Promise<void> => {
    setCollectionToken(undefined);
    notdClient.getCollectionToken(registryAddress, tokenId).then((retrievedCollectionToken: CollectionToken): void => {
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
    notdClient.getCollection(registryAddress).then((retrievedCollection: Collection): void => {
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

  const updateToken = (): void => {
    if (!account) {
      return;
    }
    notdClient.updateToken(registryAddress, tokenId, account.address).then((): void => {
      toast('We\'ve queued your request');
    }).catch((error: unknown): void => {
      console.error(error);
    });
  };

  const onRefreshMetadataClicked = (): void => {
    updateToken();
    setIsRefreshClicked(true);
  };

  const getTokenDateString = (tokenDate: Date): string => {
    if (tokenDate !== null) {
      if (isToday(tokenDate)) {
        return dateToString(tokenDate, 'HH:mm');
      }
      return dateToString(tokenDate, 'dd-MMM-yyyy');
    }
    return '';
  };

  return (
    <Stack direction={Direction.Vertical} isFullWidth={true} isFullHeight={true} childAlignment={Alignment.Center} contentAlignment={Alignment.Start}>
      {collectionToken === undefined ? (
        <LoadingSpinner />
      ) : collectionToken === null ? (
        <Text variant='error'>Collection Token failed to load</Text>
      ) : (
        <ContainingView>
          <Stack directionResponsive={{ base: Direction.Vertical, medium: Direction.Horizontal }} isFullWidth={true} childAlignment={Alignment.Center} contentAlignment={Alignment.Center} shouldAddGutters={true} defaultGutter={PaddingSize.Wide2} padding={PaddingSize.Wide2}>
            <Box height='20rem' width='20rem' shouldClipContent={true}>
              <Media source={imageUrl} alternativeText='image' fitType='contain' />
            </Box>
            <Stack.Item growthFactor={1} shrinkFactor={1}>
              <ResponsiveTextAlignmentView alignmentResponsive={{ base: TextAlignment.Center, medium: TextAlignment.Left }}>
                <Stack direction={Direction.Vertical} childAlignmentResponsive={{ base: Alignment.Center, medium: Alignment.Start }} contentAlignmentResponsive={{ base: Alignment.Center, medium: Alignment.Start }} padding={PaddingSize.Wide}>
                  <Text variant='header1'>{collectionToken.name}</Text>
                  {tokenSales && tokenSales.length > 0 && (
                    <Stack direction={Direction.Vertical} childAlignment={Alignment.Start} contentAlignment={Alignment.Center}>
                      <Stack direction={Direction.Horizontal} childAlignment={Alignment.Start} contentAlignment={Alignment.Center} shouldAddGutters={true}>
                        <Text>Owned By</Text>
                        <Account
                          accountId={tokenSales[0].toAddress}
                          target={`/accounts/${tokenSales[0].toAddress}`}
                        />
                      </Stack>
                      <Text>{`Last Bought for Ξ${tokenSales[0].value / 1000000000000000000.0} on ${getTokenDateString(tokenSales[0].blockDate)}`}</Text>
                    </Stack>
                  )}
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
                  {account?.address && !isRefreshClicked && (
                    <Button variant='tertiary' text= {'Refresh Metadata'} iconLeft={<KibaIcon iconId='ion-refresh-circle-outline' />} onClicked={onRefreshMetadataClicked} />
                  )}
                </Stack>
              </ResponsiveTextAlignmentView>
            </Stack.Item>
          </Stack>
          <Stack direction={Direction.Horizontal} isFullWidth={true} childAlignment={Alignment.Center} contentAlignment={Alignment.Center} shouldAddGutters={true} shouldWrapItems={true} padding={PaddingSize.Wide}>
            {collectionToken?.attributes.map((tokenAttribute: TokenAttribute, index: number) : React.ReactElement => (
              <MetricView key={index} name={tokenAttribute.traitType} value={tokenAttribute.value} />
            ))}
          </Stack>
          <Stack directionResponsive={{ base: Direction.Vertical, medium: Direction.Horizontal }} shouldWrapItems={true} isFullWidth={true} childAlignment={Alignment.Center} contentAlignment={Alignment.Center}>
            <Text variant='header3'>Sales history</Text>
            <Stack direction={Direction.Vertical} isFullWidth={true} childAlignment={Alignment.Center} contentAlignment={Alignment.Center} shouldWrapItems={true}>
              {tokenSales === undefined ? (
                <LoadingSpinner />
              ) : tokenSales === null ? (
                <Text variant='error'>Token Sale failed to load</Text>
              ) : tokenSales && tokenSales.length !== 0 ? (
                tokenSales.map((tokenTransfer: TokenTransfer, index: number) : React.ReactElement => (
                  <TokenSaleRow
                    tokenTransfer={tokenTransfer}
                    key={index}
                  />
                ))
              ) : (
                <Text>No recent sales</Text>
              )}
            </Stack>
            { showLoadMore && (
              <Button variant='small' text={'load more'} onClicked={onLoadMoreClicked} />
            )}
          </Stack>
        </ContainingView>
      )}
    </Stack>
  );
};
