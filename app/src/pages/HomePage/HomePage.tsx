import React from 'react';

import { dateToString, isToday, isYesterday, numberWithCommas } from '@kibalabs/core';
import { useDateUrlQueryState } from '@kibalabs/core-react';
import { Alignment, Button, ContainingView, Direction, EqualGrid, Head, IconButton, KibaIcon, LoadingSpinner, PaddingSize, Spacing, Stack, Text } from '@kibalabs/ui-react';

import { SponsoredToken, TokenTransfer, TradedToken } from '../../client/resources';
import { EmailSubsriptionPopup } from '../../components/emailSubcriptionPopup';
import { HighestPricedTokenTransferCard } from '../../components/highestPricedTokenTransferCard';
import { MostTradedTokenTransferCard } from '../../components/mostTradedTokenTransferCard';
import { RandomTokenTransferCard } from '../../components/randomTokenTransferCard';
import { SponsoredTokenCard } from '../../components/sponsoredTokenCard';
import { useGlobals } from '../../globalsContext';

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
  const [highestPricedTokenTransfer, setHighestPricedTokenTransfer] = React.useState<TokenTransfer| null>(null);
  const [mostTradedToken, setMostTradedToken] = React.useState<TradedToken | null>(null);
  const [randomTokenTransfer, setRandomTokenTransfer] = React.useState<TokenTransfer | null>(null);
  const [sponsoredToken, setSponsoredToken] = React.useState<SponsoredToken | null>(null);
  const [transferCount, setTransferCount] = React.useState<number | null>(null);
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
    notdClient.retrieveHighestPriceTransfer(startDate).then((transfer: TokenTransfer): void => {
      setHighestPricedTokenTransfer(transfer);
    }).catch((error: unknown): void => {
      console.error(error);
    });

    notdClient.retrieveMostTradedToken(startDate).then((tradedToken: TradedToken): void => {
      setMostTradedToken(tradedToken);
    }).catch((error: unknown): void => {
      console.error(error);
    });

    notdClient.retrieveRandomTokenTransfer(startDate).then((transfer: TokenTransfer): void => {
      setRandomTokenTransfer(transfer);
    }).catch((error: unknown): void => {
      console.error(error);
    });

    notdClient.retrieveSponsoredTokenTransfer(startDate).then((token: SponsoredToken): void => {
      setSponsoredToken(token);
    }).catch((error: unknown): void => {
      console.error(error);
    });

    notdClient.retrieveTransferCount(startDate).then((count: number): void => {
      setTransferCount(count);
    }).catch((error: unknown): void => {
      console.error(error);
    });
  }, [startDate, notdClient]);

  const onBackClicked = (): void => {
    const newDate = new Date(startDate);
    newDate.setDate(newDate.getDate() - 1);
    newDate.setHours(0, 0, 0, 0);
    setStartDate(newDate);
    setRandomTokenTransfer(null);
    setHighestPricedTokenTransfer(null);
    setMostTradedToken(null);
    setSponsoredToken(null);
    setTransferCount(null);
  };

  const onForwardClicked = (): void => {
    const newDate = new Date(startDate);
    newDate.setDate(newDate.getDate() + 1);
    newDate.setHours(0, 0, 0, 0);
    setStartDate(newDate);
    setRandomTokenTransfer(null);
    setHighestPricedTokenTransfer(null);
    setMostTradedToken(null);
    setSponsoredToken(null);
    setTransferCount(null);
  };

  const onEmailClicked = (): void => {
    setIsEmailPopopShowing(true);
  };

  return (
    <React.Fragment>
      <Head headId='home'>
        <title>{`Token Hunt ${getTitleDateString()}`}</title>
      </Head>
      <Stack direction={Direction.Vertical} isFullWidth={true} isFullHeight={true} childAlignment={Alignment.Center} contentAlignment={Alignment.Start}>
        <Spacing variant={PaddingSize.Wide2} />
        <Text variant='header1'>NFT of the day</Text>
        <Spacing variant={PaddingSize.Default} />
        <Stack direction={Direction.Horizontal} childAlignment={Alignment.Center} contentAlignment={Alignment.Start} shouldAddGutters={true}>
          <IconButton icon={<KibaIcon iconId='ion-chevron-back' />} onClicked={onBackClicked} isEnabled={startDate > new Date(2019, 10, 1) } />
          <Text variant='header3'>{getDateString(startDate)}</Text>
          <IconButton icon={<KibaIcon iconId='ion-chevron-forward' />} onClicked={onForwardClicked} isEnabled={startDate < defaultDate} />
        </Stack>
        <Spacing variant={PaddingSize.Wide2} />
        {!transferCount ? (
          <Text variant='header3'>Loading transfers...</Text>
        ) : (
          <Text variant='header3'>{`${numberWithCommas(transferCount)} transfers`}</Text>
        )}
        <Spacing variant={PaddingSize.Default} />
        <Stack.Item growthFactor={1} shrinkFactor={1}>
          <Spacing variant={PaddingSize.Wide2} />
        </Stack.Item>
        <ContainingView>
          <EqualGrid isFullHeight={false} childSizeResponsive={{ base: 12, small: 6, large: 4, extraLarge: 3 }} contentAlignment={Alignment.Center} childAlignment={Alignment.Center} shouldAddGutters={true}>
            <React.Fragment>
              {randomTokenTransfer ? (
                <RandomTokenTransferCard tokenTransfer={randomTokenTransfer} />
              ) : (
                <LoadingSpinner />
              )}
              {highestPricedTokenTransfer ? (
                <HighestPricedTokenTransferCard tokenTransfer={highestPricedTokenTransfer} />
              ) : (
                <LoadingSpinner />
              )}
              {mostTradedToken ? (
                <MostTradedTokenTransferCard tradedToken={mostTradedToken} />
              ) : (
                <LoadingSpinner />
              )}
              {sponsoredToken ? (
                <SponsoredTokenCard token={sponsoredToken.token} collection={sponsoredToken.collection} latestTransfer={sponsoredToken.latestTransfer} />
              ) : (
                <LoadingSpinner />
              )}
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
      </Stack>
      <EmailSubsriptionPopup
        isOpen={isEmailPopupShowing}
        onCloseClicked={() => setIsEmailPopopShowing(false)}
      />
    </React.Fragment>
  );
};
