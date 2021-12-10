import React from 'react';

import { Alignment, Box, Button, Direction, Image, MarkdownText, Media, PaddingSize, Spacing, Stack, Text, TextAlignment } from '@kibalabs/ui-react';

import { Collection, CollectionToken } from '../client/resources';
import { truncateTitle } from '../titleUtil';

export interface NftCardProps {
  token: CollectionToken;
  collection: Collection;
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
  const title = props.token.name;
  let imageUrl = props.token.imageUrl ?? props.collection.imageUrl ?? 'assets/icon.png';
  if (imageUrl.startsWith('ipfs://')) {
    imageUrl = imageUrl.replace('ipfs://', 'https://ipfs.io/ipfs/');
  }
  const collectionImageUrl = props.collection.imageUrl;
  const collectionTitle = props.collection.name;
  const collectionUrl = props.collection.url ?? (props.collection.openseaSlug ? `https://opensea.io/collections/${props.collection.openseaSlug}` : null);
  const extraLabelVariantsString = props.extraLabelVariants ? `-${props.extraLabelVariants.join('-')}` : '';
  const extraLabelBoxVariantsString = props.extraLabelBoxVariants ? `-${props.extraLabelBoxVariants.join('-')}` : '';

  return (
    <Box variant='card'>
      <Stack direction={Direction.Vertical}>
        <Stack.Item alignment={Alignment.Start} gutterAfter={PaddingSize.Wide}>
          <Box variant={`cardLabelBox${extraLabelBoxVariantsString}`} isFullWidth={false}>
            <Text variant={`cardLabel${extraLabelVariantsString}`}>{props.label}</Text>
          </Box>
          <Spacing variant={PaddingSize.Wide} />
        </Stack.Item>
        {props.error ? (
          <Stack direction={Direction.Vertical} isFullWidth={true} childAlignment={Alignment.Center} contentAlignment={Alignment.Center} paddingHorizontal={PaddingSize.Wide}>
            <Stack.Item alignment={Alignment.Start} gutterAfter={PaddingSize.Wide}>
              <Box width='175px' height='300px'>
                <Text variant='header3'>Sorry, Something went wrong.   </Text>
                <Spacing variant={PaddingSize.Wide} />
                <Text variant='header3'> Please Refresh the page.</Text>
              </Box>
            </Stack.Item>
            <Spacing variant={PaddingSize.Wide} />
          </Stack>
        ) : (
          <Stack direction={Direction.Vertical} isFullWidth={true} childAlignment={Alignment.Center} contentAlignment={Alignment.Start} paddingHorizontal={PaddingSize.Wide}>
            <Stack.Item gutterAfter={PaddingSize.Wide2}>
              <Box width='150px' height='150px'>
                {imageUrl.startsWith('data:image/svg+xml;base64,') ? (
                  <div dangerouslySetInnerHTML={{ __html: atob(imageUrl.slice('data:image/svg+xml;base64,'.length)) }} />
                ) : (
                  <Media source={imageUrl} alternativeText={`${title} image`} fitType='contain' />
                )}
              </Box>
            </Stack.Item>
            <Text variant='header3-singleLine' alignment={TextAlignment.Center}>{truncateTitle(title)}</Text>
            <Text alignment={TextAlignment.Center}>{props.subtitle}</Text>
            <Spacing variant={PaddingSize.Wide} />
            {collectionTitle && (
              <Stack direction={Direction.Horizontal} childAlignment={Alignment.Center} contentAlignment={Alignment.Center} shouldAddGutters={true}>
                {collectionImageUrl && (
                  <Box width='25px' height='25px'>
                    <Image source={collectionImageUrl} alternativeText={collectionTitle} fitType='contain' />
                  </Box>
                )}
                <Stack.Item growthFactor={1} shrinkFactor={1}>
                  {collectionUrl ? (
                    <MarkdownText textVariant='small' source={`Part of [${collectionTitle}](${collectionUrl})`} />
                  ) : (
                    <Text variant='small'>{`Part of ${collectionTitle}`}</Text>
                  )}
                </Stack.Item>
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
