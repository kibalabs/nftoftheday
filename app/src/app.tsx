import React from 'react';

import { dateFromString, dateToString, LocalStorageClient, Requester } from '@kibalabs/core';
import { useFavicon } from '@kibalabs/core-react';
import { EveryviewTracker } from '@kibalabs/everyview-tracker';
import { Alignment, BackgroundView, Button, Container, Direction, EqualGrid, IconButton, KibaApp, KibaIcon, MarkdownText, PaddingSize, Spacing, Stack, Text } from '@kibalabs/ui-react';
import { Helmet } from 'react-helmet';
// eslint-disable-next-line import/no-extraneous-dependencies
import { hot } from 'react-hot-loader/root';

import { NotdClient } from './client/client';
import { Token, TokenTransfer, UiData } from './client/resources';
import { HighestPricedTokenTransferCard } from './components/highestPricedTokenTransferCard';
import { MostTradedTokenTransferCard } from './components/mostTradedTokenTransferCard';
import { RandomTokenTransferCard } from './components/randomTokenTransferCard';
import { SponsoredTokenCard } from './components/sponsoredTokenCard';
import { GlobalsProvider } from './globalsContext';
import { buildNotdTheme } from './theme';
import './fonts.css';

const theme = buildNotdTheme();

const requester = new Requester();
const notdClient = new NotdClient(requester, 'http://localhost:5000');
const localStorageClient = new LocalStorageClient(window.localStorage);
const tracker = new EveryviewTracker('017285d5fef9449783000125f2d5d330');
tracker.trackApplicationOpen();

const globals = {
  requester,
  notdClient,
  localStorageClient,
};

const defaultDate = new Date();
defaultDate.setHours(0, 0, 0, 0);


