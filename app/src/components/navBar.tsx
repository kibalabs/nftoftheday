import React from 'react';

import { Alignment, Box, Button, Direction, Image, PaddingSize, Stack, Text } from '@kibalabs/ui-react';

export const NavBar = (): React.ReactElement => {
  return (
    <Box height='' isFullWidth={true}>
      <Stack direction={Direction.Horizontal} isFullWidth={true} childAlignment={Alignment.Center} contentAlignment={Alignment.Start} shouldAddGutters={true} padding={PaddingSize.Wide1}>
        <Box variant='card' shouldClipContent={true} width='50px' height='50px'>
          <Image source='assets/icon.png' alternativeText='logo' fitType='contain' />
        </Box>
        <Text variant='title'>Token Hunt</Text>
        <Stack direction={Direction.Horizontal} childAlignment={Alignment.Center} contentAlignment={Alignment.End} shouldAddGutters={true} padding={PaddingSize.Wide1}>
          <Button variant='secondary' text= 'Connect Wallet' />
          <Box variant='rounded-borderColored' shouldClipContent={true} height='30px' width='30px'>
            <Image source='assets/icon.png' alternativeText='profile picture' />
          </Box>
          <Text>0x876...988765</Text>
        </Stack>

      </Stack>
    </Box>
  );
};
