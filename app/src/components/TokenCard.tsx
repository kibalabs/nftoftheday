import React from 'react';

import { Alignment, Box, Direction, Image, LinkBase, PaddingSize, Stack, Text, TextAlignment } from '@kibalabs/ui-react';

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

  return (
    <LinkBase onClicked={onClicked} target={props.target}>
      <Box variant='tokenCard' shouldClipContent={true}>
        <Stack direction={Direction.Vertical} isFullWidth={true} childAlignment={Alignment.Center} contentAlignment={Alignment.Center}>
          <Box height='11rem' width='11rem'>
            <Image source={ props.collectionToken.imageUrl || defaultImage} alternativeText='image' fitType='contain' />
          </Box>
          <Box>
            <Stack direction={Direction.Vertical} childAlignment={Alignment.Center} contentAlignment={Alignment.Center} padding={PaddingSize.Wide}>
              <Text variant='bold' lineLimit={2} alignment={TextAlignment.Center}>{props.collectionToken.name}</Text>
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