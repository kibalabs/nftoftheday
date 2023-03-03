import React from 'react';

import { LocalStorageClient, Requester } from '@kibalabs/core';
import { IRoute, MockStorage, Router, useInitialization } from '@kibalabs/core-react';
import { EveryviewTracker } from '@kibalabs/everyview-tracker';
import { Alignment, BackgroundView, Box, Direction, IHeadRootProviderProps, KibaApp, Stack } from '@kibalabs/ui-react';
import 'react-toastify/dist/ReactToastify.css';
import { Web3AccountControlProvider } from '@kibalabs/web3-react';
import { ToastContainer } from 'react-toastify';

import { NotdClient } from './client/client';
import { Footer } from './components/Footer';
import { NavBar } from './components/NavBar';
import { GlobalsProvider, IGlobals } from './globalsContext';
import { PageDataProvider } from './PageDataContext';
import { CollectionPage } from './pages/CollectionPage';
import { getCollectionPageData } from './pages/CollectionPage/getCollectionPageData';
import { HomePage } from './pages/HomePage';
import { TokenPage } from './pages/TokenPage';
import { getTokenPageData } from './pages/TokenPage/getTokenPageData';
import { UserPage } from './pages/UserPage';
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
const theme = buildNotdTheme();

export const globals = {
  requester,
  notdClient,
  localStorageClient,
};

export const routes: IRoute<IGlobals>[] = [
  { path: '/', page: HomePage },
  { path: '/collections/:address', page: CollectionPage, getPageData: getCollectionPageData },
  { path: '/collections/:registryAddress/tokens/:tokenId', page: TokenPage, getPageData: getTokenPageData },
  { path: '/accounts/:accountAddress', page: UserPage },
];

interface IAppProps extends IHeadRootProviderProps {
  staticPath?: string;
  pageData?: unknown | undefined | null;
}

export const App = (props: IAppProps): React.ReactElement => {
  useInitialization((): void => {
    tracker.initialize();
    tracker.trackApplicationOpen();
  });

  const onWeb3AccountError = (error: Error): void => {
    console.error(error);
  };

  return (
    <KibaApp theme={theme} isFullPageApp={true} setHead={props.setHead}>
      <PageDataProvider initialData={props.pageData}>
        <GlobalsProvider globals={globals}>
          <Web3AccountControlProvider localStorageClient={localStorageClient} onError={onWeb3AccountError}>
            <BackgroundView linearGradient='#200122,#000000'>
              <Stack direction={Direction.Vertical} isFullHeight={true} isFullWidth={true}>
                <NavBar />
                <Stack.Item growthFactor={1} shrinkFactor={1}>
                  <Stack direction={Direction.Vertical} isFullWidth={true} childAlignment={Alignment.Center} contentAlignment={Alignment.Start} isScrollableVertically={true}>
                    <Box>
                      <Router staticPath={props.staticPath} routes={routes} />
                    </Box>
                    <Footer />
                  </Stack>
                </Stack.Item>
              </Stack>
            </BackgroundView>
          </Web3AccountControlProvider>
          <ToastContainer />
        </GlobalsProvider>
      </PageDataProvider>
      <ToastContainer />
    </KibaApp>
  );
};
