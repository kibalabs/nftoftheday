import React from 'react';

import { Alignment, BackgroundView, Box, PrettyText, Text, ContainingView, Direction, Head, Stack, PaddingSize, Image, Spacing, ResponsiveTextAlignmentView, TextAlignment, LoadingSpinner, EqualGrid, OptionSelect, IOption, useColors, SelectableView, MarkdownText, Button, Link, } from '@kibalabs/ui-react';
import { useGlobals } from '../../globalsContext';
import styled, { keyframes as styledKeyframes} from 'styled-components';
import { Collection, CollectionToken, MintedTokenCount, TokenTransfer, TokenTransferValue, TrendingCollection } from '../../client/resources';
import { addDays, dateToString, etherToNumber, longFormatEther, shortFormatEther } from '@kibalabs/core';
import { BigNumber } from 'ethers';
import { Area, AreaChart, Bar, ComposedChart, CartesianGrid, ResponsiveContainer as RechartsContainer, Tooltip, XAxis, YAxis, ResponsiveContainer, Scatter } from 'recharts';

interface MintedTokenChartData {
  date: number;
  mintedTokenCount: number;
  newRegistryCount: number;
}

const renderMintedTokenChartToolTip = (dataItem: any): React.ReactElement | null => {
  if (!dataItem.payload || dataItem.payload.length === 0) {
    return null;
  }
  const tooltipData = dataItem.payload[0].payload;
  return (
    <Box variant='card-tooltip'>
      <Stack direction={Direction.Vertical} isFullWidth={true} isFullHeight={true} childAlignment={Alignment.Start} contentAlignment={Alignment.Start} padding={PaddingSize.Wide1}>
        <Text>{`Date: ${dateToString(new Date(tooltipData.date), 'HH:mm dd/MM/yyyy')}`}</Text>
        <Text>{`New Collections: ${tooltipData.newRegistryCount}`}</Text>
      </Stack>
    </Box>
  );
};

interface TrendingCollectionTokenTransferValuesChartData {
  date: number;
  value: number;
}

const renderTrendingCollectionTokenTransferValuesTooltip = (dataItem: any): React.ReactElement | null => {
  if (!dataItem.payload || dataItem.payload.length === 0) {
    return null;
  }
  const tooltipData = dataItem.payload[0].payload;
  return (
    <Box variant='card-tooltip'>
      <Stack direction={Direction.Vertical} isFullWidth={true} isFullHeight={true} childAlignment={Alignment.Start} contentAlignment={Alignment.Start} padding={PaddingSize.Wide1}>
        <Text>{`Date: ${dateToString(new Date(tooltipData.date), 'HH:mm dd/MM/yyyy')}`}</Text>
        <Text>{`Value: Ξ${tooltipData.value}`}</Text>
      </Stack>
    </Box>
  );
};

const TRENDING_COLLECTIONS_DURATION_OPTIONS: IOption[] = [
  {itemKey: '12_HOURS', text: '12 Hours'},
  {itemKey: '24_HOURS', text: '24 Hours'},
  {itemKey: '7_DAYS', text: '7 Days'},
  {itemKey: '30_DAYS', text: '30 Days'},
];

const MINTED_TOKEN_COUNTS_DURATION_OPTIONS: IOption[] = [
  {itemKey: '12_HOURS', text: '12 Hours'},
  {itemKey: '24_HOURS', text: '24 Hours'},
  {itemKey: '7_DAYS', text: '7 Days'},
  {itemKey: '30_DAYS', text: '30 Days'},
  {itemKey: '90_DAYS', text: '90 Days'},
  {itemKey: '180_DAYS', text: '180 Days'},
];

const HeroTextAnimation = styledKeyframes`
  to {
    background-position: -200% 0;
  }
`;

const HeroText = styled.span`
  background: linear-gradient(to right, #00A3FF 0%, #00A3FF 90%, #c2e9ff 95%, #00A3FF 100%);
  background-position: 0% 0;
  background-size: 200% auto;
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  animation-name: ${HeroTextAnimation};
  animation-duration: 4s;
  animation-iteration-count: infinite;
  animation-timing-function: linear;

`;

