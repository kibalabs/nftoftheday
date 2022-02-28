import React from 'react';

import { dateToString } from '@kibalabs/core';
import { useInitialization, useNavigator, useRouteParams } from '@kibalabs/core-react';
import { Alignment, Box, Button, ContainingView, Direction, Image, KibaIcon, LayerContainer, Link, LoadingSpinner, PaddingSize, ResponsiveHidingView, ScreenSize, Spacing, Stack, Text } from '@kibalabs/ui-react';
import { ethers } from 'ethers';

import { useAccountId, useOnLinkAccountsClicked } from '../../AccountContext';
import { Collection, CollectionStatistics, CollectionToken, TokenTransfer } from '../../client/resources';
import { MetricView } from '../../components/MetricView';
import { TokenCard } from '../../components/TokenCard';
import { TruncateText } from '../../components/TruncateText';
import { useGlobals } from '../../globalsContext';

export const CollectionPage = (): React.ReactElement => {
  const { notdClient } = useGlobals();
  const [collection, setCollection] = React.useState<Collection | undefined | null>(undefined);
  const [collectionStatistics, setCollectionStatistics] = React.useState<CollectionStatistics | undefined | null>(undefined);
  const [recentSales, setRecentSales] = React.useState<TokenTransfer[] | undefined | null>(undefined);
  const [holdings, setHoldings] = React.useState<CollectionToken[] | undefined | null>(undefined);

  const routeParams = useRouteParams();
  const navigator = useNavigator();

  const address = routeParams.address as string;
  const ownerAddress = useAccountId();

  useInitialization((): void => {
    const checksumAddress = ethers.utils.getAddress(address);
    if (address !== checksumAddress) {
      navigator.navigateTo(`/collections/${checksumAddress}`);
    }
  });

  const updateCollection = React.useCallback(async (): Promise<void> => {
    setCollection(undefined);
    notdClient.retrieveCollection(address).then((retrievedCollection: Collection): void => {
      setCollection(retrievedCollection);
    }).catch((error: unknown): void => {
      console.error(error);
      setCollection(null);
    });
  }, [notdClient, address]);

  React.useEffect((): void => {
    updateCollection();
  }, [updateCollection]);

  const updateCollectionSales = React.useCallback(async (): Promise<void> => {
    setRecentSales(undefined);
    notdClient.getCollectionRecentSales(address).then((tokenTransfers: TokenTransfer[]): void => {
      setRecentSales(tokenTransfers);
    }).catch((error: unknown): void => {
      console.error(error);
      setRecentSales(null);
    });
  }, [notdClient, address]);

  React.useEffect((): void => {
    updateCollectionSales();
  }, [updateCollectionSales]);

  const updateCollectionStatistics = React.useCallback(async (): Promise<void> => {
    setCollectionStatistics(undefined);
    notdClient.getCollectionStatistics(address).then((retrievedCollectionStatistics: CollectionStatistics): void => {
      setCollectionStatistics(retrievedCollectionStatistics);
    }).catch((error: unknown): void => {
      console.error(error);
      setCollectionStatistics(null);
    });
  }, [notdClient, address]);

  React.useEffect((): void => {
    updateCollectionStatistics();
  }, [updateCollectionStatistics]);

  const getCollectionHoldings = React.useCallback(async (): Promise<void> => {
    setHoldings(undefined);
    notdClient.getCollectionHoldings(address, ownerAddress).then((tokenTransfers: CollectionToken[]): void => {
      setHoldings(tokenTransfers);
      console.log('we are', tokenTransfers)
    }).catch((error: unknown): void => {
      console.error(error);
      setHoldings(null);
    });
  }, [notdClient, address, ownerAddress]);

  React.useEffect((): void => {
    getCollectionHoldings();
  }, [getCollectionHoldings]);

  const onLinkAccountsClicked = useOnLinkAccountsClicked();

  const onConnectWalletClicked = async (): Promise<void> => {
    await onLinkAccountsClicked();
  };

  return (
    <Stack direction={Direction.Vertical} isFullWidth={true} isFullHeight={true} childAlignment={Alignment.Center} contentAlignment={Alignment.Start} isScrollableVertically={true}>
      {collection === undefined ? (
        <LoadingSpinner />
      ) : collection === null ? (
        <Text variant='error'>Collection failed to load</Text>
      ) : (
        <Stack direction={Direction.Vertical} isFullWidth={true} isFullHeight={true} childAlignment={Alignment.Center} contentAlignment={Alignment.Start}>
          <Box height='300px'>
            <LayerContainer>
              <LayerContainer.Layer isFullHeight={false} alignmentVertical={Alignment.Start}>
                {collection.bannerImageUrl && (
                  <Box height='230px' isFullWidth={true}>
                    <Image source={collection.bannerImageUrl} alternativeText='image' isFullWidth={true} fitType='cover' isFullHeight={true} />
                  </Box>
                )}
              </LayerContainer.Layer>
              <LayerContainer.Layer isFullHeight={false} isFullWidth={false} alignmentVertical={Alignment.End} alignmentHorizontal={Alignment.Center}>
                {collection.imageUrl && (
                  <Box variant='rounded-wideBorder' shouldClipContent={true} width='130px' height='130px'>
                    <Image source={collection.imageUrl} alternativeText='image' fitType='contain' />
                  </Box>
                )}
              </LayerContainer.Layer>
            </LayerContainer>
          </Box>
          <ContainingView>
            <Stack direction={Direction.Vertical} isFullWidth={true} childAlignment={Alignment.Center} paddingHorizontal={PaddingSize.Wide2} paddingBottom={PaddingSize.Wide2} paddingTop={PaddingSize.Default}>
              <Text variant='header1'>{collection.name}</Text>
              <Spacing variant={PaddingSize.Wide} />
              <Stack direction={Direction.Horizontal} shouldAddGutters={true} contentAlignment={Alignment.Center} childAlignment={Alignment.Center} isFullWidth={true} shouldWrapItems={true}>
                {collection.discordUrl && (
                  <Stack.Item baseSize='10em'>
                    <Button variant='tertiary' text= {'Discord'} iconLeft={<KibaIcon iconId='ion-logo-discord' />} target={collection.discordUrl} />
                  </Stack.Item>
                )}
                {collection.instagramUsername && (
                  <Stack.Item baseSize='10em'>
                    <Button variant='tertiary' text={'Instagram'} target={`https://instagram.com/${collection.instagramUsername}`} iconLeft={<KibaIcon iconId='feather-instagram' />} />
                  </Stack.Item>
                )}
                {collection.twitterUsername && (
                  <Stack.Item baseSize='10em'>
                    <Button variant='tertiary' text={'Twitter'} target={`https://instagram.com/${collection.twitterUsername}`} iconLeft={<KibaIcon iconId='feather-twitter' />} />
                  </Stack.Item>
                )}
                {collection.openseaSlug && (
                  <Stack.Item baseSize='10em'>
                    <Button variant='tertiary' text={'Opensea'} target={`https://opensea.io/collection/${collection.openseaSlug}`} iconLeft={<KibaIcon iconId='ion-cart' />} />
                  </Stack.Item>
                )}
                {collection.url && (
                  <Stack.Item baseSize='10em'>
                    <Button variant='tertiary' text={'Website'} target={`https://opensea.io/collection/${collection.url}`} iconLeft={<KibaIcon iconId='ion-globe' />} />
                  </Stack.Item>
                )}
              </Stack>
              <Spacing variant={PaddingSize.Wide2} />
              {collection.description && (
                <TruncateText
                  markdownText={collection.description}
                  maximumCharacters={300}
                />
              )}
              <Spacing variant={PaddingSize.Wide2} />
              {collectionStatistics === undefined ? (
                <LoadingSpinner />
              ) : collectionStatistics === null ? (
                <Text variant='error'>Collection statistics failed to load</Text>
              ) : (
                <Stack directionResponsive={{ base: Direction.Vertical, medium: Direction.Horizontal }} isFullWidth={true} childAlignment={Alignment.Center} contentAlignment={Alignment.Center} shouldAddGutters={true} defaultGutter={PaddingSize.Wide}>
                  <Stack direction={Direction.Horizontal} childAlignment={Alignment.Center} contentAlignment={Alignment.Center} shouldAddGutters={true} defaultGutter={PaddingSize.Wide}>
                    <MetricView name={'Items'} value={`${collectionStatistics.itemCount}`} />
                    <MetricView name={'Owners'} value={`${collectionStatistics.holderCount}`} />
                    <MetricView name={'Total Volume'} value={`${collectionStatistics.totalTradeVolume}`} />
                  </Stack>
                  <ResponsiveHidingView hiddenBelow={ScreenSize.Medium}>
                    <Box variant='divider' isFullHeight={true} width='1px' />
                  </ResponsiveHidingView>
                  <Stack direction={Direction.Horizontal} childAlignment={Alignment.Center} contentAlignment={Alignment.Center} shouldAddGutters={true} defaultGutter={PaddingSize.Wide}>
                    <MetricView name={'24h Low Sale'} value={`Ξ ${collectionStatistics.totalTradeVolume}`} />
                    <MetricView name={'24h High Sale'} value={`Ξ ${collectionStatistics.highestSaleLast24Hours}`} />
                    <MetricView name={'24h Volume'} value={`Ξ ${collectionStatistics.tradeVolume24Hours}`} />
                  </Stack>
                </Stack>
              )}
              { ownerAddress ? (
                <Stack direction={Direction.Vertical} isFullWidth={true} childAlignment={Alignment.Start} shouldAddGutters={true} paddingVertical={PaddingSize.Wide2} isScrollableHorizontally={true}>
                  <Text variant='header3'>{`Your Holdings (${holdings?.length})`}</Text>
                  <Stack direction={Direction.Horizontal}contentAlignment={Alignment.Center} childAlignment={Alignment.Center} shouldAddGutters={true}>
                    {holdings && holdings.length !== 0 ? holdings.map((holding: CollectionToken, index: number) : React.ReactElement => (
                      <TokenCard
                        key={index}
                        collectionToken={holding}
                        // subtitle={`Bought at ${dateToString(holding.blockDate, 'HH:mm')} for Ξ${holding.value / 1000000000000000000.0}`}
                        target={`/collections/${holding.registryAddress}/tokens/${holding.tokenId}`}
                      />
                    ))
                      : <Text>No Holdings</Text>
                    }
                  </Stack>
                </Stack>
              ) : (
                <Stack direction={Direction.Horizontal} shouldAddGutters={true}>
                  <Link text='Connect your wallet' onClicked={onConnectWalletClicked} />
                  <Text>to show your holdings and watchlist.</Text>
                </Stack>
              )}
              <Stack direction={Direction.Vertical} isFullWidth={true} childAlignment={Alignment.Start} shouldAddGutters={true} paddingVertical={PaddingSize.Wide2} isScrollableHorizontally={true}>
                <Text variant='header3'>Recent Sales</Text>
                <Stack direction={Direction.Horizontal}contentAlignment={Alignment.Center} childAlignment={Alignment.Center} shouldAddGutters={true}>
                  {recentSales && recentSales.length !== 0 ? recentSales.map((recentSale: TokenTransfer, index: number) : React.ReactElement => (
                    <TokenCard
                      key={index}
                      collectionToken={recentSale.token}
                      subtitle={`Sold at ${dateToString(recentSale.blockDate, 'HH:mm')} for Ξ${recentSale.value / 1000000000000000000.0}`}
                      target={`/collections/${recentSale.registryAddress}/tokens/${recentSale.tokenId}`}
                    />
                  ))
                    : <Text>No recent sales</Text>
                  }
                </Stack>
              </Stack>
            </Stack>
          </ContainingView>
        </Stack>
      )}
    </Stack>
  );
};
