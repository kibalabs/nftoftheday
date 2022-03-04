import React from 'react';

import { Alignment, Box, Direction, Image, LinkBase, Stack, Text } from '@kibalabs/ui-react';

import { Collection } from '../client/resources';

export interface CollectionViewProps {
  collection: Collection;
  onClicked?: (collection: Collection) => void;
  target?: string;
}
const defaultImage = '/assets/icon.png';

export const CollectionView = (props: CollectionViewProps): React.ReactElement => {
  const onClicked = (): void => {
    if (props.onClicked) {
      props.onClicked(props.collection);
    }
  };

  return (
    <LinkBase onClicked={onClicked} target={props.target}>
      <Stack direction={Direction.Horizontal} childAlignment={Alignment.Center} contentAlignment={Alignment.Center} shouldAddGutters={true}>
        <Box variant='rounded-borderColored' shouldClipContent={true} height='20px' width='20px'>
          <Image source= {props.collection.imageUrl || defaultImage} alternativeText='Avatar' />
        </Box>
        <Text>{props.collection.name}</Text>
      </Stack>
    </LinkBase>

  );
};
