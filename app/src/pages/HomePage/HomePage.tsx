import React from 'react';

import { Alignment, BackgroundView, Box, PrettyText, Text, ContainingView, Direction, Head, Stack, PaddingSize, Image, Spacing, ResponsiveTextAlignmentView, TextAlignment, LoadingSpinner, EqualGrid, OptionSelect, IOption, } from '@kibalabs/ui-react';
import { useGlobals } from '../../globalsContext';
import styled, { keyframes as styledKeyframes} from 'styled-components';
import { TrendingCollection } from '../../client/resources';
import { longFormatEther, shortFormatEther } from '@kibalabs/core';
import { BigNumber } from 'ethers';

const TRENDING_COLLECTIONS_DURATION_OPTIONS: IOption[] = [
  {itemKey: '7_DAYS', text: '7 Days'},
  {itemKey: '30_DAYS', text: '30 Days'},
  {itemKey: '24_HOURS', text: '24 Hours'},
  {itemKey: '12_HOURS', text: '12 Hours'},
];

const HeroTextAnimation = styledKeyframes`
  to {
    background-position: 200% 0;
  }
`;

const HeroText = styled.span`
  background: linear-gradient(to right, #a34b4b, #ffffff, #a34b4b);//, #ffffff);
  background-size: 200% auto;
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  animation-name: ${HeroTextAnimation};
  animation-duration: 5s;
  animation-iteration-count: infinite;
`;

export const HomePage = (): React.ReactElement => {
  const { notdClient } = useGlobals();
  const [trendingCollectionsDuration, setTrendingCollectionsDuration] = React.useState<string>('24_HOURS');
  const [trendingCollections, setTrendingCollections] = React.useState<TrendingCollection[] | undefined | null>(undefined);

  const updateTrendingCollections = React.useCallback((): void => {
    setTrendingCollections(undefined);
    notdClient.listTrendingCollections(trendingCollectionsDuration, 9).then((retrievedTrendingCollections: TrendingCollection[]): void => {
      setTrendingCollections(retrievedTrendingCollections);
    }).catch((error: unknown): void => {
      console.error(error);
      setTrendingCollections(null);
    })
  }, [notdClient, trendingCollectionsDuration]);

  React.useEffect((): void => {
    updateTrendingCollections();
  }, [updateTrendingCollections]);

  const onTrendingCollectionsDurationClicked = (newTrendingCollectionsDuration: string): void => {
    setTrendingCollectionsDuration(newTrendingCollectionsDuration);
  }

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
          <Stack direction={Direction.Vertical} isFullWidth={true} childAlignment={Alignment.Start} contentAlignment={Alignment.Center} paddingHorizontal={PaddingSize.Wide2} isScrollableVertically={false}>
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
                  <Box key={index} variant='card' shouldClipContent={true}>
                    <Stack direction={Direction.Horizontal} shouldAddGutters={true} isFullHeight={true} isFullWidth={true} padding={PaddingSize.Wide} contentAlignment={Alignment.Start} childAlignment={Alignment.Center}>
                      <Text variant='note'>{`#${index + 1}`}</Text>
                      <Image variant='rounded' source={trendingCollection.collection.imageUrl || ''} alternativeText={trendingCollection.collection.name || ''} maxHeight='3em' maxWidth='3em' fitType='cover' />
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
                  </Box>
                ))}
              </EqualGrid>
            )}
            <Spacing variant={PaddingSize.Wide3} />
          </Stack>
        </ContainingView>
        <Stack.Item growthFactor={1} shrinkFactor={1} />
      </Stack>
    </React.Fragment>
  );
};
