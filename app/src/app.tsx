import React from 'react';

import { dateFromString, dateToString, LocalStorageClient, Requester } from '@kibalabs/core';
import { useFavicon } from '@kibalabs/core-react';
import { EveryviewTracker } from '@kibalabs/everyview-tracker';
import { Alignment, BackgroundView, Box, Button, ContainingView, Direction, EqualGrid, IconButton, KibaApp, KibaIcon, Link, MarkdownText, PaddingSize, Spacing, Stack, Text } from '@kibalabs/ui-react';
import { Helmet } from 'react-helmet';

import { NotdClient } from './client/client';
import { Token, TokenTransfer, UiData } from './client/resources';
import { EmailSubsriptionPopup } from './components/emailSubcriptionPopup';
import { HighestPricedTokenTransferCard } from './components/highestPricedTokenTransferCard';
import { MostTradedTokenTransferCard } from './components/mostTradedTokenTransferCard';
import { RandomTokenTransferCard } from './components/randomTokenTransferCard';
import { SponsoredTokenCard } from './components/sponsoredTokenCard';
import { isToday, isYesterday } from './dateUtil';
import { GlobalsProvider } from './globalsContext';
import { numberWithCommas } from './numberUtil';
import { buildNotdTheme } from './theme';
import './fonts.css';

const theme = buildNotdTheme();

const API_URL = 'https://notd-api.kibalabs.com';
// const API_URL = 'http://localhost:5000';

const requester = new Requester();
const notdClient = new NotdClient(requester, API_URL);
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

