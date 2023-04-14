import React from 'react';

import { addDays, dateToString, startOfDay } from '@kibalabs/core';
import { useStringRouteParam } from '@kibalabs/core-react';
import { Alignment, Box, ContainingView, Direction, EqualGrid, Head, IconButton, Image, KibaIcon, LoadingSpinner, PaddingSize, ResponsiveHidingView, ScreenSize, Spacing, Stack, StatefulCollapsibleBox, TabBar, Text, TextAlignment, useColors } from '@kibalabs/ui-react';
import ActivityCalendar, { BlockElement, Activity as CalendarActivity, Level as CalendarActivityLevel } from 'react-activity-calendar';
import { Tooltip as ReactTooltip } from 'react-tooltip';

import { CollectionToken, OwnedCollection, TokenTransfer, TradingHistory } from '../../client/resources';
import { AccountView } from '../../components/AccountView';
import { TokenCard } from '../../components/TokenCard';
import { TokenSaleRow } from '../../components/TokenSaleRow';
import { useGlobals } from '../../globalsContext';

const TAB_KEY_OVERVIEW = 'TAB_KEY_OVERVIEW';
const TAB_KEY_OWNED = 'TAB_KEY_OWNED';
const TAB_KEY_TRANSACTIONS = 'TAB_KEY_TRANSACTIONS';

