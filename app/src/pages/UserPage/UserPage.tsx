import React from 'react';

import { useStringRouteParam } from '@kibalabs/core-react';
import { Alignment, ContainingView, Direction, EqualGrid, Head, IconButton, Image, KibaIcon, LoadingSpinner, PaddingSize, ResponsiveHidingView, ScreenSize, Stack, StatefulCollapsibleBox, TabBar, Text, TextAlignment } from '@kibalabs/ui-react';

import { CollectionToken, OwnedCollection, TokenTransfer } from '../../client/resources';
import { AccountView } from '../../components/AccountView';
import { TokenCard } from '../../components/TokenCard';
import { TokenSaleRow } from '../../components/TokenSaleRow';
import { useGlobals } from '../../globalsContext';

// const TAB_KEY_OVERVIEW = 'TAB_KEY_OVERVIEW';
const TAB_KEY_OWNED = 'TAB_KEY_OWNED';
const TAB_KEY_TRANSACTIONS = 'TAB_KEY_TRANSACTIONS';

export const UserPage = (): React.ReactElement => {
  const { notdClient } = useGlobals();
  const accountAddress = useStringRouteParam('accountAddress');
  const [ownedCollections, setOwnedCollections] = React.useState<OwnedCollection[] | null | undefined>(undefined);
  const [selectedTabKey, setSelectedTabKey] = React.useState<string>(TAB_KEY_OWNED);
  const [recentTransfers, setRecentTransfers] = React.useState<TokenTransfer[] | null | undefined>(undefined);

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
              {/* <TabBar.Item variant='lined' tabKey={TAB_KEY_OVERVIEW} text='Overview' /> */}
              <TabBar.Item variant='lined' tabKey={TAB_KEY_OWNED} text='Owned Tokens' />
              <TabBar.Item variant='lined' tabKey={TAB_KEY_TRANSACTIONS} text='Activity' />
            </TabBar>
          </ResponsiveHidingView>
          <ResponsiveHidingView hiddenAbove={ScreenSize.Medium}>
            <TabBar contentAlignment={Alignment.Start} isFullWidth={false} onTabKeySelected={onTabKeySelected} selectedTabKey={selectedTabKey}>
              {/* <TabBar.Item variant='lined' tabKey={TAB_KEY_OVERVIEW} text='Overview' /> */}
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
            ) : /* selectedTabKey === TAB_KEY_OVERVIEW */ (
              <Stack direction={Direction.Vertical} childAlignment={Alignment.Center} isScrollableVertically={false} isFullHeight={true} isFullWidth={true} shouldAddGutters={true}>
                <Text>Overview</Text>
                <Stack.Item growthFactor={1} shrinkFactor={1} />
              </Stack>
            )}
          </Stack.Item>
        </Stack>
      </ContainingView>
    </React.Fragment>
  );
};
