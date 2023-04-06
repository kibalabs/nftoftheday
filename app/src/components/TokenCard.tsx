import React from 'react';

import { truncateStart } from '@kibalabs/core';
import { Alignment, Box, Direction, LinkBase, Media, PaddingSize, Stack, Text, TextAlignment } from '@kibalabs/ui-react';

import { CollectionToken } from '../client/resources';

export interface TokenCardProps {
  collectionToken: CollectionToken;
  subtitle?: string
  onClicked?: (collectionToken: CollectionToken) => void;
  target?: string;
}

const defaultImage = '/assets/icon.png';

export const TokenCard = (props:TokenCardProps): React.ReactElement => {
  const onClicked = (): void => {
    if (props.onClicked) {
      props.onClicked(props.collectionToken);
    }
  };

  let imageUrl = props.collectionToken?.imageUrl || defaultImage;
  if (imageUrl?.startsWith('ipfs://')) {
    imageUrl = imageUrl.replace('ipfs://', 'https://pablo-images.kibalabs.com/v1/ipfs/');
  }

  return (
    <LinkBase onClicked={onClicked} target={props.target}>
      <Box variant='tokenCard' shouldClipContent={true}>
        <Stack direction={Direction.Vertical} isFullWidth={true} childAlignment={Alignment.Center} contentAlignment={Alignment.Center}>
          <Box variant='unrounded' height='11rem' width='11rem' shouldClipContent={true}>
            <Media source={ imageUrl || defaultImage} alternativeText='image' fitType='cover' />
          </Box>
          <Box>
            <Stack direction={Direction.Vertical} childAlignment={Alignment.Center} contentAlignment={Alignment.Center} padding={PaddingSize.Wide}>
              <Text variant='bold' alignment={TextAlignment.Center}>{truncateStart(props.collectionToken.name, 15)}</Text>
              { props.subtitle && (
                <Text variant='small' lineLimit={2} alignment={TextAlignment.Center}>{props.subtitle}</Text>
              )}
            </Stack>
          </Box>
        </Stack>
      </Box>
    </LinkBase>
  );
};
