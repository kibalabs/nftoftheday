import React from 'react';

import { Alignment, Box, Direction, Image, LinkBase, PaddingSize, Stack, Text } from '@kibalabs/ui-react';

export const Footer = (): React.ReactElement => {
  return (
    <Stack direction={Direction.Vertical} shouldAddGutters={true} childAlignment={Alignment.Center}>
      <LinkBase target='https://www.tokenpage.xyz?ref=tokenhunt'>
        <Stack direction={Direction.Horizontal} childAlignment={Alignment.Center} contentAlignment={Alignment.Center} shouldAddGutters={true} padding={PaddingSize.Default}>
          <Text>Made by</Text>
          <Image variant='rounded' source='/assets/tokenpage.png' alternativeText='TokenPage Logo' width='1.2rem' height='1.2rem' fitType='contain' />
          <Text>Token Page</Text>
        </Stack>
      </LinkBase>
    </Stack>
  );
};
