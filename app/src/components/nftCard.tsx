import React from 'react';

import { Alignment, Box, Button, Direction, Image, LoadingSpinner, MarkdownText, Media, PaddingSize, Spacing, Stack, Text, TextAlignment } from '@kibalabs/ui-react';

import { Collection, CollectionToken } from '../client/resources';
import { useGlobals } from '../globalsContext';
import { truncateTitle } from '../titleUtil';

export interface NftCardProps {
  tokenId: string;
  collectionAddress: string;
  label: string;
  subtitle: string;
  secondaryButtonTarget?: string;
  secondaryButtonText?: string
  primaryButtonTarget?: string;
  primaryButtonText?: string;
  extraLabelVariants?: string[];
  extraLabelBoxVariants?: string[];
  error?: Error;
}

export const NftCard = (props: NftCardProps): React.ReactElement => {
  const { notdClient } = useGlobals();
  const [asset, setAsset] = React.useState<CollectionToken | null>(null);
  const [collection, setCollection] = React.useState<Collection | null>(null);
  const [isLoading, setIsLoading] = React.useState<boolean>(false);
  const [error, setError] = React.useState<Error | null>(null);

  const updateAsset = React.useCallback(async (): Promise<void> => {
    if (!props.collectionAddress || !props.tokenId) {
      setAsset(null);
      return;
    }
    setIsLoading(true);
    try {
      const tokenPromise = notdClient.retrieveCollectionToken(props.collectionAddress, props.tokenId);
      const collectionPromise = notdClient.retrieveCollection(props.collectionAddress);
      setAsset(await tokenPromise);
      setCollection(await collectionPromise);
    } catch (apiError: unknown) {
      setError(apiError as Error);
    }
    setIsLoading(false);
  }, [notdClient, props.collectionAddress, props.tokenId]);

  React.useEffect((): void => {
    updateAsset();
  }, [updateAsset]);

  let imageUrl = asset?.imageUrl ?? collection?.imageUrl ?? 'assets/icon.png';
  if (imageUrl.startsWith('ipfs://')) {
    imageUrl = imageUrl.replace('ipfs://', 'https://ipfs.io/ipfs/');
  }

  let collectionImageUrl = collection?.imageUrl;
  if (collectionImageUrl && collectionImageUrl.startsWith('ipfs://')) {
    collectionImageUrl = collectionImageUrl.replace('ipfs://', 'https://ipfs.io/ipfs/');
  }
  const collectionUrl = collection?.url ?? (collection?.openseaSlug ? `https://opensea.io/collections/${collection?.openseaSlug}` : null);
  const extraLabelVariantsString = props.extraLabelVariants ? `-${props.extraLabelVariants.join('-')}` : '';
  const extraLabelBoxVariantsString = props.extraLabelBoxVariants ? `-${props.extraLabelBoxVariants.join('-')}` : '';

  return (
    <Box variant='card'>
      <Stack direction={Direction.Vertical} childAlignment={Alignment.Center}>
        <Stack.Item alignment={Alignment.Start} gutterAfter={PaddingSize.Wide}>
          <Box variant={`cardLabelBox${extraLabelBoxVariantsString}`} isFullWidth={false}>
            <Text variant={`cardLabel${extraLabelVariantsString}`}>{props.label}</Text>
          </Box>
          <Spacing variant={PaddingSize.Wide} />
        </Stack.Item>
        {error ? (
          <Text>{error.message}</Text>
        ) : !props.collectionAddress || !props.tokenId || isLoading || !asset || !collection ? (
          <Stack padding={PaddingSize.Wide3}>
            <LoadingSpinner variant='light' />
          </Stack>
        ) : (
          <Stack direction={Direction.Vertical} isFullWidth={true} childAlignment={Alignment.Center} contentAlignment={Alignment.Start} paddingHorizontal={PaddingSize.Wide}>
            <Stack.Item gutterAfter={PaddingSize.Wide2}>
              <Box width='150px' height='150px' shouldClipContent={true}>
                {imageUrl.startsWith('data:image/svg+xml;utf8,') ? (
                  <div dangerouslySetInnerHTML={{ __html: imageUrl.slice('data:image/svg+xml;utf8,'.length) }} />
                ) : imageUrl.startsWith('data:image/svg+xml;base64,') ? (
                  <Image source={imageUrl}alternativeText={`${asset.name} image`} />
                ) : imageUrl.startsWith('http://meebits.larvalabs.com/') ? (
                  <Image source={imageUrl} alternativeText={`${asset.name} image`} fitType='contain' />
                ) : (
                  <Media source={imageUrl} alternativeText={`${asset.name} image`} fitType='contain' />
                )}
              </Box>
            </Stack.Item>
            <Text variant='header3-singleLine' alignment={TextAlignment.Center}>{truncateTitle(asset.name)}</Text>
            <Text alignment={TextAlignment.Center}>{props.subtitle}</Text>
            <Spacing variant={PaddingSize.Wide} />
            {collection.name && (
              <Stack direction={Direction.Horizontal} childAlignment={Alignment.Center} contentAlignment={Alignment.Center} shouldAddGutters={true}>
                {collectionImageUrl && (
                  <Box width='25px' height='25px'>
                    <Image source={collectionImageUrl} alternativeText='' fitType='contain' />
                  </Box>
                )}
                {collection && collection.name && (
                  <Stack.Item growthFactor={1} shrinkFactor={1}>
                    {collectionUrl ? (
                      <MarkdownText textVariant='small' source={`Part of [${collection.name}](${collectionUrl})`} />
                    ) : (
                      <Text variant='small'>{`Part of ${collection.name}`}</Text>
                    )}
                  </Stack.Item>
                )}
              </Stack>
            )}
            <Spacing variant={PaddingSize.Wide2} />
            <Stack direction={Direction.Horizontal} childAlignment={Alignment.Center} contentAlignment={Alignment.Start} shouldAddGutters={true}>
              {props.secondaryButtonText && props.secondaryButtonTarget && (
                <Stack.Item growthFactor={1} shrinkFactor={1}>
                  <Button variant='secondary' text={props.secondaryButtonText} target={props.secondaryButtonTarget} />
                </Stack.Item>
              )}
              {props.primaryButtonText && props.primaryButtonTarget && (
                <Stack.Item growthFactor={1} shrinkFactor={1}>
                  <Button variant='primary' text={props.primaryButtonText} target={props.primaryButtonTarget} />
                </Stack.Item>
              )}
            </Stack>
            <Spacing variant={PaddingSize.Wide2} />
          </Stack>
        )}
      </Stack>
    </Box>
  );
};