export const App = (): React.ReactElement => {
  useFavicon('/assets/favicon.svg');
  const [isEmailPopupShowing, setIsEmailPopopShowing] = React.useState(false);
  const [highestPricedTokenTransfer, setHighestPricedTokenTransfer] = React.useState<TokenTransfer | null>(null);
  const [randomTokenTransfer, setRandomTokenTransfer] = React.useState<TokenTransfer | null>(null);
  const [mostTradedTokenTransfers, setMostTradedTokenTransfers] = React.useState<TokenTransfer[] | null>(null);
  const [sponsoredToken, setSponsoredToken] = React.useState<Token | null>(null);
  const [transactionCount, setTransactionCount] = React.useState<number | null>(null);
  const [error, setError] = React.useState<boolean>(false);

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
    if (isToday(startDate)) {
      return null;
    }
    return dateToString(startDate, 'yyyy-MM-dd');
  }, [startDate]);

  const getDateString = (): string => {
    if (isToday(startDate)) {
      return 'Today';
    }
    if (isYesterday(startDate)) {
      return 'Yesterday';
    }
    return dateToString(startDate, 'dd MMMM yyyy');
  };

  const getTitleDateString = (): string => {
    if (isToday(startDate)) {
      return '';
    }
    return `| ${dateToString(startDate, 'dd MMMM yyyy')}`;
  };

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
      setTransactionCount(uiData.transactionCount);
    }).catch(() => {
      setError(true);
    });
  }, [getUrlDateString, startDate]);

  const onBackClicked = (): void => {
    const newDate = new Date(startDate);
    newDate.setDate(newDate.getDate() - 1);
    newDate.setHours(0, 0, 0, 0);
    setStartDate(newDate);
    setTransactionCount(null);
  };

  const onForwardClicked = (): void => {
    const newDate = new Date(startDate);
    newDate.setDate(newDate.getDate() + 1);
    newDate.setHours(0, 0, 0, 0);
    setStartDate(newDate);
    setTransactionCount(null);
  };

  const onEmailClicked = (): void => {
    setIsEmailPopopShowing(true);
  };

  const showProductHuntBanner = (): boolean => {
    const currentDate = new Date();
    return currentDate > new Date(2021, 3, 1) && currentDate < new Date(2021, 3, 2);
  };

  return (
    <KibaApp theme={theme}>
      <GlobalsProvider globals={globals}>
        <Helmet>
          <title>{`Token Hunt ${getTitleDateString()}`}</title>
        </Helmet>
        <BackgroundView linearGradient='#200122,#6F0000'>
          <Stack direction={Direction.Vertical} isFullWidth={true} isFullHeight={true} childAlignment={Alignment.Center} contentAlignment={Alignment.Start} isScrollableVertically={true}>
            { showProductHuntBanner() && (
              <Box variant='phBanner'>
                <ContainingView>
                  <Stack directionResponsive={{ base: Direction.Vertical, small: Direction.Horizontal }} contentAlignment={Alignment.Center} childAlignment={Alignment.Center}>
                    <Text>We&apos;re live on Product Hunt 🎉</Text>
                    <Stack direction={Direction.Horizontal} contentAlignment={Alignment.Center} childAlignment={Alignment.Center}>
                      <Text>We&apos;d love your support, please</Text>
                      <Spacing variant={PaddingSize.Narrow} />
                      <Link
                        text=' leave a review here '
                        target='https://www.producthunt.com/posts/nft-of-the-day?utm_source=badge-featured&utm_medium=badge&utm_souce=badge-nft-of-the-day'
                      />
                      <Spacing variant={PaddingSize.Narrow} />
                      <Text>🙌.</Text>
                    </Stack>
                  </Stack>
                </ContainingView>
              </Box>
            )}
            <Spacing variant={PaddingSize.Wide2} />
            <Text variant='header1'>NFT of the day</Text>
            <Spacing variant={PaddingSize.Default} />
            <Stack direction={Direction.Horizontal} childAlignment={Alignment.Center} contentAlignment={Alignment.Start} shouldAddGutters={true}>
              <IconButton icon={<KibaIcon iconId='ion-chevron-back' />} onClicked={onBackClicked} isEnabled={startDate > new Date(2019, 10, 1) } />
              <Text variant='header3'>{getDateString()}</Text>
              <IconButton icon={<KibaIcon iconId='ion-chevron-forward' />} onClicked={onForwardClicked} isEnabled={startDate < defaultDate} />
            </Stack>
            <Spacing variant={PaddingSize.Wide2} />
            { transactionCount !== null ? (
              <Text variant='header3'>{`${numberWithCommas(transactionCount)} transactions in total`}</Text>
            ) : (
              <Text variant='header3'>Loading transactions...</Text>
            )}
            <Spacing variant={PaddingSize.Default} />
            <Stack.Item growthFactor={1} shrinkFactor={1}>
              <Spacing variant={PaddingSize.Wide2} />
            </Stack.Item>
            <ContainingView>
              {error ? (
                <Box isFullWidth={false}>
                  <Text variant='header3'>Sorry, something went wrong. Please Refresh the page</Text>
                </Box>
              ) : (
                <EqualGrid isFullHeight={false} childSizeResponsive={{ base: 12, small: 6, large: 4, extraLarge: 3 }} contentAlignment={Alignment.Center} childAlignment={Alignment.Center} shouldAddGutters={true}>
                  <RandomTokenTransferCard tokenTransfer={randomTokenTransfer} />
                  <HighestPricedTokenTransferCard tokenTransfer={highestPricedTokenTransfer} />
                  <MostTradedTokenTransferCard tokenTransfers={mostTradedTokenTransfers} />
                  <SponsoredTokenCard token={sponsoredToken} />
                </EqualGrid>
              )}
            </ContainingView>
            <Stack.Item growthFactor={1} shrinkFactor={1}>
              <Spacing variant={PaddingSize.Wide2} />
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
              <Stack.Item growthFactor={1} shrinkFactor={1}>
                <Button variant='tertiary' text={'Email'} onClicked={onEmailClicked} iconLeft={<KibaIcon iconId='feather-mail' />} />
              </Stack.Item>
            </Stack>
            <Spacing />
            <Spacing />
            <MarkdownText textVariant='light' source='Data provided by [OpenSea](https://opensea.io/). Made by [Kiba Labs](https://www.kibalabs.com)' />
            <Spacing variant={PaddingSize.Narrow} />
          </Stack>
        </BackgroundView>
        <EmailSubsriptionPopup
          isOpen={isEmailPopupShowing}
          onCloseClicked={() => setIsEmailPopopShowing(false)}
        />
      </GlobalsProvider>
    </KibaApp>
  );
};
