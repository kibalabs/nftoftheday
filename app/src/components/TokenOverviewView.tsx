import React from 'react';

import { Alignment, Box, Direction, PaddingSize, Media, Spacing, Stack, Text, TextAlignment } from '@kibalabs/ui-react';
import { longFormatEther } from '@kibalabs/core';
import { CollectionToken } from '../client/resources';


export interface TokenOverviewViewProps {
  title: string;
  collectionToken: CollectionToken;
}

const defaultImage = '/assets/icon.png';


export const TokenOverviewView = (props: TokenOverviewViewProps): React.ReactElement => {

  let imageUrl = props.collectionToken.imageUrl || defaultImage;
  if (imageUrl?.startsWith('ipfs://')) {
    imageUrl = imageUrl.replace('ipfs://', 'https://pablo-images.kibalabs.com/v1/ipfs/');
  }

  return (
    <Box variant='tokenOverviewViewCard' height='8rem' width='20rem' shouldClipContent={true}>
      <Stack direction={Direction.Vertical} isFullHeight={true} isFullWidth={true} childAlignment={Alignment.Center} contentAlignment={Alignment.Center} padding={PaddingSize.Default}>
        <Text variant='bold' alignment={TextAlignment.Center} lineLimit={2}>{props.title}</Text>
        <Stack direction={Direction.Horizontal} padding={PaddingSize.Default}>
          <Box variant='rounded' height='2rem' width='2rem' shouldClipContent={true}>
          <Media source={imageUrl || defaultImage} alternativeText='image' fitType='cover' />
          </Box>
          <Stack childAlignment={Alignment.Center} contentAlignment={Alignment.Center} paddingLeft={PaddingSize.Default}>
            <Text variant='small' alignment={TextAlignment.Center} lineLimit={2} shouldBreakAnywhere={true}>{props.collectionToken.name}</Text>
          </Stack>
        </Stack>
      </Stack>
    </Box>
  );
};
