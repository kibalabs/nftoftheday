import React from 'react';

import { LocalStorageClient, Requester } from '@kibalabs/core';
import { IRoute, MockStorage, Router, useInitialization } from '@kibalabs/core-react';
import { EveryviewTracker } from '@kibalabs/everyview-tracker';
import { KibaApp } from '@kibalabs/ui-react';

import { NotdClient } from './client/client';
import { GlobalsProvider } from './globalsContext';
import { HomePage } from './pages/HomePage';
import { buildNotdTheme } from './theme';


declare global {
  export interface Window {
    KRT_API_URL?: string;
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
  ];

  return (
    <KibaApp theme={theme} isFullPageApp={true}>
      <GlobalsProvider globals={globals}>
        <Router routes={routes} />
      </GlobalsProvider>
    </KibaApp>
  );
};
