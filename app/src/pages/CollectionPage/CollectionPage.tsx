import React from 'react';

import { dateToRelativeShortString, dateToString, etherToNumber, shortFormatEther } from '@kibalabs/core';
import { useFavicon, useInitialization, useIntegerUrlQueryState, useNavigator, useStringRouteParam } from '@kibalabs/core-react';
import { Alignment, Box, Button, ContainingView, Direction, Head, Image, KibaIcon, LayerContainer, Link, LoadingSpinner, PaddingSize, ResponsiveHidingView, ScreenSize, Stack, Text, TextAlignment, useColors } from '@kibalabs/ui-react';
import { useOnLinkWeb3AccountsClicked, useWeb3Account } from '@kibalabs/web3-react';
import { ethers } from 'ethers';
import { toast } from 'react-toastify';
import { TwitterTimelineEmbed } from 'react-twitter-embed';
import { Area, Bar, CartesianGrid, ComposedChart, ResponsiveContainer as RechartsContainer, Tooltip, XAxis, YAxis } from 'recharts';
import styled from 'styled-components';

import { ICollectionPageData } from './getCollectionPageData';
import { Collection, CollectionActivity, CollectionStatistics, CollectionToken, TokenTransfer } from '../../client/resources';
import { MetricView } from '../../components/MetricView';
import { TokenCard } from '../../components/TokenCard';
import { TruncateText } from '../../components/TruncateText';
import { useGlobals } from '../../globalsContext';
import { usePageData } from '../../PageDataContext';

interface ChartData {
  date: string;
  averageValue: number;
  saleCount: number;
}

const ColoredCircle = styled.div<{ fillColor: string, strokeColor: string }>`
  background-color: ${(props) => props.fillColor};
  width: 0.7em;
  height: 0.7em;
  border: 1px solid ${(props) => props.strokeColor};
  border-radius: 100%;
`;

