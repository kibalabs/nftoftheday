import React from 'react';

import { Alignment, Box, Direction, Image, PaddingSize, Spacing, Stack } from '@kibalabs/ui-react';

import { Account } from './account';

export const NavBar = (): React.ReactElement => {
  return (
    <Box height='64px' isFullWidth={true}>
      <Stack direction={Direction.Horizontal} isFullWidth={true} isFullHeight={true} childAlignment={Alignment.Center} contentAlignment={Alignment.Center} shouldAddGutters={true} padding={PaddingSize.Wide1}>
        <Box shouldClipContent={true} width='40px' height='40px'>
          <Image source='assets/icon.png' alternativeText='logo' fitType='contain' />
        </Box>
        <Image source='assets/wordmark.svg' alternativeText='watermark' fitType='contain' />
        <Stack.Item growthFactor={1} shrinkFactor={1}>
          <Spacing variant={PaddingSize.Wide2} />
        </Stack.Item>
        <Account />
      </Stack>
    </Box>
  );
};
