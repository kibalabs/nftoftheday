import React from 'react';

import { useRouteParams } from '@kibalabs/core-react';
import { Alignment, BackgroundView, Box, Button, ContainingView, Direction, EqualGrid, Image, KibaIcon, MarkdownText, PaddingSize, Spacing, Stack, Text } from '@kibalabs/ui-react';

import { Collection } from '../../client/resources';
import { useGlobals } from '../../globalsContext';

export const CollectionsPage = (): React.ReactElement => {
  const { notdClient } = useGlobals();
  const [collection, setCollection] = React.useState<Collection | null>(null);
  const collectionBannerUrl = collection?.bannerImageUrl as string;
  const collectionDiscord = collection?.discordUrl as string;
  const collectionInstagram = collection?.instagramUsername as string;
  const collectionImageUrl = collection?.imageUrl as string;
  const collectionDescription = collection?.description as string;
  const collectionTwitter = collection?.twitterUsername as string;
  const collectionName = collection?.name as string;
  const collectionOpenSeaSlug = collection?.openseaSlug as string;

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
          <Image source={collectionBannerUrl} alternativeText='image' fitType='cover' />
          <Stack direction={Direction.Horizontal} isFullWidth={true} childAlignment={Alignment.Center} contentAlignment={Alignment.Center} padding={PaddingSize.Wide2}>
            <Box variant='rounded-borderColored' shouldClipContent={true} width='100px' height='100px'>
              <Image source={collectionImageUrl} alternativeText='image' fitType='contain' />
            </Box>
            <Spacing variant={PaddingSize.Wide2} />
            <Text variant='header1'>{collectionName}</Text>
          </Stack>
          <MarkdownText textVariant='light' source={collectionDescription} />
          <Stack direction={Direction.Horizontal} isFullWidth={true} contentAlignment={Alignment.Center} padding={PaddingSize.Wide2} shouldAddGutters={true}>
            <MarkdownText textVariant='light' source={collectionDescription} />
            <Stack direction={Direction.Vertical} contentAlignment={Alignment.Center} childAlignment={Alignment.Start} shouldAddGutters={true}>
              {collectionDiscord
                ? (<Button variant='tertiary' text= 'Discord' iconLeft={<KibaIcon iconId='ion-logo-discord' />} target={collectionDiscord} />
                ) : collectionInstagram ? (
                  <Button variant='tertiary' text={'Instagram'} target={`https://instagram.com/${collectionInstagram}`} iconLeft={<KibaIcon iconId='feather-instagram' />} />
                ) : collectionTwitter ? (
                  <Button variant='tertiary' text={'Twitter'} target={`https://instagram.com/${collectionTwitter}`} iconLeft={<KibaIcon iconId='feather-twitter' />} />
                ) : (
                  <Button variant='tertiary' text={'opensea'} target={`https://opensea.io/collection/${collectionOpenSeaSlug}`} />
                )}
            </Stack>
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
            {`Recent ${collectionName} sales`}
          </Text>
          <ContainingView>
            <EqualGrid isFullHeight={false} childSizeResponsive={{ base: 12, small: 6, large: 4, extraLarge: 3 }} contentAlignment={Alignment.Center} childAlignment={Alignment.Center} shouldAddGutters={true}>
              <Box variant='card'>
                <Stack direction={Direction.Vertical} childAlignment={Alignment.Center} contentAlignment={Alignment.Center} padding={PaddingSize.Wide2}>
                  <Box variant='card' width='250px' height='250px'>
                    <Image source={collectionImageUrl} alternativeText='image' fitType='contain' />
                  </Box>
                  <Spacing variant={PaddingSize.Wide2} />
                  <Text variant='header7'>
                    {`${collectionDescription}sold for $37k yesterday`}
                  </Text>
                </Stack>
              </Box>
              <Box variant='card'>
                <Stack direction={Direction.Vertical} childAlignment={Alignment.Center} contentAlignment={Alignment.Center} padding={PaddingSize.Wide2}>
                  <Box variant='card' width='250px' height='250px'>
                    <Image source={collectionImageUrl} alternativeText='image' fitType='contain' />
                  </Box>
                  <Spacing variant={PaddingSize.Wide2} />
                  <Text variant='header7'>
                    {`${collectionDescription}sold for $37k yesterday`}
                  </Text>
                </Stack>
              </Box>
              <Box variant='card'>
                <Stack direction={Direction.Vertical} childAlignment={Alignment.Center} contentAlignment={Alignment.Center} padding={PaddingSize.Wide2}>
                  <Box variant='card' width='250px' height='250px'>
                    <Image source={collectionImageUrl} alternativeText='image' fitType='contain' />
                  </Box>
                  <Spacing variant={PaddingSize.Wide2} />
                  <Text variant='header7'>
                    {`${collectionDescription}sold for $37k yesterday`}
                  </Text>
                </Stack>
              </Box>
              <Box variant='card'>
                <Stack direction={Direction.Vertical} childAlignment={Alignment.Center} contentAlignment={Alignment.Center} padding={PaddingSize.Wide2}>
                  <Box variant='card' width='250px' height='250px'>
                    <Image source={collectionImageUrl} alternativeText='image' fitType='contain' />
                  </Box>
                  <Spacing variant={PaddingSize.Wide2} />
                  <Text variant='header7'>
                    {`${collectionDescription}sold for $37k yesterday`}
                  </Text>
                </Stack>
              </Box>
            </EqualGrid>
            <Stack direction={Direction.Horizontal} childAlignment={Alignment.Start} contentAlignment={Alignment.Center}>
              <EqualGrid isFullHeight={false} childSizeResponsive={{ base: 10, small: 8, large: 6, extraLarge: 4 }} contentAlignment={Alignment.Center} childAlignment={Alignment.Center} shouldAddGutters={true}>
                <Box variant='card' isFullWidth={true}>
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
            </Stack>
          </ContainingView>
          <Text variant='header7'>Ten percent of the CryptoSkulls sales were for $187 or less, half of the sales were for less than $2327 and the highest ten percent were sold for $8.3k or higher.</Text>
        </Stack>
      </BackgroundView>
    </React.Fragment>
  );
};
