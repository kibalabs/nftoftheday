import React from 'react';

import { IMultiAnyChildProps } from '@kibalabs/core-react';
import { ethers } from 'ethers';

type AccountsControl = {
  accounts: ethers.Signer[] | undefined | null;
  accountIds: string[] | undefined | null;
  accountId: string | undefined | null;

  onLinkAccountsClicked: () => void;
}

export const AccountsContext = React.createContext<AccountsControl | undefined | null>(undefined);

interface IAccountControlProviderProps extends IMultiAnyChildProps {
  accounts: ethers.Signer[] | null;
  accountIds: string[] | null;
  accountId: string | undefined | null;
  onLinkAccountsClicked: () => void;
}

export const AccountControlProvider = (props: IAccountControlProviderProps): React.ReactElement => (
  <AccountsContext.Provider value={{ accounts: props.accounts, accountIds: props.accountIds, accountId: props.accountId, onLinkAccountsClicked: props.onLinkAccountsClicked }}>
    {props.children}
  </AccountsContext.Provider>
);

export const useAccounts = (): ethers.Signer[] | undefined | null => {
  const accountsControl = React.useContext(AccountsContext);
  if (!accountsControl) {
    throw Error('accountsControl has not been initialized correctly.');
  }
  return accountsControl.accounts;
};

export const useAccountIds = (): string[] | undefined | null => {
  const accountsControl = React.useContext(AccountsContext);
  if (!accountsControl) {
    throw Error('accountsControl has not been initialized correctly.');
  }
  return accountsControl.accountIds;
};
export const useAccountId = (): string | undefined | null => {
  const accountsControl = React.useContext(AccountsContext);
  if (!accountsControl) {
    throw Error('accountsControl has not been initialized correctly.');
  }
  return accountsControl?.accountIds?.length ? accountsControl.accountIds[0] : null;
};

export const useOnLinkAccountsClicked = (): (() => void) => {
  const accountsControl = React.useContext(AccountsContext);
  if (!accountsControl) {
    throw Error('accountsControl has not been initialized correctly.');
  }
  return accountsControl.onLinkAccountsClicked;
};