export const App = hot((): React.ReactElement => {
  useFavicon('/assets/favicon.svg');
  const [highestPricedTokenTransfer, setHighestPricedTokenTransfer] = React.useState<TokenTransfer | null>(null);
  const [randomTokenTransfer, setRandomTokenTransfer] = React.useState<TokenTransfer | null>(null);
  const [mostTradedTokenTransfers, setMostTradedTokenTransfers] = React.useState<TokenTransfer[] | null>(null);
  const [sponsoredToken, setSponsoredToken] = React.useState<Token | null>(null);

  const getUrlDate = (key: string): Date | null => {
    const searchParams = new URLSearchParams(window.location.search);
    const value = searchParams.get(key);
    try {
      return dateFromString(value, 'yyyy-MM-dd');
    } catch {
      // No-op
    }
    return null;
  };
  const [startDate, setStartDate] = React.useState<Date | null>(getUrlDate('date') || defaultDate);

  const setUrlString = (key: string, value: string): void => {
    const searchParams = new URLSearchParams(window.location.search);
    if (value === null || value === undefined) {
      searchParams.delete(key);
    } else {
      searchParams.set(key, value);
    }
    window.history.replaceState({}, '', `${window.location.pathname}?${searchParams.toString()}`);
  };

  const getUrlDateString = React.useCallback((): string | null => {
    const currentDate = new Date();
    if (startDate.getDate() === currentDate.getDate()) {
      return null;
    }
    return dateToString(startDate, 'yyyy-MM-dd');
  }, [startDate]);

  React.useEffect((): void => {
    setHighestPricedTokenTransfer(null);
    setRandomTokenTransfer(null);
    setMostTradedTokenTransfers(null);
    setSponsoredToken(null);
    setUrlString('date', getUrlDateString());

    notdClient.retrieveUiData(startDate).then((uiData: UiData): void => {
      setHighestPricedTokenTransfer(uiData.highestPricedTokenTransfer);
      setRandomTokenTransfer(uiData.randomTokenTransfer);
      setMostTradedTokenTransfers(uiData.mostTradedTokenTransfers);
      setSponsoredToken(uiData.sponsoredToken);
    });
  }, [getUrlDateString, startDate]);

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

  const getTitleDateString = (): string => {
    const currentDate = new Date();
    if (startDate.getDate() === currentDate.getDate()) {
      return '';
    }
    return `| ${dateToString(startDate, 'dd MMMM yyyy')}`;
  };

  const onBackClicked = (): void => {
    const newDate = new Date(startDate);
    newDate.setDate(newDate.getDate() - 1);
    newDate.setHours(0, 0, 0, 0);
    setStartDate(newDate);
  };

  const onForwardClicked = (): void => {
    const newDate = new Date(startDate);
    newDate.setDate(newDate.getDate() + 1);
    newDate.setHours(0, 0, 0, 0);
    setStartDate(newDate);
  };

  return (
    <KibaApp theme={theme}>
      <GlobalsProvider globals={globals}>
        <Helmet>
          <title>{`Token Hunt ${getTitleDateString()}`}</title>
        </Helmet>
        <BackgroundView linearGradient='#200122,#6F0000'>
          <Stack direction={Direction.Vertical} isFullWidth={true} isFullHeight={true} childAlignment={Alignment.Center} contentAlignment={Alignment.Start} isScrollableVertically={true}>
            <Spacing variant={PaddingSize.Wide3} />
            <Text variant='header1'>NFT of the day</Text>
            <Spacing variant={PaddingSize.Default} />
            <Stack direction={Direction.Horizontal} childAlignment={Alignment.Center} contentAlignment={Alignment.Start} shouldAddGutters={true}>
              <IconButton icon={<KibaIcon iconId='ion-chevron-back' />} onClicked={onBackClicked} isEnabled={startDate > new Date(2021, 0, 1) } />
              <Text variant='header3'>{getDateString()}</Text>
              <IconButton icon={<KibaIcon iconId='ion-chevron-forward' />} onClicked={onForwardClicked} isEnabled={startDate < defaultDate} />
            </Stack>
            <Stack.Item growthFactor={1} shrinkFactor={1}>
              <Spacing variant={PaddingSize.Wide3} />
            </Stack.Item>
            <Container isFullHeight={false}>
              <EqualGrid isFullHeight={false} childSizeResponsive={{ base: 12, small: 6, large: 4, extraLarge: 3 }} contentAlignment={Alignment.Center} childAlignment={Alignment.Center} shouldAddGutters={true}>
                <RandomTokenTransferCard tokenTransfer={randomTokenTransfer} />
                <HighestPricedTokenTransferCard tokenTransfer={highestPricedTokenTransfer} />
                <MostTradedTokenTransferCard tokenTransfers={mostTradedTokenTransfers} />
                <SponsoredTokenCard token={sponsoredToken} />
              </EqualGrid>
            </Container>
            <Stack.Item growthFactor={1} shrinkFactor={1}>
              <Spacing variant={PaddingSize.Wide3} />
            </Stack.Item>
            <Text>Get your daily dose on:</Text>
            <Spacing variant={PaddingSize.Narrow} />
            <Stack direction={Direction.Horizontal} childAlignment={Alignment.Center} contentAlignment={Alignment.Start} shouldAddGutters={true}>
              <Stack.Item growthFactor={1} shrinkFactor={1}>
                <Button variant='tertiary' text={'Twitter'} target={'https://twitter.com/tokenhunt'} iconLeft={<KibaIcon iconId='feather-twitter' />} />
              </Stack.Item>
              <Stack.Item growthFactor={1} shrinkFactor={1}>
                <Button variant='tertiary' text={'Instagram'} target={'https://instagram.com/tokenhunt'} iconLeft={<KibaIcon iconId='feather-instagram' />} />
              </Stack.Item>
            </Stack>
            <Spacing />
            <Spacing />
            <MarkdownText textVariant='light' source='Data provided by [OpenSea](https://opensea.io/). Made by [krishan711](https://twitter.com/krishan711)' />
            <Spacing variant={PaddingSize.Narrow} />
          </Stack>
        </BackgroundView>
      </GlobalsProvider>
    </KibaApp>
  );
});
