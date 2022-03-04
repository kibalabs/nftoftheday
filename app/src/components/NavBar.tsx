import React from 'react';

import { Alignment, Box, Button, Direction, Image, PaddingSize, Spacing, Stack } from '@kibalabs/ui-react';

import { useAccount, useOnLinkAccountsClicked } from '../AccountContext';
import { Account } from './Account';

export const NavBar = (): React.ReactElement => {
  const accountId = useAccount();
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
        <Box variant='unrounded' shouldClipContent={true} height='20px' isFullWidth={false}>
          <Image source='/assets/wordmark.svg' alternativeText='wordmark' fitType='cover' />
        </Box>
        <Stack.Item growthFactor={1} shrinkFactor={1}>
          <Spacing variant={PaddingSize.Wide2} />
        </Stack.Item>
        { !accountId ? (
          <Button variant='secondary' text= 'Connect Wallet' onClicked={onConnectWalletClicked} />
        ) : (
          <Account accountId={accountIdStr} />
        )}
      </Stack>
    </Box>
  );
};
