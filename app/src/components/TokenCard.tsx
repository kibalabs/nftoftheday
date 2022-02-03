import React from 'react';

import { Alignment, Box, Direction, Image, PaddingSize, PaddingView, Stack, Text, TextAlignment } from '@kibalabs/ui-react';

import { CollectionToken } from '../client/resources';

export interface TokenCardProps {
  collectionToken: CollectionToken;
}

const defaultImage = '/assets/icon.png';

export const TokenCard = (props:TokenCardProps): React.ReactElement => {
  return (
    <Box variant='tokenCard' shouldClipContent={true}>
      <Stack direction={Direction.Vertical} isFullWidth={true} childAlignment={Alignment.Center} contentAlignment={Alignment.Center}>
        <Box height='9rem' width='9rem'>
          <Image source={ props.collectionToken.imageUrl || defaultImage} alternativeText='image' fitType='contain' />
        </Box>
        <PaddingView padding={PaddingSize.Wide}>
          <Box>
            <Stack direction={Direction.Vertical} isFullWidth={true} childAlignment={Alignment.Center} contentAlignment={Alignment.Center}>
              <Text variant='subtitle' alignment={TextAlignment.Center}>{props.collectionToken.name}</Text>
              <Text variant='small' alignment={TextAlignment.Center}>sold 12/12/21 for 0.3</Text>
            </Stack>
          </Box>
        </PaddingView>
      </Stack>
    </Box>
  );
};