export const UserPage = (): React.ReactElement => {
  const colors = useColors();
  const { notdClient } = useGlobals();
  const accountAddress = useStringRouteParam('accountAddress');
  const [blueChipOwnedCollections, setBlueChipOwnedCollections] = React.useState<OwnedCollection[] | null | undefined>(undefined);
  const [ownedCollections, setOwnedCollections] = React.useState<OwnedCollection[] | null | undefined>(undefined);
  const [selectedTabKey, setSelectedTabKey] = React.useState<string>(TAB_KEY_OVERVIEW);
  const [tradingCalendarActivity, setTradingCalendarActivity] = React.useState<CalendarActivity[] | undefined | null>(undefined);
  const [recentTransfers, setRecentTransfers] = React.useState<TokenTransfer[] | null | undefined>(undefined);

  const updateTradingCalendarActivity = React.useCallback(async (shouldClear = false): Promise<void> => {
    if (shouldClear) {
      setTradingCalendarActivity(undefined);
    }
    if (!accountAddress) {
      setTradingCalendarActivity(undefined);
      return;
    }
    notdClient.listUserTradingHistories(accountAddress).then((tradingHistories: TradingHistory[]): void => {
      const allValues: Record<string, TradingHistory> = tradingHistories.reduce((accumulator: Record<string, TradingHistory>, current: TradingHistory): Record<string, TradingHistory> => {
        accumulator[dateToString(current.date, 'yyyy-MM-dd')] = current;
        return accumulator;
      }, {});
      let currentDay = addDays(startOfDay(new Date()), -365);
      const newTradingCalendarActivities: CalendarActivity[] = [];
      while (currentDay < new Date()) {
        const currentDayString = dateToString(currentDay, 'yyyy-MM-dd');
        const currentDayHistory = allValues[currentDayString];
        const value = currentDayHistory ? Number(currentDayHistory.buyCount + currentDayHistory.mintCount + currentDayHistory.sellCount + currentDayHistory.transferCount) : 0;
        newTradingCalendarActivities.push({
          date: currentDayString,
          count: value,
          level: Math.max(0, Math.min(value, 4)) as CalendarActivityLevel,
        });
        currentDay = addDays(currentDay, 1);
      }
      setTradingCalendarActivity(newTradingCalendarActivities);
    }).catch((error: unknown): void => {
      console.error(error);
      setTradingCalendarActivity(null);
    });
  }, [notdClient, accountAddress]);

  React.useEffect((): void => {
    updateTradingCalendarActivity();
  }, [updateTradingCalendarActivity]);

  const updateOwnedBlueChipTokens = React.useCallback(async (shouldClear = false): Promise<void> => {
    if (shouldClear) {
      setBlueChipOwnedCollections(undefined);
    }
    if (!accountAddress) {
      setBlueChipOwnedCollections(undefined);
      return;
    }
    notdClient.listUserBlueChipOwnedCollections(accountAddress).then((retrievedOwnedCollections: OwnedCollection[]): void => {
      setBlueChipOwnedCollections(retrievedOwnedCollections);
    }).catch((error: unknown): void => {
      console.error(error);
      setBlueChipOwnedCollections(null);
    });
  }, [notdClient, accountAddress]);

  React.useEffect((): void => {
    updateOwnedBlueChipTokens();
  }, [updateOwnedBlueChipTokens]);

  const updateOwnedCollections = React.useCallback(async (shouldClear = false): Promise<void> => {
    if (shouldClear) {
      setOwnedCollections(undefined);
    }
    if (!accountAddress) {
      setOwnedCollections(undefined);
      return;
    }
    notdClient.listUserOwnedCollections(accountAddress).then((retrievedOwnedCollections: OwnedCollection[]): void => {
      setOwnedCollections(retrievedOwnedCollections);
    }).catch((error: unknown): void => {
      console.error(error);
      setOwnedCollections(null);
    });
  }, [notdClient, accountAddress]);

  React.useEffect((): void => {
    updateOwnedCollections();
  }, [updateOwnedCollections]);

  const updateTransfers = React.useCallback(async (shouldClear = false): Promise<void> => {
    if (shouldClear) {
      setRecentTransfers(undefined);
    }
    if (!accountAddress) {
      setRecentTransfers(undefined);
      return;
    }
    notdClient.listUserRecentTransfers(accountAddress, 1000, 0).then((retrievedRecentTransfers: TokenTransfer[]): void => {
      setRecentTransfers(retrievedRecentTransfers);
    }).catch((error: unknown): void => {
      console.error(error);
      setRecentTransfers(null);
    });
  }, [notdClient, accountAddress]);

  React.useEffect((): void => {
    updateTransfers();
  }, [updateTransfers]);

  const onTabKeySelected = (newSelectedTabKey: string): void => {
    setSelectedTabKey(newSelectedTabKey);
  };

  return (
    <React.Fragment>
      <Head>
        <title>{`${accountAddress} | Token Hunt`}</title>
      </Head>
      <ContainingView>
        <Stack direction={Direction.Vertical} isFullHeight={false} isFullWidth={true} childAlignment={Alignment.Center} contentAlignment={Alignment.Center} shouldAddGutters={true} paddingHorizontal={PaddingSize.Wide} paddingVertical={PaddingSize.Default}>
          <Stack direction={Direction.Horizontal} shouldAddGutters={true} childAlignment={Alignment.Center}>
            <AccountView
              address={accountAddress}
              textVariant='header2'
              imageSize='2em'
              shouldUseYourAccount={true}
            />
            <IconButton icon={<KibaIcon iconId='ion-open-outline' />} target={`https://etherscan.io/address/${accountAddress}`} />
          </Stack>
          <ResponsiveHidingView hiddenBelow={ScreenSize.Medium}>
            <TabBar contentAlignment={Alignment.Start} isFullWidth={false} onTabKeySelected={onTabKeySelected} selectedTabKey={selectedTabKey}>
              <TabBar.Item variant='lined' tabKey={TAB_KEY_OVERVIEW} text='Overview' />
              <TabBar.Item variant='lined' tabKey={TAB_KEY_OWNED} text='Owned Tokens' />
              <TabBar.Item variant='lined' tabKey={TAB_KEY_TRANSACTIONS} text='Activity' />
            </TabBar>
          </ResponsiveHidingView>
          <ResponsiveHidingView hiddenAbove={ScreenSize.Medium}>
            <TabBar contentAlignment={Alignment.Start} isFullWidth={false} onTabKeySelected={onTabKeySelected} selectedTabKey={selectedTabKey}>
              <TabBar.Item variant='lined' tabKey={TAB_KEY_OVERVIEW} text='Overview' />
              <TabBar.Item variant='lined' tabKey={TAB_KEY_OWNED} text='Owned Tokens' />
              <TabBar.Item variant='lined' tabKey={TAB_KEY_TRANSACTIONS} text='Activity' />
            </TabBar>
          </ResponsiveHidingView>
          <Stack.Item growthFactor={1} shrinkFactor={1}>
            {selectedTabKey === TAB_KEY_OWNED ? (
              <Stack direction={Direction.Vertical} childAlignment={Alignment.Center} isScrollableVertically={false} isFullHeight={true} isFullWidth={true} shouldAddGutters={true}>
                { ownedCollections === undefined ? (
                  <LoadingSpinner />
                ) : ownedCollections === null ? (
                  <Text variant='error' alignment={TextAlignment.Center}>Failed to load other projects</Text>
                ) : ownedCollections.length === 0 ? (
                  <Text alignment={TextAlignment.Center}>No other projects</Text>
                ) : (
                  <React.Fragment>
                    {ownedCollections.map((ownedCollection: OwnedCollection): React.ReactElement => (
                      <StatefulCollapsibleBox
                        key={ownedCollection.collection.address}
                        isCollapsedInitially={true}
                        headerView={(
                          <Stack direction={Direction.Horizontal} shouldAddGutters={true}>
                            <Image source={ownedCollection.collection.imageUrl || ''} height='1.5em' width='1.5em' alternativeText='' />
                            <Text>{ownedCollection.collection.name}</Text>
                            <Text variant='bold'>{`x${ownedCollection.tokens.length}`}</Text>
                          </Stack>
                        )}
                        shouldSkipRenderingWhenCollapsed={true}
                      >
                        <EqualGrid childSizeResponsive={{ base: 6, medium: 4, large: 3, extraLarge: 2 }} contentAlignment={Alignment.Start} childAlignment={Alignment.Start} shouldAddGutters={true}>
                          {ownedCollection.tokens.map((token: CollectionToken): React.ReactElement => (
                            <TokenCard
                              key={`${token.registryAddress}-${token.tokenId}`}
                              collectionToken={token}
                              target={`/collections/${token.registryAddress}/tokens/${token.tokenId}`}
                            />
                          ))}
                        </EqualGrid>
                      </StatefulCollapsibleBox>
                    ))}
                  </React.Fragment>
                )}
              </Stack>
            ) : selectedTabKey === TAB_KEY_TRANSACTIONS ? (
              <Stack direction={Direction.Vertical} childAlignment={Alignment.Center} isScrollableVertically={false} isFullHeight={true} isFullWidth={true} shouldAddGutters={true}>
                { recentTransfers === undefined ? (
                  <LoadingSpinner />
                ) : recentTransfers === null ? (
                  <Text variant='error' alignment={TextAlignment.Center}>Failed to load activity</Text>
                ) : recentTransfers.length === 0 ? (
                  <Text alignment={TextAlignment.Center}>No activity</Text>
                ) : (
                  <React.Fragment>
                    {recentTransfers.map((tokenTransfer: TokenTransfer, index: number): React.ReactElement => (
                      <TokenSaleRow key={index} tokenTransfer={tokenTransfer} showToken={true} />
                    ))}
                  </React.Fragment>
                )}
              </Stack>
            ) : selectedTabKey === TAB_KEY_OVERVIEW ? (
              <Stack direction={Direction.Vertical} childAlignment={Alignment.Center} isScrollableVertically={false} isFullHeight={true} isFullWidth={true} shouldAddGutters={true}>
                <Stack.Item gutterAfter={PaddingSize.Narrow}>
                  <Text variant='header3'>Activity Map</Text>
                </Stack.Item>
                { tradingCalendarActivity === undefined ? (
                  <LoadingSpinner />
                ) : tradingCalendarActivity === null ? (
                  <Text variant='error' alignment={TextAlignment.Center}>Failed to load activity</Text>
                ) : tradingCalendarActivity.length === 0 ? (
                  <Text alignment={TextAlignment.Center}>No activity</Text>
                ) : (
                  <ActivityCalendar
                    data={tradingCalendarActivity}
                    weekStart={1}
                    hideColorLegend={true}
                    hideTotalCount={true}
                    theme={{
                      light: [colors.brandPrimaryClear95, colors.brandPrimaryClear75, colors.brandPrimaryClear50, colors.brandPrimaryClear25, colors.brandPrimary],
                      dark: [colors.brandPrimaryClear95, colors.brandPrimaryClear75, colors.brandPrimaryClear50, colors.brandPrimaryClear25, colors.brandPrimary],
                    }}
                    renderBlock={(block :BlockElement, activity: CalendarActivity) => React.cloneElement(block, {
                      'data-tooltip-id': 'react-tooltip',
                      'data-tooltip-html': `${activity.count} activities on ${activity.date}`,
                    })
                    }
                  />
                )}
                <Spacing variant={PaddingSize.Wide} />
                <Stack.Item gutterAfter={PaddingSize.Narrow}>
                  <Text variant='header3'>Blue Chip Holdings</Text>
                </Stack.Item>
                { blueChipOwnedCollections === undefined ? (
                  <LoadingSpinner />
                ) : blueChipOwnedCollections === null ? (
                  <Text variant='error' alignment={TextAlignment.Center}>Failed to load activity</Text>
                ) : blueChipOwnedCollections.length === 0 ? (
                  <Text alignment={TextAlignment.Center}>No activity</Text>
                ) : (
                  <EqualGrid childSizeResponsive={{ base: 12, small: 6, medium: 4, large: 3 }} shouldAddGutters={true}>
                    {blueChipOwnedCollections.map((ownedCollection: OwnedCollection): React.ReactElement => (
                      <Box key={ownedCollection.collection.address} variant='card' isFullHeight={true} isFullWidth={true}>
                        <Stack direction={Direction.Vertical} shouldAddGutters={true}>
                          <Stack direction={Direction.Horizontal} shouldAddGutters={true}>
                            <Image height='3em' width='3em' source={ownedCollection.collection.imageUrl || '/favicon.png'} alternativeText='' />
                            <Stack.Item growthFactor={1} shrinkFactor={1}>
                              <Stack direction={Direction.Vertical} shouldAddGutters={false} contentAlignment={Alignment.Start} childAlignment={Alignment.Start}>
                                <Text variant='bold'>{ownedCollection.collection.name}</Text>
                                <Text>{`x${ownedCollection.tokens.length}`}</Text>
                              </Stack>
                            </Stack.Item>
                          </Stack>
                          <Stack direction={Direction.Horizontal} shouldAddGutters={true} contentAlignment={Alignment.Start} isFullWidth={true}>
                            {ownedCollection.tokens.slice(0, 10).map((token: CollectionToken): React.ReactElement => (
                              <Image key={token.tokenId} source={token.imageUrl || '/favicon.png'} width='1em' height='1em' alternativeText='' />
                            ))}
                          </Stack>
                        </Stack>
                      </Box>
                    ))}
                  </EqualGrid>
                )}
                <Stack.Item growthFactor={1} shrinkFactor={1} />
              </Stack>
            ) : (
              null
            )}
          </Stack.Item>
        </Stack>
      </ContainingView>
      <ReactTooltip id='react-tooltip' />
    </React.Fragment>
  );
};
