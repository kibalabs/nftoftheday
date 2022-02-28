import React from 'react';

import { dateToString, isToday, isYesterday, numberWithCommas } from '@kibalabs/core';
import { useDateUrlQueryState } from '@kibalabs/core-react';
import { Alignment, Box, Button, ContainingView, Direction, EqualGrid, Head, IconButton, KibaIcon, LoadingSpinner, MarkdownText, PaddingSize, Spacing, Stack, Text } from '@kibalabs/ui-react';

import { HighestPriceTransfer, MostTradedTokenTransfer, Token, TokenTransfer, UiData } from '../../client/resources';
import { EmailSubsriptionPopup } from '../../components/emailSubcriptionPopup';
import { HighestPricedTokenTransferCard } from '../../components/highestPricedTokenTransferCard';
import { MostTradedTokenTransferCard } from '../../components/mostTradedTokenTransferCard';
import { RandomTokenTransferCard } from '../../components/randomTokenTransferCard';
import { SponsoredTokenCard } from '../../components/sponsoredTokenCard';
import { useGlobals } from '../../globalsContext';
import '../../fonts.css';

const defaultDate = new Date();
defaultDate.setHours(0, 0, 0, 0);

const getDateString = (startDate: Date): string => {
  if (startDate !== null) {
    if (isToday(startDate)) {
      return 'Today';
    }
    if (isYesterday(startDate)) {
      return 'Yesterday';
    }
    return dateToString(startDate, 'dd MMMM yyyy');
  }
  return '';
};

export const HomePage = (): React.ReactElement => {
  const { notdClient } = useGlobals();
  const [isEmailPopupShowing, setIsEmailPopopShowing] = React.useState(false);
  // const [uiData, setUiData] = React.useState<UiData | null>(null);
  const [highestPricedTokenTransfer, setHighestPricedTokenTransfer] = React.useState<TokenTransfer| undefined | null>(undefined);
  const [mostTradedTokenTransfer, setMostTradedTokenTransfer] = React.useState<TokenTransfer[] | undefined | null>(undefined);
  const [randomTokenTransfer, setRandomTokenTransfer] = React.useState<TokenTransfer | undefined | null>(undefined);
  const [sponsoredToken, setSponsoredToken] = React.useState<Token | undefined | null>(undefined);

  const [error, setError] = React.useState<boolean>(false);
  const [startDate_, setStartDate] = useDateUrlQueryState('date', undefined, 'yyyy-MM-dd', defaultDate);
  const startDate = startDate_ as Date;

  const getTitleDateString = (): string => {
    if (startDate !== null) {
      if (isToday(startDate)) {
        return '';
      }
      return `| ${dateToString(startDate, 'dd MMMM yyyy')}`;
    }
    return '';
  };

  React.useEffect((): void => {
    // setUiData(null);
    // notdClient.retrieveUiData(startDate).then((retrievedUiData: UiData): void => {
    //   setUiData(retrievedUiData);
    // }).catch(() => {
    //   setError(true);
    // });
    notdClient.retrieveHighestPriceTransfer(startDate).then((transfers: TokenTransfer): void => {
      setHighestPricedTokenTransfer(transfers);
    }).catch((error: unknown): void => {
      console.error(error);
      setError(true);
      setHighestPricedTokenTransfer(null);
    });
    notdClient.retrieveMostTradedTokenTransfer(startDate).then((tradedToken: TokenTransfer[]): void => {
      setMostTradedTokenTransfer(tradedToken);
    }).catch((error: unknown): void => {
      console.error(error);
      setError(true);
      setMostTradedTokenTransfer(null);
    });
    notdClient.retrieveRandomTokenTransfer(startDate).then((tokenTransfers: TokenTransfer): void => {
      setRandomTokenTransfer(tokenTransfers);
    }).catch((error: unknown): void => {
      console.error(error);
      setError(true);
      setRandomTokenTransfer(null);
    });
    notdClient.retrieveSponsoredTokenTransfer(startDate).then((token: Token): void => {
      setSponsoredToken(token);
    }).catch((error: unknown): void => {
      console.error(error);
      setError(true);
      setSponsoredToken(null);
    });
  }, [startDate, notdClient]);

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

  const onEmailClicked = (): void => {
    setIsEmailPopopShowing(true);
  };

  return (
    <React.Fragment>
      <Head headId='home'>
        <title>{`Token Hunt ${getTitleDateString()}`}</title>
      </Head>
      <Stack direction={Direction.Vertical} isFullWidth={true} isFullHeight={true} childAlignment={Alignment.Center} contentAlignment={Alignment.Start} isScrollableVertically={true}>
        <Spacing variant={PaddingSize.Wide2} />
        <Text variant='header1'>NFT of the day</Text>
        <Spacing variant={PaddingSize.Default} />
        <Stack direction={Direction.Horizontal} childAlignment={Alignment.Center} contentAlignment={Alignment.Start} shouldAddGutters={true}>
          <IconButton icon={<KibaIcon iconId='ion-chevron-back' />} onClicked={onBackClicked} isEnabled={startDate > new Date(2019, 10, 1) } />
          <Text variant='header3'>{getDateString(startDate)}</Text>
          <IconButton icon={<KibaIcon iconId='ion-chevron-forward' />} onClicked={onForwardClicked} isEnabled={startDate < defaultDate} />
        </Stack>
        <Spacing variant={PaddingSize.Wide2} />
        {/* { uiData !== null ? (
          <Text variant='header3'>{`${numberWithCommas(uiData.transactionCount)} transfers`}</Text>
        ) : (
          <Text variant='header3'>Loading transactions...</Text>
        )} */}
        <Spacing variant={PaddingSize.Default} />
        <Stack.Item growthFactor={1} shrinkFactor={1}>
          <Spacing variant={PaddingSize.Wide2} />
        </Stack.Item>
        <ContainingView>
     
            {/* <Box isFullWidth={false}>
              <Text variant='header3'>Sorry, something went wrong. Please Refresh the page</Text>
            </Box>
            <LoadingSpinner variant='light' /> */}
            <EqualGrid isFullHeight={false} childSizeResponsive={{ base: 12, small: 6, large: 4, extraLarge: 3 }} contentAlignment={Alignment.Center} childAlignment={Alignment.Center} shouldAddGutters={true}>
              <React.Fragment>
                <RandomTokenTransferCard tokenTransfer={randomTokenTransfer} />
                <HighestPricedTokenTransferCard tokenTransfer={highestPricedTokenTransfer} />
                <MostTradedTokenTransferCard tokenTransfers={mostTradedTokenTransfer} />
                <SponsoredTokenCard token={sponsoredToken} />
              </React.Fragment>
            </EqualGrid>
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
        <MarkdownText textVariant='light' source='Made by [Kiba Labs](https://www.kibalabs.com)' />
        <Spacing variant={PaddingSize.Narrow} />
      </Stack>
      <EmailSubsriptionPopup
        isOpen={isEmailPopupShowing}
        onCloseClicked={() => setIsEmailPopopShowing(false)}
      />
    </React.Fragment>
  );
};
