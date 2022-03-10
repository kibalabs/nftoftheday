import React from 'react';

import { LocalStorageClient, Requester } from '@kibalabs/core';
import { IRoute, MockStorage, Router, useInitialization } from '@kibalabs/core-react';
import { EveryviewTracker } from '@kibalabs/everyview-tracker';
import { BackgroundView, Direction, KibaApp, Stack } from '@kibalabs/ui-react';
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
  useInitialization((): void => {
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
        <AccountControlProvider>
          <BackgroundView linearGradient='#200122,#6F0000'>
            <Stack direction={Direction.Vertical} isFullHeight={true} isFullWidth={true}>
              {!isProduction() && (
                <NavBar />
              )}
              <Stack.Item growthFactor={1} shrinkFactor={1}>
                <Router routes={routes} />
              </Stack.Item>
            </Stack>
          </BackgroundView>
        </AccountControlProvider>
      </GlobalsProvider>
    </KibaApp>
  );
};
