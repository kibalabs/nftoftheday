import React from 'react';

import { Alignment, Box, Direction, PaddingSize, Media, Spacing, Stack, Text, TextAlignment } from '@kibalabs/ui-react';
import { dateToRelativeShortString, dateToString, longFormatEther, shortFormatEther } from '@kibalabs/core';


export interface TokenOverviewViewProps {
  title: string;
  imageUrl: string;
  value: number
  name: string;
}

const defaultImage = '/assets/icon.png';


export const TokenOverviewView = (props: TokenOverviewViewProps): React.ReactElement => {

  let imageUrl = props.imageUrl || defaultImage;
  if (imageUrl?.startsWith('ipfs://')) {
    imageUrl = imageUrl.replace('ipfs://', 'https://pablo-images.kibalabs.com/v1/ipfs/');
  }

  return (
    <Box variant='tokenOverviewViewCard' height='5rem' width='15rem' shouldClipContent={true}>
      <Stack direction={Direction.Vertical} isFullHeight={true} isFullWidth={true} childAlignment={Alignment.Center} contentAlignment={Alignment.Center} padding={PaddingSize.Default}>
        <Text variant='bold' alignment={TextAlignment.Center} lineLimit={2}>{props.title}</Text>
        <Spacing variant={PaddingSize.Narrow} />
        <Stack direction={Direction.Horizontal} isFullHeight={true} isFullWidth={true} childAlignment={Alignment.Center} contentAlignment={Alignment.Center} padding={PaddingSize.Default}>
          <Box variant='rounded' height='2rem' width='2rem' shouldClipContent={true}>
            <Media source={imageUrl || defaultImage} alternativeText='image' fitType='cover' />
          </Box>
          <Stack direction={Direction.Vertical} isFullHeight={true} isFullWidth={true} childAlignment={Alignment.Center} contentAlignment={Alignment.Center} padding={PaddingSize.Default}>
            <Text variant='small' alignment={TextAlignment.Center} lineLimit={2} shouldBreakAnywhere={true}>{props.name}</Text>
            <Spacing variant={PaddingSize.Narrow} />
            <Text variant='small' alignment={TextAlignment.Center} lineLimit={2} shouldBreakAnywhere={true}>{longFormatEther(BigInt(props.value.toString()))}</Text>
          </Stack>
        </Stack>
      </Stack>
    </Box>
  );
};
