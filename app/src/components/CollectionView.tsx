import React from 'react';

import { Alignment, Box, Direction, Image, Stack, Text } from '@kibalabs/ui-react';

import { Collection } from '../client/resources';

export interface CollectionViewProps {
  collection: Collection;
}
const defaultImage = '/assets/icon.png';

export const CollectionView = (props: CollectionViewProps): React.ReactElement => {
  return (
    <Stack direction={Direction.Horizontal} childAlignment={Alignment.Center} contentAlignment={Alignment.Center} shouldAddGutters={true}>
      <Text>Part of</Text>
      <Box variant='rounded-borderColored' shouldClipContent={true} height='20px' width='20px'>
        <Image source= {props.collection.imageUrl || defaultImage} alternativeText='Avatar' />
      </Box>
      <Text>{props.collection.name}</Text>
    </Stack>
  );
};
