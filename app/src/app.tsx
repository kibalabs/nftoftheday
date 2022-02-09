import React from 'react';

import { LocalStorageClient, Requester } from '@kibalabs/core';
import { IRoute, MockStorage, Router, useInitialization } from '@kibalabs/core-react';
import { EveryviewTracker } from '@kibalabs/everyview-tracker';
import { BackgroundView, Direction, KibaApp, Stack } from '@kibalabs/ui-react';
import detectEthereumProvider from '@metamask/detect-provider';
import { ethers } from 'ethers';
import { toast } from 'react-toastify';

import 'react-toastify/dist/ReactToastify.css';

import { AccountControlProvider } from './AccountContext';
import { NotdClient } from './client/client';
import { NavBar } from './components/NavBar';
import { isProduction } from './envUtil';
import { GlobalsProvider } from './globalsContext';
import { CollectionPage } from './pages/CollectionPage';
import { HomePage } from './pages/HomePage';
import { TokenPage } from './pages/TokenPage';
import { buildNotdTheme } from './theme';


declare global {
  export interface Window {
    KRT_API_URL?: string;
    KRT_ENV?: string;
  }
}

const requester = new Requester(undefined, undefined, false);
const notdClient = new NotdClient(requester, typeof window !== 'undefined' ? window.KRT_API_URL : undefined);
const localStorageClient = new LocalStorageClient(typeof window !== 'undefined' ? window.localStorage : new MockStorage());
const tracker = new EveryviewTracker('017285d5fef9449783000125f2d5d330');

const globals = {
  requester,
  notdClient,
  localStorageClient,
};

const theme = buildNotdTheme();

export const App = (): React.ReactElement => {
  const [accounts, setAccounts] = React.useState<ethers.Signer[] | undefined | null>(undefined);
  const [accountIds, setAccountIds] = React.useState<string[] | undefined | null>(undefined);
  const [web3, setWeb3] = React.useState<ethers.providers.Web3Provider | null | undefined>(undefined);

  const loadWeb3 = async (): Promise<void> => {
    const provider = await detectEthereumProvider();
    if (!provider) {
      setAccounts(null);
      setAccountIds(null);
      return;
    }
    const web3Connection = new ethers.providers.Web3Provider(provider);
    setWeb3(web3Connection);
  };

  const onAccountsChanged = React.useCallback(async (accountAddresses: string[]): Promise<void> => {
    // NOTE(krishan711): metamask only deals with one account at the moment but returns an array for future compatibility
    const linkedAccounts = accountAddresses.map((accountAddress: string): ethers.Signer => web3.getSigner(accountAddress));
    setAccounts(linkedAccounts);
    Promise.all(linkedAccounts.map((account: ethers.Signer): Promise<string> => account.getAddress())).then((retrievedAccountIds: string[]): void => {
      setAccountIds(retrievedAccountIds);
    });
  }, [web3]);

  const loadAccounts = React.useCallback(async (): Promise<void> => {
    if (!web3) {
      return;
    }
    onAccountsChanged(await web3.provider.request({ method: 'eth_accounts' }));
    web3.provider.on('accountsChanged', onAccountsChanged);
  }, [web3, onAccountsChanged]);

  React.useEffect((): void => {
    loadAccounts();
  }, [loadAccounts]);

  const onLinkAccountsClicked = async (): Promise<void> => {
    if (web3) {
      web3.provider.request({ method: 'eth_requestAccounts', params: [] }).then(async (): Promise<void> => {
        await loadWeb3();
      }).catch((error: unknown): void => {
        if (error.message?.includes('wallet_requestPermissions')) {
          toast.error('You already have a MetaMask request window open, please find it!');
        } else {
          toast.error('Something went wrong connecting to MetaMask. Please try refresh the page / your browser and try again');
        }
      });
    }
  };

  useInitialization((): void => {
    loadWeb3();
    tracker.trackApplicationOpen();
  });

  const routes: IRoute[] = [
    { path: '/', page: HomePage },
    { path: '/collections/:address', page: CollectionPage },
    { path: '/collections/:registryAddress/tokens/:tokenId', page: TokenPage },
  ];

  return (
    <KibaApp theme={theme} isFullPageApp={true}>
      <GlobalsProvider globals={globals}>
        <BackgroundView linearGradient='#200122,#6F0000'>
          <AccountControlProvider accounts={accounts} accountIds={accountIds} onLinkAccountsClicked={onLinkAccountsClicked}>
            <Stack direction={Direction.Vertical} isFullHeight={true} isFullWidth={true}>
              {!isProduction() && (
                <NavBar />
              )}
              <Stack.Item growthFactor={1} shrinkFactor={1}>
                <Router routes={routes} />
              </Stack.Item>
            </Stack>
          </AccountControlProvider>
        </BackgroundView>
      </GlobalsProvider>
    </KibaApp>
  );
};
