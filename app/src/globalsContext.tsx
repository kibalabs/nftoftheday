import React from 'react';

import { LocalStorageClient, Requester } from '@kibalabs/core';
import { IMultiAnyChildProps } from '@kibalabs/core-react';

import { NotdClient } from './client/client';

export interface IGlobals {
  requester: Requester;
  notdClient: NotdClient;
  localStorageClient: LocalStorageClient;
}

export const GlobalsContext = React.createContext<IGlobals | null>(null);

interface IGlobalsProviderProps extends IMultiAnyChildProps {
  globals: IGlobals;
}

export const GlobalsProvider = (props: IGlobalsProviderProps): React.ReactElement => (
  <GlobalsContext.Provider value={props.globals}>
    {props.children}
  </GlobalsContext.Provider>
);

export const useGlobals = (): IGlobals => {
  const globals = React.useContext(GlobalsContext);
  if (!globals) {
    throw new Error('Cannot use useGlobals since globals has not ben provided above in the hierarchy');
  }
  return globals;
};
