import React from 'react';

import { dateToString } from '@kibalabs/core';
import { useInitialization, useIntegerUrlQueryState, useNavigator, useStringRouteParam } from '@kibalabs/core-react';
import { Alignment, Box, Button, ContainingView, Direction, Image, KibaIcon, LayerContainer, Link, LoadingSpinner, PaddingSize, ResponsiveHidingView, ScreenSize, Spacing, Stack, Text, TextAlignment, useColors } from '@kibalabs/ui-react';
import { BigNumber, ethers } from 'ethers';
import { toast } from 'react-toastify';
import { Area, AreaChart, CartesianGrid, Legend, ResponsiveContainer as RechartsContainer, Tooltip, XAxis, YAxis } from 'recharts';

import { useAccount, useOnLinkAccountsClicked } from '../../AccountContext';
import { Collection, CollectionActivity, CollectionStatistics, CollectionToken, TokenTransfer } from '../../client/resources';
import { MetricView } from '../../components/MetricView';
import { TokenCard } from '../../components/TokenCard';
import { TruncateText } from '../../components/TruncateText';
import { useGlobals } from '../../globalsContext';

export const CollectionPage = (): React.ReactElement => {
  const { notdClient } = useGlobals();
  const [collection, setCollection] = React.useState<Collection | undefined | null>(undefined);
  const [collectionStatistics, setCollectionStatistics] = React.useState<CollectionStatistics | undefined | null>(undefined);
  const [collectionActivities, setCollectionActivities] = React.useState<CollectionActivity[] | undefined | null>(undefined);
  const [chartData, setChartData] = React.useState< any[] | undefined >(undefined);
  const [recentSales, setRecentSales] = React.useState<TokenTransfer[] | undefined | null>(undefined);
  const [isRefreshClicked, setIsRefreshClicked] = React.useState<boolean>(false);
  const [shouldRefreshAllTokens, _] = useIntegerUrlQueryState('shouldRefreshAllTokens');
  const [holdings, setHoldings] = React.useState<CollectionToken[] | undefined | null>(undefined);
  const address = useStringRouteParam('address');
  const navigator = useNavigator();
  const account = useAccount();
  const onLinkAccountsClicked = useOnLinkAccountsClicked();
  const bannerImageUrl = collection?.bannerImageUrl || '/assets/black_banner.png';
  const imageUrl = collection?.imageUrl || '/assets/icon.png';

  useInitialization((): void => {
    const checksumAddress = ethers.utils.getAddress(address);
    if (address !== checksumAddress) {
      navigator.navigateTo(`/collections/${checksumAddress}`);
    }
  });

  const updateCollection = React.useCallback(async (): Promise<void> => {
    setCollection(undefined);
    notdClient.getCollection(address).then((retrievedCollection: Collection): void => {
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
    if (!account) {
      return;
    }
    notdClient.getCollectionHoldings(address, account.address).then((tokenTransfers: CollectionToken[]): void => {
      setHoldings(tokenTransfers);
    }).catch((error: unknown): void => {
      console.error(error);
      setHoldings(null);
    });
  }, [notdClient, address, account]);

  React.useEffect((): void => {
    getCollectionHoldings();
  }, [getCollectionHoldings]);

  const onConnectWalletClicked = async (): Promise<void> => {
    await onLinkAccountsClicked();
  };

  const refreshMetadata = (): void => {
    if (!account) {
      return;
    }
    notdClient.updateCollection(address, account.address).then((): void => {
      toast('We\'ve queued your request');
    }).catch((error: unknown): void => {
      console.error(error);
    });
  };

  const onRefreshMetadataClicked = (): void => {
    refreshMetadata();
    setIsRefreshClicked(true);
  };

  React.useEffect((): void => {
    if (shouldRefreshAllTokens) {
      if (!account) {
        return;
      }
      notdClient.updateCollectionTokens(address, account.address).then((): void => {
        toast('We\'ve queued your request');
      }).catch((error: unknown): void => {
        console.error(error);
      });
    }
  }, [notdClient, account, address, shouldRefreshAllTokens]);

  const updateCollectionActivities = React.useCallback(async (): Promise<void> => {
    setCollectionActivities(undefined);
    notdClient.getCollectionActivities(address).then((retrievedCollectionActivities: CollectionActivity[]): void => {
      setCollectionActivities(retrievedCollectionActivities);
      const data = retrievedCollectionActivities.map((formattedValues) => ({
        date: dateToString(formattedValues.date, 'dd MMMM yyyy'),
        maximumValue: formatEtherValue(formattedValues.maximumValue),
        minimumValue: formatEtherValue(formattedValues.minimumValue),
        totalValue: formatEtherValue(formattedValues.averageValue),
        transferCount: formatEtherValue(formattedValues.transferCount),
        averageValue: formatEtherValue(formattedValues.averageValue),
        saleCount: formatEtherValue(formattedValues.saleCount),
      }));
      setChartData(data);
    }).catch((error: unknown): void => {
      console.error(error);
      setCollectionActivities(null);
    });
  }, [notdClient, address]);
  React.useEffect((): void => {
    updateCollectionActivities();
  }, [updateCollectionActivities]);

  const colors = useColors();
  const renderColorfulLegendText = (value: string) => {
    return <span style={{ color: '#FFFFFF' }}>{value}</span>;
  };

  let formatEtherValue = (value: BigNumber) => {
    return ethers.utils.formatEther(value);
  };

  const renderCustomToolTip = (data: any) => {
    if (!data.payload || data.payload.length === 0) return null;
    const tooltipData = data.payload[0].payload;
    return (
      <Box variant='card'>
        <Stack direction={Direction.Vertical} isFullWidth={true} isFullHeight={true} childAlignment={Alignment.Start} contentAlignment={Alignment.Start} padding={PaddingSize.Wide1}>
          <Text>{`Date:${tooltipData.date}`}</Text>
          <Text>{`SaleCount:${tooltipData.saleCount}`}</Text>
          <Text>{`AverageValue:${tooltipData.averageValue}`}</Text>
        </Stack>
      </Box>
    );
  };

  return (
    <Stack direction={Direction.Vertical} isFullWidth={true} isFullHeight={true} childAlignment={Alignment.Center} contentAlignment={Alignment.Start}>
      {collection === undefined ? (
        <LoadingSpinner />
      ) : collection === null ? (
        <Text variant='error'>Collection failed to load</Text>
      ) : (
        <Stack direction={Direction.Vertical} isFullWidth={true} isFullHeight={true} childAlignment={Alignment.Center} contentAlignment={Alignment.Start}>
          <Box height='300px'>
            <LayerContainer>
              <LayerContainer.Layer isFullHeight={false} alignmentVertical={Alignment.Start}>
                {bannerImageUrl && (
                  <Box height='230px' isFullWidth={true}>
                    <Image source={bannerImageUrl} alternativeText='image' isFullWidth={true} fitType='cover' isFullHeight={true} />
                  </Box>
                )}
              </LayerContainer.Layer>
              <LayerContainer.Layer isFullHeight={false} isFullWidth={false} alignmentVertical={Alignment.End} alignmentHorizontal={Alignment.Center}>
                {imageUrl && (
                  <Box variant='rounded-wideBorder' shouldClipContent={true} width='130px' height='130px'>
                    <Image source={imageUrl} alternativeText='image' fitType='contain' />
                  </Box>
                )}
              </LayerContainer.Layer>
            </LayerContainer>
          </Box>
          <ContainingView>
            <Stack direction={Direction.Vertical} isFullWidth={true} childAlignment={Alignment.Center} paddingHorizontal={PaddingSize.Wide2} paddingBottom={PaddingSize.Wide2} paddingTop={PaddingSize.Default}>
              <Text variant='header1' alignment={TextAlignment.Center}>{collection.name}</Text>
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
                    <Button variant='tertiary' text={'Twitter'} target={`https://twitter.com/${collection.twitterUsername}`} iconLeft={<KibaIcon iconId='feather-twitter' />} />
                  </Stack.Item>
                )}
                {collection.openseaSlug && (
                  <Stack.Item baseSize='10em'>
                    <Button variant='tertiary' text={'Opensea'} target={`https://opensea.io/collection/${collection.openseaSlug}`} iconLeft={<KibaIcon iconId='ion-cart' />} />
                  </Stack.Item>
                )}
                {collection.url && (
                  <Stack.Item baseSize='10em'>
                    <Button variant='tertiary' text={'Website'} target={collection.url} iconLeft={<KibaIcon iconId='ion-globe' />} />
                  </Stack.Item>
                )}
              </Stack>
              {account?.address && !isRefreshClicked && (
                <Button variant='tertiary' text= {'Refresh Metadata'} iconLeft={<KibaIcon iconId='ion-refresh-circle-outline' />} onClicked={onRefreshMetadataClicked} />
              )}
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
                    <MetricView name={'Total Volume'} value={`${ethers.utils.formatEther(collectionStatistics.totalTradeVolume)}`} />
                  </Stack>
                  <ResponsiveHidingView hiddenBelow={ScreenSize.Medium}>
                    <Box variant='divider' isFullHeight={true} width='1px' />
                  </ResponsiveHidingView>
                  <Stack direction={Direction.Horizontal} childAlignment={Alignment.Center} contentAlignment={Alignment.Center} shouldAddGutters={true} defaultGutter={PaddingSize.Wide}>
                    <MetricView name={'24h Low Sale'} value={`Ξ ${ethers.utils.formatEther(collectionStatistics.lowestSaleLast24Hours)}`} />
                    <MetricView name={'24h High Sale'} value={`Ξ  ${ethers.utils.formatEther(collectionStatistics.highestSaleLast24Hours)}`} />
                    <MetricView name={'24h Volume'} value={`Ξ ${ethers.utils.formatEther(collectionStatistics.tradeVolume24Hours)}`} />
                  </Stack>
                </Stack>
              )}
              { account ? (
                <Stack direction={Direction.Vertical} isFullWidth={true} childAlignment={Alignment.Start} shouldAddGutters={true} paddingVertical={PaddingSize.Wide2} isScrollableHorizontally={true}>
                  <Text variant='header3'>{`Your Holdings (${holdings?.length})`}</Text>
                  <Stack direction={Direction.Horizontal} contentAlignment={Alignment.Center} childAlignment={Alignment.Center} shouldAddGutters={true}>
                    {holdings && holdings.length !== 0 ? holdings.map((holding: CollectionToken, index: number) : React.ReactElement => (
                      <TokenCard
                        key={index}
                        collectionToken={holding}
                        // subtitle={`Bought at ${dateToString(holding.blockDate, 'HH:mm')} for Ξ${holding.value / 1000000000000000000.0}`}
                        target={`/collections/${holding.registryAddress}/tokens/${holding.tokenId}`}
                      />
                    )) : (
                      <Text>No Holdings</Text>
                    )}
                  </Stack>
                </Stack>
              ) : (
                <Stack direction={Direction.Horizontal} shouldAddGutters={true} paddingTop={PaddingSize.Wide2}>
                  <Link text='Connect your wallet' onClicked={onConnectWalletClicked} />
                  <Text>to show your holdings and watchlist.</Text>
                </Stack>
              )}
              <Stack direction={Direction.Vertical} isFullWidth={true} childAlignment={Alignment.Start} shouldAddGutters={true} paddingVertical={PaddingSize.Wide2} isScrollableHorizontally={true}>
                <Text variant='header3'>Recent Sales</Text>
                <Stack direction={Direction.Horizontal} contentAlignment={Alignment.Center} childAlignment={Alignment.Center} shouldAddGutters={true}>
                  { recentSales === undefined ? (
                    <LoadingSpinner />
                  ) : recentSales === null ? (
                    <Text variant='error'>Collection Sale failed to load</Text>
                  ) : recentSales && recentSales.length !== 0 ? recentSales.map((recentSale: TokenTransfer, index: number) : React.ReactElement => (
                    <TokenCard
                      key={index}
                      collectionToken={recentSale.token}
                      subtitle={`Sold at ${dateToString(recentSale.blockDate, 'HH:mm')} for Ξ${ethers.utils.formatEther(recentSale.value)}`}
                      target={`/collections/${recentSale.registryAddress}/tokens/${recentSale.tokenId}`}
                    />
                  )) : (
                    <Text>No recent sales</Text>
                  )}
                </Stack>
              </Stack>
              { collectionActivities && (
                <Box height='350px'>
                  <Text variant='header3'>Recent Activity</Text>
                  <RechartsContainer width='100%' height='100%'>
                    <AreaChart data={chartData}>
                      <defs>
                        <linearGradient id='gradient-color' x1='0%' y1='0%' x2='100%' y2='0%'>
                          <stop stopColor={colors.brandPrimaryClear50} />
                        </linearGradient>
                      </defs>
                      <Legend formatter={renderColorfulLegendText} iconType='circle' align='right' />
                      <CartesianGrid stroke={colors.brandPrimary} strokeDasharray='3 3' />
                      <XAxis dataKey='date' />
                      <YAxis yAxisId={0} />
                      <YAxis yAxisId={1}type='number' domain={['dataMin', 'auto']} orientation='right' />
                      <Tooltip content={renderCustomToolTip} />
                      <Area isAnimationActive={false} type='monotone' dataKey='saleCount' stroke={colors.xAxis1} strokeWidth={2} fill='#ffffff' fillOpacity={0.15} yAxisId={1} />
                      <Area isAnimationActive={false} type='monotone' dataKey='averageValue' stroke={colors.text}strokeWidth={2} fill='#ffffff' fillOpacity={0} yAxisId={0} />
                    </AreaChart>
                  </RechartsContainer>
                </Box>
              )}
            </Stack>
          </ContainingView>
        </Stack>
      )}
    </Stack>
  );
};
