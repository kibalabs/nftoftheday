import React from 'react';

import { dateToString, Requester } from '@kibalabs/core';
import { useFavicon } from '@kibalabs/core-react';
import { Alignment, BackgroundView, Direction, EqualGrid, KibaApp, LoadingSpinner, MarkdownText, PaddingSize, Spacing, Stack, Text } from '@kibalabs/ui-react';
// eslint-disable-next-line import/no-extraneous-dependencies
import { hot } from 'react-hot-loader/root';

import { NotdClient } from './client/client';
import { TokenTransfer, UiData } from './client/resources';
import { HighestPricedTokenTransferCard } from './components/highestPricedTokenTransferCard';
import { MostTradedTokenTransferCard } from './components/mostTradedTokenTransferCard';
import { buildNotdTheme } from './theme';
import './fonts.css';

const theme = buildNotdTheme();

const requester = new Requester();
const notdClient = new NotdClient(requester, 'http://localhost:5000');

const defaultDate = new Date();
defaultDate.setHours(0, 0, 0, 0);

export const App = hot((): React.ReactElement => {
  useFavicon('/assets/favicon.svg');
  const [highestPricedTokenTransfer, setHighestPricedTokenTransfer] = React.useState<TokenTransfer | null>(null);
  const [mostTradedTokenTransfers, setMostTradedTokenTransfers] = React.useState<TokenTransfer[] | null>(null);
  const [startDate] = React.useState<Date | null>(defaultDate);

  React.useEffect((): void => {
    notdClient.retrieveUiData(startDate).then((uiData: UiData): void => {
      setHighestPricedTokenTransfer(uiData.highestPricedTokenTransfer);
      setMostTradedTokenTransfers(uiData.mostTradedTokenTransfers);
    });
  }, [startDate]);

  const getDateString = (): string => {
    const currentDate = new Date();
    if (startDate.getDate() === currentDate.getDate()) {
      return 'Today';
    }
    if (startDate.getDate() === new Date(currentDate.setDate(currentDate.getDate() - 1)).getDate()) {
      return 'Yesterday';
    }
    return dateToString(startDate, 'dd MMMM yyyy');
  };

  return (
    <KibaApp theme={theme}>
      <BackgroundView linearGradient='#200122,#6F0000'>
        <Stack direction={Direction.Vertical} isFullWidth={true} isFullHeight={true} childAlignment={Alignment.Center} contentAlignment={Alignment.Start} isScrollableVertically={true}>
          <Spacing variant={PaddingSize.Wide3} />
          <Text variant='header1'>NFT of the day</Text>
          <Spacing variant={PaddingSize.Default} />
          <Text variant='header3'>{getDateString()}</Text>
          <Stack.Item growthFactor={1} shrinkFactor={1}>
            <Spacing variant={PaddingSize.Wide3} />
          </Stack.Item>
          {/* {!highestPricedTokenTransfer ? (
            <LoadingSpinner variant='light-large' />
          ) : ( */}
            <EqualGrid isFullHeight={false} childSizeResponsive={{ base: 12, small: 6, medium: 5, large: 4, extraLarge: 3 }} contentAlignment={Alignment.Center} shouldAddGutters={true}>
              <HighestPricedTokenTransferCard tokenTransfer={highestPricedTokenTransfer} />
              <MostTradedTokenTransferCard tokenTransfers={mostTradedTokenTransfers} />
            </EqualGrid>
          {/* )} */}
          <Stack.Item growthFactor={1} shrinkFactor={1}>
            <Spacing variant={PaddingSize.Wide3} />
          </Stack.Item>
          <MarkdownText source='Made by [Kiba Labs](https://www.kibalabs.com)' />
          <Spacing variant={PaddingSize.Narrow} />
        </Stack>
      </BackgroundView>
    </KibaApp>
  );
});
