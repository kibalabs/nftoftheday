import React from 'react';

import { Alignment, Box, Button, Direction, Image, LinkBase, Stack, Text } from '@kibalabs/ui-react';

import { useOnLinkAccountsClicked } from '../accountContext';

export interface AccountViewProps {
  accountIds: string[] | null;
}
export const Account = (props: AccountViewProps): React.ReactElement => {
  const onLinkAccountsClicked = useOnLinkAccountsClicked();

  const onConnectWalletClicked = async (): Promise<void> => {
    if (!props.accountIds) {
      window.open('https://metamask.io');
    } else if (props.accountIds.length === 0) {
      await onLinkAccountsClicked();
    }
  };
  return (
    <Stack direction={Direction.Horizontal} childAlignment={Alignment.Center} contentAlignment={Alignment.Center} shouldAddGutters={true}>
      { !props.accountIds ? (
        <LinkBase onClicked={onConnectWalletClicked}>
          <Text variant='bold'>Install metamask to get started</Text>
        </LinkBase>
      ) : props.accountIds.length === 0 ? (
        <Button variant='secondary' text= 'Connect Wallet' onClicked={onConnectWalletClicked} />
      ) : (
        <Stack direction={Direction.Horizontal} childAlignment={Alignment.Center} contentAlignment={Alignment.Center} shouldAddGutters={true}>
          <Box variant='rounded-borderColored' shouldClipContent={true} height='20px' width='20px'>
            <Image source={`https://web3-images-api.kibalabs.com/v1/accounts/${props.accountIds}/image`} alternativeText='Avatar' />
          </Box>
          <Text>{props.accountIds}</Text>
        </Stack>
      )}
    </Stack>
  );
};