export const CollectionPage = (): React.ReactElement => {
  const colors = useColors();
  const { data } = usePageData<ICollectionPageData>();
  const { notdClient } = useGlobals();
  const [collection, setCollection] = React.useState<Collection | undefined | null>(data?.collection || undefined);
  const [collectionStatistics, setCollectionStatistics] = React.useState<CollectionStatistics | undefined | null>(undefined);
  const [recentSales, setRecentSales] = React.useState<TokenTransfer[] | undefined | null>(undefined);
  const [collectionActivities, setCollectionActivities] = React.useState<CollectionActivity[] | undefined | null>(undefined);
  const [isRefreshClicked, setIsRefreshClicked] = React.useState<boolean>(false);
  const [shouldRefreshAllTokens, _] = useIntegerUrlQueryState('shouldRefreshAllTokens');
  const [holdings, setHoldings] = React.useState<CollectionToken[] | undefined | null>(undefined);
  const address = useStringRouteParam('address');
  const navigator = useNavigator();
  const account = useWeb3Account();
  const onLinkAccountsClicked = useOnLinkWeb3AccountsClicked();
  const bannerImageUrl = collection?.bannerImageUrl || '/assets/black_banner.png';
  const imageUrl = collection?.imageUrl || '/assets/icon.png';
  useFavicon(imageUrl);

  useInitialization((): void => {
    const checksumAddress = ethers.utils.getAddress(address);
    if (address !== checksumAddress) {
      navigator.navigateTo(`/collections/${checksumAddress}`);
    }
  });

  const updateCollection = React.useCallback(async (shouldClear = false): Promise<void> => {
    if (shouldClear) {
      setCollection(undefined);
    }
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

  const updateCollectionSales = React.useCallback(async (shouldClear = false): Promise<void> => {
    if (shouldClear) {
      setRecentSales(undefined);
    }
    notdClient.listCollectionRecentSales(address).then((tokenTransfers: TokenTransfer[]): void => {
      setRecentSales(tokenTransfers);
    }).catch((error: unknown): void => {
      console.error(error);
      setRecentSales(null);
    });
  }, [notdClient, address]);

  React.useEffect((): void => {
    updateCollectionSales();
  }, [updateCollectionSales]);

  const updateCollectionStatistics = React.useCallback(async (shouldClear = false): Promise<void> => {
    if (shouldClear) {
      setCollectionStatistics(undefined);
    }
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

  const getCollectionHoldings = React.useCallback(async (shouldClear = false): Promise<void> => {
    if (shouldClear) {
      setHoldings(undefined);
    }
    if (!account) {
      setHoldings(null);
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

  const updateCollectionActivities = React.useCallback(async (): Promise<void> => {
    setCollectionActivities(undefined);
    notdClient.getCollectionDailyActivities(address).then((retrievedCollectionActivities: CollectionActivity[]): void => {
      setCollectionActivities(retrievedCollectionActivities);
    }).catch((error: unknown): void => {
      console.error(error);
      setCollectionActivities(null);
    });
  }, [notdClient, address]);

  React.useEffect((): void => {
    updateCollectionActivities();
  }, [updateCollectionActivities]);

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

  const chartData = React.useMemo((): ChartData[] | null => {
    if (!collectionActivities) {
      return null;
    }
    return collectionActivities.map((collectionActivity: CollectionActivity): ChartData => ({
      date: dateToString(collectionActivity.date, 'dd/MM/yy'),
      averageValue: etherToNumber(collectionActivity.averageValue),
      saleCount: collectionActivity.saleCount.toNumber(),
    }));
  }, [collectionActivities]);

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const renderCustomToolTip = (dataItem: any): React.ReactElement | null => {
    if (!dataItem.payload || dataItem.payload.length === 0) {
      return null;
    }
    const tooltipData = dataItem.payload[0].payload;
    return (
      <Box variant='card-tooltip'>
        <Stack direction={Direction.Vertical} isFullWidth={true} isFullHeight={true} childAlignment={Alignment.Start} contentAlignment={Alignment.Start} padding={PaddingSize.Wide1}>
          <Text>{`Date: ${tooltipData.date}`}</Text>
          <Text>{`Sale count: ${tooltipData.saleCount}`}</Text>
          <Text>{`Average value: Ξ${tooltipData.averageValue}`}</Text>
        </Stack>
      </Box>
    );
  };

  return (
    <React.Fragment>
      <Head>
        <title>{`${collection ? collection.name : 'Collection'} | Token Hunt`}</title>
      </Head>
      <Stack direction={Direction.Vertical} isFullWidth={true} isFullHeight={true} childAlignment={Alignment.Center} contentAlignment={Alignment.Start}>
        {collection === undefined ? (
          <LoadingSpinner />
        ) : collection === null ? (
          <Text variant='error'>Collection failed to load</Text>
        ) : (
          <React.Fragment>
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
                  <Box variant='rounded-avatar' shouldClipContent={true} width='130px' height='130px'>
                    <Image source={imageUrl} alternativeText='image' fitType='contain' />
                  </Box>
                </LayerContainer.Layer>
              </LayerContainer>
            </Box>
            <ContainingView>
              <Stack direction={Direction.Vertical} isFullWidth={true} childAlignment={Alignment.Fill} paddingHorizontal={PaddingSize.Wide2} paddingBottom={PaddingSize.Wide2} paddingTop={PaddingSize.Default} shouldAddGutters={true} defaultGutter={PaddingSize.Wide2}>
                <Stack.Item gutterAfter={PaddingSize.Default}>
                  <Text variant='header1' alignment={TextAlignment.Center}>{collection.name}</Text>
                </Stack.Item>
                {collection.description && (
                  <TruncateText
                    markdownText={collection.description}
                    textAlignment={TextAlignment.Center}
                    maximumCharacters={300}
                  />
                )}
                <Stack direction={Direction.Horizontal} shouldAddGutters={true} contentAlignment={Alignment.Center} childAlignment={Alignment.Center} isFullWidth={true} shouldWrapItems={true}>
                  {collection.discordUrl && (
                    <Stack.Item baseSize='5em'>
                      <Button variant='tertiary' text= {'Discord'} iconLeft={<KibaIcon iconId='ion-logo-discord' />} target={collection.discordUrl} />
                    </Stack.Item>
                  )}
                  {collection.instagramUsername && (
                    <Stack.Item baseSize='5em'>
                      <Button variant='tertiary' text={'Instagram'} target={`https://instagram.com/${collection.instagramUsername}`} iconLeft={<KibaIcon iconId='feather-instagram' />} />
                    </Stack.Item>
                  )}
                  {collection.twitterUsername && (
                    <Stack.Item baseSize='5em'>
                      <Button variant='tertiary' text={'Twitter'} target={`https://twitter.com/${collection.twitterUsername}`} iconLeft={<KibaIcon iconId='feather-twitter' />} />
                    </Stack.Item>
                  )}
                  {collection.openseaSlug && (
                    <Stack.Item baseSize='5em'>
                      <Button variant='tertiary' text={'Opensea'} target={`https://opensea.io/collection/${collection.openseaSlug}`} iconLeft={<KibaIcon iconId='ion-cart' />} />
                    </Stack.Item>
                  )}
                  {collection.url && (
                    <Stack.Item baseSize='5em'>
                      <Button variant='tertiary' text={'Website'} target={collection.url} iconLeft={<KibaIcon iconId='ion-globe' />} />
                    </Stack.Item>
                  )}
                  {account?.address && !isRefreshClicked && (
                    <Button variant='tertiary' text= {'Refresh'} iconLeft={<KibaIcon iconId='ion-refresh-circle-outline' />} onClicked={onRefreshMetadataClicked} />
                  )}
                </Stack>
                {collectionStatistics === undefined ? (
                  <LoadingSpinner />
                ) : collectionStatistics === null ? (
                  <Text variant='error'>Collection statistics failed to load</Text>
                ) : (
                  <Stack directionResponsive={{ base: Direction.Vertical, medium: Direction.Horizontal }} isFullWidth={true} childAlignment={Alignment.Center} contentAlignment={Alignment.Center} shouldAddGutters={true} defaultGutter={PaddingSize.Wide}>
                    <Stack direction={Direction.Horizontal} childAlignment={Alignment.Center} contentAlignment={Alignment.Center} shouldAddGutters={true} defaultGutter={PaddingSize.Wide}>
                      <MetricView name={'Items'} value={`${collectionStatistics.itemCount}`} />
                      <MetricView name={'Owners'} value={`${collectionStatistics.holderCount}`} />
                      <MetricView name={'Total Volume'} value={shortFormatEther(collectionStatistics.totalTradeVolume)} />
                    </Stack>
                    <ResponsiveHidingView hiddenBelow={ScreenSize.Medium}>
                      <Box variant='divider' isFullHeight={true} width='1px' />
                    </ResponsiveHidingView>
                    <Stack direction={Direction.Horizontal} childAlignment={Alignment.Center} contentAlignment={Alignment.Center} shouldAddGutters={true} defaultGutter={PaddingSize.Wide}>
                      <MetricView name={'24h Low Sale'} value={shortFormatEther(collectionStatistics.lowestSaleLast24Hours)} />
                      <MetricView name={'24h High Sale'} value={shortFormatEther(collectionStatistics.highestSaleLast24Hours)} />
                      <MetricView name={'24h Volume'} value={shortFormatEther(collectionStatistics.tradeVolume24Hours)} />
                    </Stack>
                  </Stack>
                )}
                { account ? (
                  <React.Fragment>
                    <Stack.Item gutterAfter={PaddingSize.Narrow}>
                      <Text variant='header3'>{`Your Holdings (${holdings?.length})`}</Text>
                    </Stack.Item>
                    <Stack direction={Direction.Horizontal} contentAlignment={Alignment.Start} childAlignment={Alignment.Start} shouldAddGutters={true} isScrollableHorizontally={true}>
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
                  </React.Fragment>
                ) : (
                  <Stack direction={Direction.Horizontal} shouldAddGutters={true} contentAlignment={Alignment.Center}>
                    <Link text='Connect your wallet' onClicked={onConnectWalletClicked} />
                    <Text>to show your holdings and watchlist.</Text>
                  </Stack>
                )}
                <Stack.Item gutterAfter={PaddingSize.Narrow}>
                  <Text variant='header3'>Recent Sales</Text>
                </Stack.Item>
                <Stack direction={Direction.Horizontal} contentAlignment={Alignment.Start} childAlignment={Alignment.Start} shouldAddGutters={true} isScrollableHorizontally={true}>
                  { recentSales === undefined ? (
                    <LoadingSpinner />
                  ) : recentSales === null ? (
                    <Text variant='error'>Failed to load recent sales</Text>
                  ) : recentSales && recentSales.length !== 0 ? recentSales.map((recentSale: TokenTransfer, index: number) : React.ReactElement => (
                    <TokenCard
                      key={index}
                      collectionToken={recentSale.token}
                      subtitle={`${dateToRelativeShortString(recentSale.blockDate)} • ${shortFormatEther(recentSale.value)}`}
                      target={`/collections/${recentSale.registryAddress}/tokens/${recentSale.tokenId}`}
                    />
                  )) : (
                    <Text>No recent sales</Text>
                  )}
                </Stack>
                <Stack.Item gutterAfter={PaddingSize.Narrow}>
                  <Text variant='header3'>Recent Activity</Text>
                </Stack.Item>
                { collectionActivities === undefined ? (
                  <LoadingSpinner />
                ) : collectionActivities === null || chartData === null ? (
                  <Text variant='error'>Failed to load activity</Text>
                ) : (
                  <React.Fragment>
                    <Stack.Item gutterAfter={PaddingSize.Narrow}>
                      <Box height='350px'>
                        <RechartsContainer width='100%' height='100%'>
                          <ComposedChart data={chartData}>
                            <CartesianGrid stroke={colors.brandPrimaryClear90} strokeDasharray='3 3' />
                            <XAxis dataKey='date' />
                            <YAxis yAxisId={0} type='number' domain={['dataMin', 'auto']} orientation='right' />
                            <YAxis yAxisId={1} />
                            <Tooltip content={renderCustomToolTip} />
                            <Bar isAnimationActive={false} type='monotone' dataKey='saleCount' stroke={colors.brandPrimary} strokeWidth={0} fill={colors.backgroundLight50} fillOpacity={0.5} yAxisId={1} />
                            <Area isAnimationActive={false} type='monotone' dataKey='averageValue' stroke={colors.text} strokeWidth={2} fillOpacity={0} yAxisId={0} />
                          </ComposedChart>
                        </RechartsContainer>
                      </Box>
                    </Stack.Item>
                    <Stack direction={Direction.Horizontal} shouldWrapItems={true} contentAlignment={Alignment.Center} shouldAddGutters={true} defaultGutter={PaddingSize.Wide} isFullWidth={true}>
                      <Stack direction={Direction.Horizontal} childAlignment={Alignment.Center} shouldAddGutters={true} defaultGutter={PaddingSize.Narrow}>
                        <ColoredCircle fillColor={colors.brandPrimary} strokeColor={colors.brandPrimary} />
                        <Text variant='small'>Sale count</Text>
                      </Stack>
                      <Stack direction={Direction.Horizontal} childAlignment={Alignment.Center} shouldAddGutters={true} defaultGutter={PaddingSize.Narrow}>
                        <ColoredCircle fillColor={colors.text} strokeColor={colors.text} />
                        <Text variant='small'>Average value</Text>
                      </Stack>
                    </Stack>
                    { collection.twitterUsername && (
                      <React.Fragment>
                        <Stack.Item gutterAfter={PaddingSize.Narrow}>
                          <Text variant='header3'>Recent Tweets</Text>
                        </Stack.Item>
                        <Stack.Item alignment={Alignment.Center}>
                          <Box width='400px' maxWidth='90%'>
                            <TwitterTimelineEmbed
                              sourceType='profile'
                              screenName={`${collection.twitterUsername}`}
                              options={{ width: 900, height: 500 }}
                            />
                          </Box>
                        </Stack.Item>
                      </React.Fragment>
                    )}
                  </React.Fragment>
                )}
              </Stack>
            </ContainingView>
          </React.Fragment>
        )}
      </Stack>
    </React.Fragment>
  );
};
