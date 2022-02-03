import React from 'react';

import { Alignment, Box, Direction, Image, PaddingSize, Stack, Text, TextAlignment } from '@kibalabs/ui-react';

import { CollectionToken, TokenTransfer } from '../client/resources';

export interface TokenCardProps {
  collectionToken: CollectionToken;
  tokenTranfer: TokenTransfer;
}

const defaultImage = '/assets/icon.png';

export const TokenCard = (props:TokenCardProps): React.ReactElement => {
  return (
    <Box variant='tokenCard' shouldClipContent={true}>
      <Stack direction={Direction.Vertical} isFullWidth={true} childAlignment={Alignment.Center} contentAlignment={Alignment.Center}>
        <Box height='9rem' width='9rem'>
          <Image source={ props.collectionToken.imageUrl || defaultImage} alternativeText='image' fitType='contain' />
        </Box>
        <Box>
          <Stack direction={Direction.Vertical} childAlignment={Alignment.Center} contentAlignment={Alignment.Center} paddingVertical={PaddingSize.Wide}>
            <Text variant='note' lineLimit={2} alignment={TextAlignment.Center}>{props.collectionToken.name}</Text>
            <Text variant='small' lineLimit={2} alignment={TextAlignment.Center}>{`sold on ${props.tokenTranfer.blockDate} for ${props.tokenTranfer.value}`}</Text>
          </Stack>
        </Box>
      </Stack>
    </Box>
  );
};
