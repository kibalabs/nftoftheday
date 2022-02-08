import React from 'react';

import { truncateMiddle } from '@kibalabs/core';
import { Alignment, Box, Button, Direction, Image, Stack, Text } from '@kibalabs/ui-react';
import { ethers } from 'ethers';
import { SiweMessage } from 'siwe';

const domain = window.location.host;
const origin = window.location.origin;
const provider = new ethers.providers.Web3Provider(window.ethereum);
const signer = provider.getSigner();

const createSiweMessage = (address: string, statement: string) => {
  const message = new SiweMessage({
    domain,
    address,
    statement,
    uri: origin,
    version: '1',
    chainId: 1,
  });
  return message.prepareMessage();
};

export const Account = (): React.ReactElement => {
  const [account, setAccount] = React.useState<string | undefined>(undefined);

  const connectWallet = () => {
    provider.send('eth_requestAccounts', [])
      .then(() => signInWithEthereum())
      .catch(() => console.error('user rejected request'));
  };

  const signInWithEthereum = async (): Promise<void> => {
    const address = await signer.getAddress();
    const _ = createSiweMessage(address, 'Connect Wallet.');
    setAccount(await signer.getAddress());
  };

  const onConnectWalletClicked = (): void => {
    connectWallet();
  };
  return (
    <Stack direction={Direction.Horizontal} childAlignment={Alignment.Center} contentAlignment={Alignment.Center} shouldAddGutters={true}>
      {!account ? (
        <Button variant='secondary' text= 'Connect Wallet' onClicked={onConnectWalletClicked} />
      ) : (
        <Stack direction={Direction.Horizontal} childAlignment={Alignment.Center} contentAlignment={Alignment.Center} shouldAddGutters={true}>
          <Box variant='rounded-borderColored' shouldClipContent={true} height='20px' width='20px'>
            <Image source= {`https://web3-images-api.kibalabs.com/v1/accounts/${account}/image`} alternativeText='Avatar' />
          </Box>
          <Text>{truncateMiddle(account, 10)}</Text>
        </Stack>
      )
      }
    </Stack>
  );
};