export const HomePage = (): React.ReactElement => {
  const { notdClient } = useGlobals();
  const colors = useColors();
  const [heroTokens, setHeroTokens] = React.useState<CollectionToken[] | undefined | null>(undefined);
  const [trendingCollectionsDuration, setTrendingCollectionsDuration] = React.useState<string>(TRENDING_COLLECTIONS_DURATION_OPTIONS[0].itemKey);
  const [trendingCollections, setTrendingCollections] = React.useState<TrendingCollection[] | undefined | null>(undefined);
  const [selectedTrendingCollection, setSelectedTrendingCollection] = React.useState<Collection | undefined | null>(undefined);
  const [trendingCollectionTokenTransferValues, setTrendingCollectionTokenTransferValues] = React.useState<TokenTransferValue[] | undefined | null>(undefined);
  const [mintedTokenCountsDuration, setMintedTokenCountsDuration] = React.useState<string>(MINTED_TOKEN_COUNTS_DURATION_OPTIONS[0].itemKey);
  const [mintedTokenCounts, setMintedTokenCounts] = React.useState<MintedTokenCount[] | undefined | null>(undefined);

  const updateHeroTokens = React.useCallback((): void => {
    setHeroTokens(undefined);
    notdClient.retrieveHeroTokens().then((retrievedHeroTokens: CollectionToken[]): void => {
      setHeroTokens(retrievedHeroTokens);
    }).catch((error: unknown): void => {
      console.error(error);
      setHeroTokens(null);
    });
  }, [notdClient]);

  React.useEffect((): void => {
    updateHeroTokens();
  }, [updateHeroTokens]);

  const updateTrendingCollections = React.useCallback((): void => {
    setTrendingCollections(undefined);
    setSelectedTrendingCollection(undefined);
    notdClient.retrieveTrendingCollections(trendingCollectionsDuration, 9).then((retrievedTrendingCollections: TrendingCollection[]): void => {
      setTrendingCollections(retrievedTrendingCollections);
      setSelectedTrendingCollection(retrievedTrendingCollections.length > 0 ? retrievedTrendingCollections[0].collection : null);
    }).catch((error: unknown): void => {
      console.error(error);
      setTrendingCollections(null);
      setSelectedTrendingCollection(null);
    });
  }, [notdClient, trendingCollectionsDuration]);

  React.useEffect((): void => {
    updateTrendingCollections();
  }, [updateTrendingCollections]);

  const updateTrendingCollectionGraphData = React.useCallback((): void => {
    if (!selectedTrendingCollection) {
      setTrendingCollectionTokenTransferValues(null);
      return;
    }
    setTrendingCollectionTokenTransferValues(undefined);
    const maxDate = new Date();
    let minDate: Date | undefined = addDays(maxDate, -1);;
    if (trendingCollectionsDuration === '12_HOURS') {
      minDate = addDays(maxDate, -0.5);
    } else if (trendingCollectionsDuration === '24_HOURS') {
      minDate = addDays(maxDate, -1);
    } else if (trendingCollectionsDuration === '7_DAYS') {
      minDate = addDays(maxDate, -7);
    } else if (trendingCollectionsDuration === '30_DAYS') {
      minDate = addDays(maxDate, -30);
    } else if (trendingCollectionsDuration === '90_DAYS') {
      minDate = addDays(maxDate, -90);
    } else if (trendingCollectionsDuration === '180_DAYS') {
      minDate = addDays(maxDate, -180);
    }
    notdClient.listCollectionTransferValues(selectedTrendingCollection.address, minDate, maxDate, BigNumber.from(1)).then((retrievedTokenTransferValues: TokenTransferValue[]): void => {
      setTrendingCollectionTokenTransferValues(retrievedTokenTransferValues.sort((tokenTransferValue1: TokenTransferValue, tokenTransferValue2: TokenTransferValue): number => {
        return tokenTransferValue1.blockDate.getTime() - tokenTransferValue2.blockDate.getTime();
      }));
    }).catch((error: unknown): void => {
      console.error(error);
      setTrendingCollectionTokenTransferValues(null);
    });
  }, [notdClient, selectedTrendingCollection, trendingCollectionsDuration]);

  React.useEffect((): void => {
    updateTrendingCollectionGraphData();
  }, [updateTrendingCollectionGraphData]);

  const onTrendingCollectionsDurationClicked = (newTrendingCollectionsDuration: string): void => {
    setTrendingCollectionsDuration(newTrendingCollectionsDuration);
  }

  const updateMintedTokenCounts = React.useCallback((): void => {
    setMintedTokenCounts(undefined);
    notdClient.retrieveMintedTokenCounts(mintedTokenCountsDuration).then((retrievedMintedTokenCounts: MintedTokenCount[]): void => {
      setMintedTokenCounts(retrievedMintedTokenCounts);
    }).catch((error: unknown): void => {
      console.error(error);
      setMintedTokenCounts(null);
    })
  }, [notdClient, mintedTokenCountsDuration]);

  React.useEffect((): void => {
    updateMintedTokenCounts();
  }, [updateMintedTokenCounts]);

  const onMintedTokenCountsDurationClicked = (newMintedTokenCountsDuration: string): void => {
    setMintedTokenCountsDuration(newMintedTokenCountsDuration);
  }

  const mintedTokenCountsChartData = React.useMemo((): MintedTokenChartData[] | undefined | null => {
    if (mintedTokenCounts === undefined) {
      return undefined;
    }
    if (mintedTokenCounts === null) {
      return null;
    }
    return mintedTokenCounts.map((mintedToken: MintedTokenCount): MintedTokenChartData => ({
      date: mintedToken.date.getTime(),
      mintedTokenCount: mintedToken.mintedTokenCount.toNumber(),
      newRegistryCount: mintedToken.newRegistryCount.toNumber(),
    }));
  }, [mintedTokenCounts]);

  const onTrendingCollectionClicked = (trendingCollection: TrendingCollection): void => {
    setSelectedTrendingCollection(trendingCollection.collection);
  }

  const trendingCollectionTokenTransferValuesChartData = React.useMemo((): TrendingCollectionTokenTransferValuesChartData[] | undefined | null => {
    if (trendingCollectionTokenTransferValues === undefined) {
      return undefined;
    }
    if (trendingCollectionTokenTransferValues === null) {
      return null;
    }
    return trendingCollectionTokenTransferValues.map((tokenTransferValue: TokenTransferValue): TrendingCollectionTokenTransferValuesChartData => ({
      date: tokenTransferValue.blockDate.getTime(),
      value: tokenTransferValue.value.div(1000000000000000).toNumber() / 1000,
    }));
  }, [trendingCollectionTokenTransferValues]);

  console.log('heroTokens', heroTokens);

  return (
    <React.Fragment>
      <Head headId='home'>
        <title>Token Hunt</title>
      </Head>
      <Stack direction={Direction.Vertical} isFullWidth={true} childAlignment={Alignment.Center} contentAlignment={Alignment.Start}>
        <BackgroundView layers={[{imageUrl: 'https://arweave.net/cuGWQb6lme5sVhumf1yrt2GnTuxILG_f-9IhbDyLIEY'}, {color: 'rgba(0, 0, 0, 0.9)'}]}>
          <Box>
            <ContainingView>
              <Stack directionResponsive={{base: Direction.Vertical, medium: Direction.Horizontal}} isFullWidth={true} childAlignment={Alignment.Center} contentAlignment={Alignment.Start} paddingVertical={PaddingSize.Wide2} paddingHorizontal={PaddingSize.Wide2}>
                <Stack.Item growthFactor={1} shrinkFactor={1} shouldShrinkBelowContentSize={true}>
                  <ResponsiveTextAlignmentView alignmentResponsive={{base: TextAlignment.Center, medium: TextAlignment.Left}}>
                    <Stack direction={Direction.Vertical} shouldAddGutters={true}>
                      <PrettyText variant='header2-large'>Your explorer for <HeroText>all NFTs and Collections</HeroText> on Ethereum Mainnet 🎭</PrettyText>
                    </Stack>
                  </ResponsiveTextAlignmentView>
                </Stack.Item>
                <Spacing variant={PaddingSize.Wide} />
                <Box widthResponsive={{base: '100%', medium: '40%'}} height='400px' maxHeight='calc(max(400px, 0.5vh))' maxWidth='calc(max(400px, 0.5vh))'>
                  <Stack direction={Direction.Vertical} shouldAddGutters={true} isFullHeight={true} isFullWidth={true}>
                    <Stack.Item growthFactor={1} shrinkFactor={1} shouldShrinkBelowContentSize={true}>
                      <Image variant='rounded' source='https://arweave.net/cuGWQb6lme5sVhumf1yrt2GnTuxILG_f-9IhbDyLIEY' alternativeText='Title NFT' isFullWidth={true} fitType='cover' />
                    </Stack.Item>
                    <Text variant='note'>XYZ 123</Text>
                  </Stack>
                </Box>
              </Stack>
            </ContainingView>
          </Box>
        </BackgroundView>
        <ContainingView>
          <Stack direction={Direction.Vertical} isFullWidth={true} childAlignment={Alignment.Start} contentAlignment={Alignment.Center} paddingHorizontal={PaddingSize.Wide2}>
            <Spacing variant={PaddingSize.Wide3} />
            <Stack directionResponsive={{base: Direction.Vertical, small: Direction.Horizontal}} isFullWidth={true}>
              <Stack direction={Direction.Vertical}>
                <Text variant='header2'>Trending Collections</Text>
                <Text>These are the collections with the most sales on mainnet.</Text>
              </Stack>
              <Stack.Item growthFactor={1} shrinkFactor={1}>
                <Spacing />
              </Stack.Item>
              <Box isFullWidth={false}>
                <OptionSelect options={TRENDING_COLLECTIONS_DURATION_OPTIONS} selectedItemKey={trendingCollectionsDuration} onItemClicked={onTrendingCollectionsDurationClicked} />
              </Box>
            </Stack>
            <Spacing variant={PaddingSize.Default} />
            {trendingCollections === undefined ? (
              <LoadingSpinner />
            ) : trendingCollections === null ? (
              <Text variant='note-error'>Failed to retrieve trendingCollections</Text>
            ) : (
              <EqualGrid childSizeResponsive={{base: 12, medium: 6, large: 4}} shouldAddGutters={true} childAlignment={Alignment.Start}>
                {trendingCollections.map((trendingCollection: TrendingCollection, index: number): React.ReactElement => (
                  <SelectableView key={index} variant='card' isSelected={trendingCollection.collection.address === selectedTrendingCollection?.address} onClicked={(): void => onTrendingCollectionClicked(trendingCollection)} shouldHideDefaultSelectedIndicator={true} isFullWidth={true} isFullHeight={true}>
                    <Stack direction={Direction.Horizontal} shouldAddGutters={true} isFullHeight={true} isFullWidth={true} padding={PaddingSize.Wide} contentAlignment={Alignment.Start} childAlignment={Alignment.Center}>
                      <Text variant='note'>{`#${index + 1}`}</Text>
                      <Image variant='rounded' source={trendingCollection.collection.imageUrl || ''} alternativeText={''} maxHeight='3em' maxWidth='3em' fitType='cover' />
                      <Stack.Item growthFactor={1} shrinkFactor={1}>
                        <Stack direction={Direction.Vertical} shouldAddGutters={false} contentAlignment={Alignment.Start}>
                          <Text isSingleLine={true}>{`${trendingCollection.collection.name}`}</Text>
                          <Stack direction={Direction.Horizontal} shouldAddGutters={true}>
                            <Text>{`${shortFormatEther(trendingCollection.totalVolume)}`}</Text>
                            {trendingCollection.previousTotalVolume.eq(BigNumber.from(0)) ? (
                              <Text variant='success'>{`✨ NEW`}</Text>
                            ) : (trendingCollection.totalVolume.gt(trendingCollection.previousTotalVolume)) ? (
                              <Text variant='success'>{`▴ ${(trendingCollection.totalVolume.sub(trendingCollection.previousTotalVolume)).mul(100).div(trendingCollection.previousTotalVolume.add(1))}%`}</Text>
                            ) : (trendingCollection.totalVolume.lt(trendingCollection.previousTotalVolume)) ? (
                              <Text variant='error'>{`▾ ${(trendingCollection.previousTotalVolume.sub(trendingCollection.totalVolume)).mul(100).div(trendingCollection.previousTotalVolume.add(1))}%`}</Text>
                            ) : (
                              <Text>{``}</Text>
                            )}
                          </Stack>
                        </Stack>
                      </Stack.Item>
                    </Stack>
                  </SelectableView>
                ))}
              </EqualGrid>
            )}
            {selectedTrendingCollection && trendingCollectionTokenTransferValuesChartData && (
              <React.Fragment>
                <Text variant='header3'>{`${selectedTrendingCollection.name} activity`}</Text>
                <Spacing />
                <Link text={`See all collection data`} target={`/collections/${selectedTrendingCollection.address}`} />
                <Spacing variant={PaddingSize.Wide} />
                <ResponsiveContainer width="100%" height={400}>
                  <ComposedChart data={trendingCollectionTokenTransferValuesChartData}>
                    <CartesianGrid stroke={colors.brandPrimaryClear90} strokeDasharray='3 3' />
                    <XAxis
                      dataKey='date'
                      tickFormatter={(value: number): string => {
                        return dateToString(new Date(value), 'dd.MM.yy');
                      }}
                      type='number'
                      domain={['min', (new Date()).getTime()]}
                      style={{ fontSize: '0.8em' }}
                    />
                    <YAxis yAxisId={0} />
                    <Tooltip content={renderTrendingCollectionTokenTransferValuesTooltip} />
                    <Scatter isAnimationActive={false} type='monotone' dataKey='value' stroke={colors.brandPrimary} strokeWidth={0} fill={colors.brandPrimary} fillOpacity={1} yAxisId={0} />
                  </ComposedChart>
                </ResponsiveContainer>
              </React.Fragment>
            )}
            <Spacing variant={PaddingSize.Wide3} />
            <Stack directionResponsive={{base: Direction.Vertical, small: Direction.Horizontal}} isFullWidth={true}>
              <Stack direction={Direction.Vertical}>
                <Text variant='header2'>New Collections Trend</Text>
                <Text>Here's how many new collections are being created on mainnet.</Text>
              </Stack>
              <Stack.Item growthFactor={1} shrinkFactor={1}>
                <Spacing />
              </Stack.Item>
              <Box isFullWidth={false}>
                <OptionSelect options={MINTED_TOKEN_COUNTS_DURATION_OPTIONS} selectedItemKey={mintedTokenCountsDuration} onItemClicked={onMintedTokenCountsDurationClicked} />
              </Box>
            </Stack>
            <Spacing variant={PaddingSize.Default} />
            {mintedTokenCountsChartData === undefined ? (
              <LoadingSpinner />
            ) : mintedTokenCountsChartData === null ? (
              <Text variant='note-error'>Failed to retrieve mintedTokenCounts</Text>
            ) : (
              <Box height='350px'>
                <RechartsContainer width='100%' height='100%'>
                  <ComposedChart data={mintedTokenCountsChartData}>
                    <CartesianGrid stroke={colors.brandPrimaryClear90} strokeDasharray='3 3' />
                    <XAxis
                      dataKey='date'
                      tickFormatter={(value: number): string => {
                        return dateToString(new Date(value), 'dd.MM.yy');
                      }}
                      type='number'
                      domain={['min', (new Date()).getTime()]}
                      style={{ fontSize: '0.8em' }}
                    />
                    <YAxis yAxisId={0} />
                    <Tooltip content={renderMintedTokenChartToolTip} />
                    <Bar isAnimationActive={false} type='monotone' dataKey='newRegistryCount' stroke={colors.brandPrimary} strokeWidth={0} fill={colors.brandPrimary} fillOpacity={1} yAxisId={0} />
                  </ComposedChart>
                </RechartsContainer>
              </Box>
            )}
            <Spacing variant={PaddingSize.Wide3} />
          </Stack>
        </ContainingView>
        <Stack childAlignment={Alignment.Center} isFullWidth={true}>
          <Box maxWidth='650px'>
            <Stack direction={Direction.Vertical} shouldAddGutters={true} isFullWidth={true} childAlignment={Alignment.Center} paddingHorizontal={PaddingSize.Wide}>
              <Spacing variant={PaddingSize.Wide3} />
              <PrettyText variant='header2' alignment={TextAlignment.Center}><HeroText>Super-charge your apps</HeroText> with rich data 🚀</PrettyText>
              <MarkdownText textVariant='default' textAlignment={TextAlignment.Center} source={`We've got a database brimming with insights about NFTs, Collections and Accounts. It's aching to be harnessed into custom APIs to power your apps.\n\nWe already use it to super-charge our own apps as well as some of the coolest web3 experiences such as [the Rude Boy's Gallery](https://gallery.rudeboys.io) and the suite of [SwapShop tools by seedphrase](https://swapshop.pro).\n\nGo on! Let's get your app filled with the rich data it deserves.`} />
              <Spacing variant={PaddingSize.Wide} />
              <Button variant='large-primary' target='#' text='Start using our API' />
              <Spacing variant={PaddingSize.Wide3} />
            </Stack>
          </Box>
        </Stack>
        <Stack.Item growthFactor={1} shrinkFactor={1} />
      </Stack>
    </React.Fragment>
  );
};
