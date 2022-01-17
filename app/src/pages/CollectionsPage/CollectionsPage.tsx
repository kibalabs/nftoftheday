import React from 'react';

import { Link, useRouteParams } from '@kibalabs/core-react';
import { Alignment, BackgroundView, Box, ContainingView, Direction, EqualGrid, Image, PaddingSize, Pill, Stack, Text } from '@kibalabs/ui-react';

import { Collection } from '../../client/resources';
import { useGlobals } from '../../globalsContext';

export const CollectionsPage = (): React.ReactElement => {
  const { notdClient } = useGlobals();
  const [collection, setCollection] = React.useState<Collection | null>(null);
  const collectionImageUrl = collection?.imageUrl as string;

  const routeParams = useRouteParams();
  const address = routeParams.address as string;

  const updateCollection = React.useCallback(async (): Promise<void> => {
    const collectionPromise = notdClient.retrieveCollection(address);
    setCollection(await collectionPromise);
  }, [notdClient, address]);

  React.useEffect((): void => {
    updateCollection();
  }, [updateCollection]);

  return (
    <React.Fragment>
      <BackgroundView linearGradient='#200122,#6F0000'>
        <Stack direction={Direction.Vertical} isFullWidth={true} isFullHeight={true} childAlignment={Alignment.Center} contentAlignment={Alignment.Start} padding={PaddingSize.Wide2} isScrollableVertically={true}>
          <Stack direction={Direction.Horizontal} isFullWidth={true} childAlignment={Alignment.Center} contentAlignment={Alignment.Center} padding={PaddingSize.Wide2}>
            <Box variant='rounded-borderColored' shouldClipContent={true} width='100px' height='100px'>
              <Image source={collectionImageUrl} alternativeText='image' fitType='contain' />
            </Box>
            <Text variant='header1'>{collection?.name}</Text>
          </Stack>
          <Text variant='header3'>{collection?.description}</Text>
          <Stack direction={Direction.Horizontal} isFullWidth={true} contentAlignment={Alignment.Center} padding={PaddingSize.Wide2} shouldAddGutters={true}>
            <Text variant='header5'>{collection?.description}</Text>
            <Stack direction={Direction.Vertical} contentAlignment={Alignment.Center} shouldAddGutters={true}>
              <Link href={'https://opensea.com'}>opensea</Link>
              <Link href={'www.discord.com'}>Discord</Link>
              <Link href={'www.instagram.com'}>Instagram</Link>
              <Link href={'www.twitter.com'}>Twitter</Link>
              <Link href={'www.Activity.com'}>Activity</Link>
            </Stack>
          </Stack>
          <Stack direction={Direction.Horizontal} isFullWidth={true} contentAlignment={Alignment.Center} padding={PaddingSize.Wide2} shouldAddGutters={true}>
            <Pill variant='secondary' text='created over 2 years ago' />
            <Pill variant='secondary' text='fee' />
            <Pill variant='secondary' text='opensea verified' />
            <Pill variant='secondary' text='token supplied' />
            <Pill variant='secondary' text='discord members' />
            <Pill variant='secondary' text='twitter followers' />
          </Stack>
          <ContainingView>
            <Stack direction={Direction.Horizontal} isFullWidth={true}childAlignment={Alignment.Center} contentAlignment={Alignment.Center} padding={PaddingSize.Wide2} shouldAddGutters={true}>
              <EqualGrid isFullHeight={false} childSizeResponsive={{ base: 10, small: 8, large: 6, extraLarge: 4 }} contentAlignment={Alignment.Center} childAlignment={Alignment.Center} shouldAddGutters={true}>
                <Box variant='card'>
                  <Stack direction={Direction.Vertical} childAlignment={Alignment.Center} contentAlignment={Alignment.Center} padding={PaddingSize.Wide2} isScrollableVertically={true}>
                    <Text variant='header3'>NFTs Sold</Text>
                    <Text variant='header7'>Last 7 days</Text>
                    <Text variant='header2'>15,434</Text>
                  </Stack>
                </Box>
                <Box variant='card'>
                  <Stack direction={Direction.Vertical} childAlignment={Alignment.Center} contentAlignment={Alignment.Center} padding={PaddingSize.Wide2} isScrollableVertically={true}>
                    <Text variant='header3'>Trading Volume</Text>
                    <Text variant='header7'>Last 7 days</Text>
                    <Text variant='header2'>$44.09M</Text>
                  </Stack>
                </Box>
                <Box variant='card'>
                  <Stack direction={Direction.Vertical} childAlignment={Alignment.Center} contentAlignment={Alignment.Center} padding={PaddingSize.Wide2} isScrollableVertically={true}>
                    <Text variant='header3'>Average Price</Text>
                    <Text variant='header7'>Last 7 days</Text>
                    <Text variant='header2'>$3039</Text>
                  </Stack>
                </Box>
                <Box variant='card'>
                  <Stack direction={Direction.Vertical} childAlignment={Alignment.Center} contentAlignment={Alignment.Center} padding={PaddingSize.Wide2} isScrollableVertically={true}>
                    <Text variant='header3'>Floor Price</Text>
                    <Text variant='header7'>Lower ask price</Text>
                    <Text variant='header2'>2.7</Text>
                  </Stack>
                </Box>
                <Box variant='card'>
                  <Stack direction={Direction.Vertical} childAlignment={Alignment.Center} contentAlignment={Alignment.Center} padding={PaddingSize.Wide2} isScrollableVertically={true}>
                    <Text variant='header3'>Total Supply</Text>
                    <Text variant='header7'>Number of tokens</Text>
                    <Text variant='header2'>9,997</Text>
                  </Stack>
                </Box>
                <Box variant='card'>
                  <Stack direction={Direction.Vertical} childAlignment={Alignment.Center} contentAlignment={Alignment.Center} padding={PaddingSize.Wide2} isScrollableVertically={true}>
                    <Text variant='header3'>Owners</Text>
                    <Text variant='header7'>Number of owners</Text>
                    <Text variant='header2'>4,214</Text>
                  </Stack>
                </Box>
              </EqualGrid>
            </Stack>
          </ContainingView>
          <Text variant='header2'>
Recent
            {collection?.name}
            {' '}
sales
          </Text>
          <ContainingView>
            <EqualGrid isFullHeight={false} childSizeResponsive={{ base: 12, small: 6, large: 4, extraLarge: 3 }} contentAlignment={Alignment.Center} childAlignment={Alignment.Center} shouldAddGutters={true}>
              <Box variant='card'>
                <Stack direction={Direction.Vertical} childAlignment={Alignment.Center} contentAlignment={Alignment.Center} padding={PaddingSize.Wide2}>
                  <Box variant='card' width='250px' height='250px'>
                    <Image source={collectionImageUrl} alternativeText='image' fitType='contain' />
                  </Box>
                  <Text variant='header7'>
                    {collection?.description}
                    {' '}
sold for $37k yesterday
                  </Text>
                </Stack>
              </Box>
              <Box variant='card'>
                <Stack direction={Direction.Vertical} childAlignment={Alignment.Center} contentAlignment={Alignment.Center} padding={PaddingSize.Wide2}>
                  <Box variant='card' width='250px' height='250px'>
                    <Image source={collectionImageUrl} alternativeText='image' fitType='contain' />
                  </Box>
                  <Text variant='header7'>
                    {collection?.description}
                    {' '}
sold for $37k yesterday
                  </Text>
                </Stack>
              </Box>
              <Box variant='card'>
                <Stack direction={Direction.Vertical} childAlignment={Alignment.Center} contentAlignment={Alignment.Center} padding={PaddingSize.Wide2}>
                  <Box variant='card' width='250px' height='250px'>
                    <Image source={collectionImageUrl} alternativeText='image' fitType='contain' />
                  </Box>
                  <Text variant='header7'>
                    {collection?.description}
                    {' '}
sold for $37k yesterday
                  </Text>
                </Stack>
              </Box>
              <Box variant='card'>
                <Stack direction={Direction.Vertical} childAlignment={Alignment.Center} contentAlignment={Alignment.Center} padding={PaddingSize.Wide2}>
                  <Box variant='card' width='250px' height='250px'>
                    <Image source={collectionImageUrl} alternativeText='image' fitType='contain' />
                  </Box>
                  <Text variant='header7'>
                    {collection?.description}
                    {' '}
sold for $37k yesterday
                  </Text>
                </Stack>
              </Box>
            </EqualGrid>
            <EqualGrid isFullHeight={false} childSizeResponsive={{ base: 10, small: 8, large: 6, extraLarge: 4 }} contentAlignment={Alignment.Center} childAlignment={Alignment.Center} shouldAddGutters={true}>
              <Box variant='card'>
                <Stack direction={Direction.Vertical} childAlignment={Alignment.Center} contentAlignment={Alignment.Center} padding={PaddingSize.Wide2}>
                  <Text variant='header3'>10th percentile price</Text>
                  <Text variant='header7'>Last 7 days</Text>
                  <Text variant='header2'>187</Text>
                </Stack>
              </Box>
              <Box variant='card'>
                <Stack direction={Direction.Vertical} childAlignment={Alignment.Center} contentAlignment={Alignment.Center} padding={PaddingSize.Wide2}>
                  <Text variant='header3'>Median price</Text>
                  <Text variant='header7'>Last 7 days</Text>
                  <Text variant='header2'>$2324</Text>
                </Stack>
              </Box>
              <Box variant='card'>
                <Stack direction={Direction.Vertical} childAlignment={Alignment.Center} contentAlignment={Alignment.Center} padding={PaddingSize.Wide2}>
                  <Text variant='header3'>90th percentile price</Text>
                  <Text variant='header7'>Last 7 days</Text>
                  <Text variant='header2'>$8.3k</Text>
                </Stack>
              </Box>
            </EqualGrid>

          </ContainingView>
          <Text variant='header7'>Ten percent of the CryptoSkulls sales were for $187 or less, half of the sales were for less than $2327 and the highest ten percent were sold for $8.3k or higher.</Text>
        </Stack>
      </BackgroundView>
    </React.Fragment>
  );
};
