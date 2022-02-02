
import React from 'react';

import { Box, Direction, Image, PaddingSize, Spacing, Stack, Text, TextAlignment } from '@kibalabs/ui-react';

export const TokenCard = (): React.ReactElement => {
  return (
    <Stack direction={Direction.Vertical} isFullHeight={true} isFullWidth={true} padding={PaddingSize.Wide}>
      <Text variant='header3-singleLine'>Your Holdings</Text>
      <Spacing variant={PaddingSize.Wide} />
      <Box variant='card' height='204px' width='140px'>
        <Box height='140px' width='140px'>
          <Image source={'/assets/icon.png'} alternativeText='image' fitType='contain' />
        </Box>
        <Spacing variant={PaddingSize.Wide} />
        <Text variant='subtitle' alignment={TextAlignment.Center}>mdtp</Text>
        <Text variant='small' alignment={TextAlignment.Center}>bought on 12/12/21 for 0.3</Text>
      </Box>
      <Spacing variant={PaddingSize.Wide} />
      <Text variant='bold'>Connect your wallet to show your holdings and watchlist.</Text>
    </Stack>
  );
};
