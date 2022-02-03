
import React from 'react';

import { Alignment, Box, Direction, Image, PaddingSize, Stack, Text, TextAlignment } from '@kibalabs/ui-react';

import { CollectionToken } from '../client/resources';

export interface TokenCardProps {
  collectionToken: CollectionToken;
}

export const TokenCard = (props:TokenCardProps): React.ReactElement => {
  return (
    <Stack direction={Direction.Vertical} isFullWidth={true} childAlignment={Alignment.Center} contentAlignment={Alignment.Start} paddingHorizontal={PaddingSize.Wide1}>
      <Box variant='tokenCard' shouldClipContent={true}>
        <Box>
          <Image source={props.collectionToken.imageUrl as string} alternativeText='image' fitType='contain' />
        </Box>
        <Stack direction={Direction.Vertical} padding={PaddingSize.Wide1}>
          <Text variant='tokenTitle' alignment={TextAlignment.Center}>{props.collectionToken.name}</Text>
          <Text alignment={TextAlignment.Center}>sold 12/12/21 for 0.3</Text>
        </Stack>
      </Box>
    </Stack>
  );
};
