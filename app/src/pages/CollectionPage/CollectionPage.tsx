import React from 'react';

import { useRouteParams } from '@kibalabs/core-react';
import { Alignment, Box, Button, ContainingView, Direction, EqualGrid, Image, KibaIcon, LayerContainer, LoadingSpinner, MarkdownText, PaddingSize, Spacing, Stack, Text } from '@kibalabs/ui-react';

import { Collection } from '../../client/resources';
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
          <Spacing variant={PaddingSize.Wide2} />
          <ContainingView>
          <Stack direction={Direction.Vertical} isFullWidth={true} childAlignment={Alignment.Center} padding={PaddingSize.Wide2}>
          <Text variant='header1'>{collection.name}</Text>
            <Spacing variant={PaddingSize.Wide2} />
          <EqualGrid childSizeResponsive={{ base: 12, small: 6, large: 3, extraLarge: 2 }} isFullHeight={false} shouldAddGutters={true}>
              {collection.discordUrl && (
                <Button variant='tertiary' text= 'Discord' iconLeft={<KibaIcon iconId='ion-logo-discord' />} target={collection.discordUrl} />
              )}                       
              {collection.instagramUsername && (
                <Button variant='tertiary' text={'Instagram'} target={`https://instagram.com/${collection.instagramUsername}`} iconLeft={<KibaIcon iconId='feather-instagram' />} />
              )}                                     
              {collection.twitterUsername && (
                <Button variant='tertiary' text={'Twitter'} target={`https://instagram.com/${collection.twitterUsername}`} iconLeft={<KibaIcon iconId='feather-twitter' />} />
              )}
              {collection.openseaSlug && (
                <Button variant='tertiary' text={'Opensea'} target={`https://opensea.io/collection/${collection.openseaSlug}`} iconLeft={<KibaIcon iconId='ion-cart' />} />
              )}
              {collection.url && (
                <Button variant='tertiary' text={'Website'} target={`https://opensea.io/collection/${collection.url}`} iconLeft={<KibaIcon iconId='ion-globe' />} />
              )}
              </EqualGrid>
            <Spacing variant={PaddingSize.Wide2} />
            {collection.description && (
              <MarkdownText textVariant='light' source={collection.description} />
            )}
            </Stack>
          </ContainingView>
        </Stack>
      )}
    </Stack>
  );
};
