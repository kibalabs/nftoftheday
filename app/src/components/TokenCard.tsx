
import React from 'react';


import { Alignment, Box, Direction, Image, LoadingSpinner, Stack, Text, TextAlignment } from '@kibalabs/ui-react';

import { CollectionToken } from '../client/resources';

export interface TokenCardProps {
  collectionToken: CollectionToken;
}

export const TokenCard = (props:TokenCardProps): React.ReactElement => {
  return (
    <Box variant='card'>
      {CollectionToken === null ? (
        <LoadingSpinner />
      ) : CollectionToken === undefined ? (
        <Text variant='error'>Token failed to load</Text>
      ) : (
        <Stack direction={Direction.Vertical} isFullWidth={true} childAlignment={Alignment.Center} contentAlignment={Alignment.Start}>
          <Box>
            <Image source={props.collectionToken.imageUrl as string} alternativeText='image' fitType='contain' />
          </Box>
          <Text variant='tokenTitle' alignment={TextAlignment.Center}>{props.collectionToken.name}</Text>
          <Text alignment={TextAlignment.Center}>{props.collectionToken.description}</Text>
        </Stack>
      )}
    </Box>
  );
};
