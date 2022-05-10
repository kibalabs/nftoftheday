import React from 'react';

import { Alignment, Box, Button, Direction, Image, LinkBase, PaddingSize, Spacing, Stack } from '@kibalabs/ui-react';

import { useAccount, useOnLinkAccountsClicked } from '../AccountContext';
import { Account } from './Account';

export const NavBar = (): React.ReactElement => {
  const account = useAccount();
  const onLinkAccountsClicked = useOnLinkAccountsClicked();

  const onConnectWalletClicked = async (): Promise<void> => {
    await onLinkAccountsClicked();
  };

  return (
    <Box height='64px' isFullWidth={true}>
      <Stack direction={Direction.Horizontal} isFullWidth={true} isFullHeight={true} childAlignment={Alignment.Center} contentAlignment={Alignment.Center} shouldAddGutters={true} padding={PaddingSize.Wide1}>
        <Box shouldClipContent={true} width='40px' height='40px'>
          <Image source='/assets/icon.png' alternativeText='logo' fitType='cover' />
        </Box>
        <LinkBase target='/'>
          <Box variant='unrounded' shouldClipContent={true} height='20px' isFullWidth={false}>
            <Image source='/assets/wordmark.svg' alternativeText='wordmark' fitType='cover' />
          </Box>
        </LinkBase>
        <Stack.Item growthFactor={1} shrinkFactor={1}>
          <Spacing variant={PaddingSize.Wide2} />
        </Stack.Item>
        { !account ? (
          <Button variant='secondary' text= 'Connect Wallet' onClicked={onConnectWalletClicked} />
        ) : (
          <Account accountId={account.address} />
        )}
      </Stack>
    </Box>
  );
};
