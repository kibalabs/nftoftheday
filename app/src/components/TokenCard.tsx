import React from 'react';

import { Alignment, Box, Direction, Image, Stack, Text, TextAlignment } from '@kibalabs/ui-react';

import { CollectionToken } from '../client/resources';

export interface TokenCardProps {
  collectionToken: CollectionToken;
}

const defaultImage = "/assets/icon.png";

export const TokenCard = (props:TokenCardProps): React.ReactElement => {
  return (
    <Box variant='tokenCard' shouldClipContent={true}>
      <Stack direction={Direction.Vertical} isFullWidth={true} childAlignment={Alignment.Center} contentAlignment={Alignment.Center}>
        <Box>
          <Image source={ props.collectionToken.imageUrl || defaultImage} alternativeText='image' fitType='contain' />
        </Box>
        <Text variant='tokenTitle' alignment={TextAlignment.Center}>{props.collectionToken.name}</Text>
        <Text alignment={TextAlignment.Center}>sold 12/12/21 for 0.3</Text>
      </Stack>
    </Box>
  );
};
