import React from 'react';

import { useRouteParams } from '@kibalabs/core-react';
import { Alignment, BackgroundView, Box, Button, ContainingView, Direction, Image, KibaIcon, MarkdownText, PaddingSize, Spacing, Stack, Text } from '@kibalabs/ui-react';

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
  const collectionUrl = collection?.url as string;

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
        <Stack direction={Direction.Vertical} isFullWidth={true} isFullHeight={true} childAlignment={Alignment.Center} contentAlignment={Alignment.Start}>
          <Box variant='card' isFullWidth={true}>
            <Image source={collectionBannerUrl} alternativeText='image' isFullWidth={true} fitType='cover' />
          </Box>
          <ContainingView>
            <Stack direction={Direction.Horizontal} isFullWidth={true} childAlignment={Alignment.Center} contentAlignment={Alignment.Center} paddingTop={PaddingSize.Wide3}>
              <Box variant='rounded-borderColored' shouldClipContent={true} width='100px' height='100px'>
                <Image source={collectionImageUrl} alternativeText='image' fitType='contain' />
              </Box>
              <Spacing variant={PaddingSize.Wide2} />
              <Stack.Item shrinkFactor={1}>
                <Text variant='title'>{collectionName}</Text>
              </Stack.Item>
            </Stack>
            <Stack direction={Direction.Horizontal} contentAlignment={Alignment.Center} childAlignment={Alignment.Center} shouldAddGutters={true}>
              {collectionDiscord && (
                <Button variant='tertiary' text= 'Discord' iconLeft={<KibaIcon iconId='ion-logo-discord' />} target={collectionDiscord} />)}
              { collectionInstagram && (
                <Button variant='tertiary' text={'Instagram'} target={`https://instagram.com/${collectionInstagram}`} iconLeft={<KibaIcon iconId='feather-instagram' />} />)}
              { collectionTwitter && (
                <Button variant='tertiary' text={'Twitter'} target={`https://instagram.com/${collectionTwitter}`} iconLeft={<KibaIcon iconId='feather-twitter' />} />)}
              {collectionOpenSeaSlug && (
                <Button variant='tertiary' text={'Opensea'} target={`https://opensea.io/collection/${collectionOpenSeaSlug}`} iconLeft={<KibaIcon iconId='ion-cart' />} />)}
              {collectionUrl && (
                <Button variant='tertiary' text={'Website'} target={`https://opensea.io/collection/${collectionUrl}`} iconLeft={<KibaIcon iconId='ion-globe' />} />)}
            </Stack>
            <Stack direction={Direction.Vertical} childAlignment={Alignment.Center} contentAlignment={Alignment.Center} padding={PaddingSize.Wide2}>
              <MarkdownText textVariant='light' source={collectionDescription} />
            </Stack>
          </ContainingView>
        </Stack>
      </BackgroundView>
    </React.Fragment>
  );
};
