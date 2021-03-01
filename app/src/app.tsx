import React from 'react';
import { hot } from 'react-hot-loader/root';
import { useFavicon } from '@kibalabs/core-react';
import { BackgroundView, KibaApp, Direction, Stack, Alignment, PaddingSize, Text } from '@kibalabs/ui-react';

import { buildNotdTheme } from './theme';

const theme = buildNotdTheme();

export const App = hot((): React.ReactElement => {
  useFavicon('/assets/favicon.svg');

  return (
    <KibaApp theme={theme}>
      <BackgroundView linearGradient='#E56B6F, #6D597A'>
        <Stack direction={Direction.Vertical} isFullWidth={true} isFullHeight={true} childAlignment={Alignment.Center} paddingStart={PaddingSize.Wide3} paddingEnd={PaddingSize.Wide3}>
          <Text>Hello world!</Text>
        </Stack>
      </BackgroundView>
    </KibaApp>
  );
});
