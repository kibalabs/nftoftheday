import React from 'react';

import { truncateEnd } from '@kibalabs/core';
import { Alignment, Box, Button, Direction, Image, Media, PaddingSize, Spacing, Stack, Text, TextAlignment } from '@kibalabs/ui-react';

import { CollectionView } from './CollectionView';
import { Collection, CollectionToken } from '../client/resources';

export interface NftCardProps {
  token: CollectionToken;
  collection: Collection;
  label: string;
  subtitle: string;
  secondaryButtonTarget?: string;
  secondaryButtonText?: string
  primaryButtonText?: string;
  extraLabelVariants?: string[];
  extraLabelBoxVariants?: string[];
  error?: Error;
}

export const NftCard = (props: NftCardProps): React.ReactElement => {
  let imageUrl = props.token.imageUrl ?? props.collection.imageUrl ?? 'assets/icon.png';
  if (imageUrl.startsWith('ipfs://')) {
    imageUrl = imageUrl.replace('ipfs://', 'https://pablo-images.kibalabs.com/v1/ipfs/');
  }

  let collectionImageUrl = props.collection.imageUrl;
  if (collectionImageUrl && collectionImageUrl.startsWith('ipfs://')) {
    collectionImageUrl = collectionImageUrl.replace('ipfs://', 'https://pablo-images.kibalabs.com/v1/ipfs/');
  }
  const extraLabelVariantsString = props.extraLabelVariants ? `-${props.extraLabelVariants.join('-')}` : '';
  const extraLabelBoxVariantsString = props.extraLabelBoxVariants ? `-${props.extraLabelBoxVariants.join('-')}` : '';

  return (
    <Box variant='card' shouldClipContent={true}>
      <Stack direction={Direction.Vertical} childAlignment={Alignment.Center}>
        <Stack.Item alignment={Alignment.Start} gutterAfter={PaddingSize.Wide}>
          <Box variant={`cardLabelBox${extraLabelBoxVariantsString}`} isFullWidth={false}>
            <Text variant={`cardLabel${extraLabelVariantsString}`}>{props.label}</Text>
          </Box>
          <Spacing variant={PaddingSize.Wide} />
        </Stack.Item>
        <Stack direction={Direction.Vertical} isFullWidth={true} childAlignment={Alignment.Center} contentAlignment={Alignment.Start} paddingHorizontal={PaddingSize.Wide}>
          <Stack.Item gutterAfter={PaddingSize.Wide2}>
            <Box width='150px' height='150px' shouldClipContent={true}>
              {/* imageUrl.startsWith('data:image/svg+xml;utf8,') ? (
                <div dangerouslySetInnerHTML={{ __html: imageUrl.slice('data:image/svg+xml;utf8,'.length) }} />
              ) : imageUrl.startsWith('data:image/svg+xml;base64,') ? (
                <div dangerouslySetInnerHTML={{ __html: atob(imageUrl.slice('data:image/svg+xml;base64,'.length)) }} /> */}
              { imageUrl.startsWith('http://meebits.larvalabs.com/') ? (
                <Image source={imageUrl} alternativeText={`${props.token.name} image`} fitType='contain' />
              ) : (
                <Media source={imageUrl} alternativeText={`${props.token.name} image`} fitType='contain' />
              )}
            </Box>
          </Stack.Item>
          <Text variant='header3-singleLine' alignment={TextAlignment.Center}>{truncateEnd(props.token.name, 40)}</Text>
          <Text alignment={TextAlignment.Center}>{props.subtitle}</Text>
          <Spacing variant={PaddingSize.Wide} />
          <Stack direction={Direction.Horizontal} childAlignment={Alignment.Center} contentAlignment={Alignment.Center} shouldAddGutters={true}>
            <Text>Part of</Text>
            <CollectionView
              collection={props.collection}
              target={`/collections/${props.collection.address}`}
            />
          </Stack>
          <Spacing variant={PaddingSize.Wide2} />
          <Stack direction={Direction.Horizontal} childAlignment={Alignment.Center} contentAlignment={Alignment.Start} shouldAddGutters={true}>
            {props.secondaryButtonText && props.secondaryButtonTarget && (
              <Stack.Item growthFactor={1} shrinkFactor={1}>
                <Button variant='secondary' text={props.secondaryButtonText} target={props.secondaryButtonTarget} />
              </Stack.Item>
            )}
            {props.primaryButtonText && (
              <Stack.Item growthFactor={1} shrinkFactor={1}>
                <Button
                  variant='primary' text={props.primaryButtonText}
                  target={`/collections/${props.token.registryAddress}/tokens/${props.token.tokenId}`}
                />
              </Stack.Item>
            )}
          </Stack>
          <Spacing variant={PaddingSize.Wide2} />
        </Stack>
      </Stack>
    </Box>
  );
};
