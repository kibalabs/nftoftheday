import React from 'react';

import { Alignment, Box, Direction, IconButton, KibaIcon, PaddingSize, ResponsiveHidingView, ScreenSize, Spacing, Stack, Text, TextAlignment } from '@kibalabs/ui-react';

import { TokenTransfer } from '../client/resources';
import { Account } from './Account';

export interface ITokenSaleRowProps {
  tokenTransfer: TokenTransfer;
}

export const TokenSaleRow = (props: ITokenSaleRowProps): React.ReactElement => {
  const timeSince = (date: Date): string => {
    const seconds = Math.floor((new Date().valueOf() - date.valueOf()) / 1000);

    let interval = seconds / 31536000;

    if (interval > 1) {
      return `${Math.floor(interval)} year(s)`;
    }
    interval = seconds / 2592000;
    if (interval > 1) {
      return `${Math.floor(interval)} month(s)`;
    }
    interval = seconds / 86400;
    if (interval > 1) {
      return `${Math.floor(interval)} day(s)`;
    }
    interval = seconds / 3600;
    if (interval > 1) {
      return `${Math.floor(interval)} hour(s)`;
    }
    interval = seconds / 60;
    if (interval > 1) {
      return `${Math.floor(interval)} minute(s)`;
    }
    return `${Math.floor(seconds)} second(s)`;
  };

  return (
    <Stack direction={Direction.Vertical} shouldWrapItems={true} isFullWidth={true} childAlignment={Alignment.Center} contentAlignment={Alignment.Center}>
      <ResponsiveHidingView hiddenBelow={ScreenSize.Medium}>
        <Stack direction={Direction.Horizontal} isFullWidth={true} isFullHeight={true}childAlignment={Alignment.Center} contentAlignment={Alignment.Center}>
          <Box variant='tokenSaleRow'>
            <Stack direction={Direction.Horizontal} shouldWrapItems={true} isFullWidth={true} childAlignment={Alignment.Center} contentAlignment={Alignment.Center}>
              <Stack.Item baseSize='12rem' alignment={Alignment.Center}>
                <Account accountId={props.tokenTransfer?.fromAddress} />
              </Stack.Item>
              <Stack.Item baseSize='6rem' alignment={Alignment.Center}>
                <KibaIcon iconId='ion-arrow-forward' />
              </Stack.Item>
              <Stack.Item baseSize='12rem' alignment={Alignment.Center}>
                <Account accountId={props.tokenTransfer?.toAddress} />
              </Stack.Item>
              <Stack.Item baseSize='12rem' alignment={Alignment.Center}>
                <Spacing variant={PaddingSize.Wide2} />
              </Stack.Item>
              <Stack.Item baseSize='12rem' alignment={Alignment.Center}>
                <Text alignment={TextAlignment.Center}>
                  { `Ξ${props.tokenTransfer.value / 1000000000000000000.0}`}
                </Text>
              </Stack.Item>
              <Stack.Item baseSize='12rem' alignment={Alignment.Center}>
                <Text alignment={TextAlignment.Center}>
                  {`${timeSince(props.tokenTransfer.blockDate)} ago`}
                </Text>
              </Stack.Item>
              <Stack.Item baseSize='12rem' alignment={Alignment.Center}>
                <IconButton icon={<KibaIcon iconId='ion-open-outline' />} target={`https://etherscan.io/tx/${props.tokenTransfer.transactionHash}`} />
              </Stack.Item>
            </Stack>
          </Box>
        </Stack>
      </ResponsiveHidingView>
      <ResponsiveHidingView hiddenAbove={ScreenSize.Medium}>
        <Stack direction={Direction.Vertical}isFullWidth={true} isFullHeight={true} childAlignment={Alignment.Center} contentAlignment={Alignment.Center} paddingLeft={PaddingSize.Wide} paddingRight={PaddingSize.Wide}>
          <Box variant='tokenSaleRow' isFullWidth={true}>
            <Stack direction={Direction.Horizontal} childAlignment={Alignment.Center} contentAlignment={Alignment.Center} padding={PaddingSize.Narrow}>
              <Stack.Item alignment={Alignment.Center}>
                <Text alignment={TextAlignment.Right}>
                  { `Ξ${props.tokenTransfer.value / 1000000000000000000.0}`}
                </Text>
              </Stack.Item>
              <Spacing variant={PaddingSize.Wide2} />
              <Stack.Item alignment={Alignment.Center}>
                <Text alignment={TextAlignment.Left}>
                  {`${timeSince(props.tokenTransfer.blockDate)} ago`}
                </Text>
              </Stack.Item>
              <Stack.Item alignment={Alignment.Center}>
                <IconButton icon={<KibaIcon iconId='ion-open-outline' />} target={`https://etherscan.io/tx/${props.tokenTransfer.transactionHash}`} />
              </Stack.Item>
            </Stack>
          </Box>
          <Box variant='tokenSaleRow'>
            <Stack direction={Direction.Horizontal} childAlignment={Alignment.Center} contentAlignment={Alignment.Center}>
              <Stack.Item baseSize='5rem' alignment={Alignment.Center}>
                <Account accountId={props.tokenTransfer?.fromAddress} />
              </Stack.Item>
              <Stack.Item baseSize='3rem' alignment={Alignment.Center}>
                <KibaIcon iconId='ion-arrow-forward' />
              </Stack.Item>
              <Stack.Item baseSize='5rem' alignment={Alignment.Center}>
                <Account accountId={props.tokenTransfer?.toAddress} />
              </Stack.Item>
            </Stack>
          </Box>
        </Stack>
      </ResponsiveHidingView>
    </Stack>
  );
};
