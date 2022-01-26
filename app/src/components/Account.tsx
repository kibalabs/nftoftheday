import React from 'react';

import { Alignment, Box, Button, Direction, Image, Stack, Text } from '@kibalabs/ui-react';

export const Account = (): React.ReactElement => {
  return (
    <Stack direction={Direction.Horizontal} childAlignment={Alignment.Center} contentAlignment={Alignment.Center} shouldAddGutters={true}>
      <Button variant='secondary' text= 'Connect Wallet' />
      <Box variant='rounded-borderColored' shouldClipContent={true} height='20px' width='20px'>
        <Image source='/assets/icon.png' alternativeText='Avatar' />
      </Box>
      <Text>0x876...988765</Text>
    </Stack>
  );
};
