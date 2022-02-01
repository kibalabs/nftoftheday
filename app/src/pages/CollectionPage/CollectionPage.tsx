import React from 'react';

import { useRouteParams } from '@kibalabs/core-react';
import { Alignment, Box, Button, ContainingView, Direction, Image, KibaIcon, LayerContainer, LoadingSpinner, PaddingSize, ResponsiveHidingView, ScreenSize, Spacing, Stack, Text } from '@kibalabs/ui-react';

import { Collection } from '../../client/resources';
import { MetricView } from '../../components/MetricView';
import { TruncateText } from '../../components/TruncateText';
import { useGlobals } from '../../globalsContext';

export const CollectionPage = (): React.ReactElement => {
  const { notdClient } = useGlobals();
  const [collection, setCollection] = React.useState<Collection | null>(null);
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
    <Stack direction={Direction.Vertical} isFullWidth={true} isFullHeight={true} childAlignment={Alignment.Center} contentAlignment={Alignment.Start}>
      {collection === null ? (
        <LoadingSpinner />
      ) : collection === undefined ? (
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
            <Stack direction={Direction.Vertical} isFullWidth={true} childAlignment={Alignment.Center}>
              <Text variant='header1'>{collection.name}</Text>
              <Spacing variant={PaddingSize.Wide2} />
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
              <Stack directionResponsive={{ base: Direction.Vertical, medium: Direction.Horizontal }} isFullWidth={true} childAlignment={Alignment.Center} contentAlignment={Alignment.Center}>
                <Stack direction={Direction.Horizontal} childAlignment={Alignment.Center} contentAlignment={Alignment.Center} shouldAddGutters={true} paddingHorizontal={PaddingSize.Wide2}>
                  <MetricView name={'Items'} value={10000} />
                  <Spacing variant={PaddingSize.Wide1} />
                  <MetricView name={'owners'} value={5432} />
                  <Spacing variant={PaddingSize.Wide1} />
                  <MetricView name={'Total Volume'} value={140} />
                </Stack>
                <ResponsiveHidingView hiddenBelow={ScreenSize.Medium}>
                  <Box variant='divider' isFullHeight={true} width='1px' />
                </ResponsiveHidingView>
                <Stack direction={Direction.Horizontal} childAlignment={Alignment.Center} contentAlignment={Alignment.Center} shouldAddGutters={true} padding={PaddingSize.Wide2}>
                  <MetricView name={'24h low sale'} value={2.5} />
                  <Spacing variant={PaddingSize.Wide1} />
                  <MetricView name={'24h high sale'} value={150} />
                  <Spacing variant={PaddingSize.Wide1} />
                  <MetricView name={'24h volume'} value={350} />
                </Stack>
              </Stack>
            </Stack>
          </ContainingView>
        </Stack>
      )}
    </Stack>
  );
};
