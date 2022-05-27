import React from 'react';

import { Alignment, Box, Direction, IconButton, KibaIcon, PaddingSize, ResponsiveHidingView, ScreenSize, Spacing, Stack, Text, TextAlignment } from '@kibalabs/ui-react';

import { shortFormatEther } from '../chainUtil';
import { TokenTransfer } from '../client/resources';
import { Account } from './Account';

export interface ITokenSaleRowProps {
  tokenTransfer: TokenTransfer;
}

export const TokenSaleRow = (props: ITokenSaleRowProps): React.ReactElement => {
  const formatDate = (date: Date): string => {
    const seconds = Math.floor((new Date().valueOf() - date.valueOf()) / 1000);
    let intervalType: string;

    let interval = Math.floor(seconds / 31536000);
    if (interval >= 1) {
      intervalType = 'year';
    } else {
      interval = Math.floor(seconds / 2592000);
      if (interval >= 1) {
        intervalType = 'month';
      } else {
        interval = Math.floor(seconds / 86400);
        if (interval >= 1) {
          intervalType = 'day';
        } else {
          interval = Math.floor(seconds / 3600);
          if (interval >= 1) {
            intervalType = 'hour';
          } else {
            interval = Math.floor(seconds / 60);
            if (interval >= 1) {
              intervalType = 'minute';
            } else {
              interval = seconds;
              intervalType = 'second';
            }
          }
        }
      }
    }

    if (interval > 1 || interval === 0) {
      intervalType += 's';
    }
    return `${interval} ${intervalType}`;
  };

  return (
    <Stack direction={Direction.Vertical} shouldWrapItems={true} isFullWidth={true} childAlignment={Alignment.Center} contentAlignment={Alignment.Center}>
      <ResponsiveHidingView hiddenBelow={ScreenSize.Medium}>
        <Box variant='tokenSaleRow'>
          <Stack direction={Direction.Horizontal} shouldWrapItems={true} isFullWidth={true} childAlignment={Alignment.Center} contentAlignment={Alignment.Center}>
            <Box width='12rem'>
              <Account accountId={props.tokenTransfer?.fromAddress} />
            </Box>
            <Stack.Item baseSize='6rem' alignment={Alignment.Center}>
              <KibaIcon iconId='ion-arrow-forward' />
            </Stack.Item>
            <Box width='12rem'>
              <Account accountId={props.tokenTransfer?.toAddress} />
            </Box>
            <Stack.Item baseSize='12rem' alignment={Alignment.Center}>
              <Spacing variant={PaddingSize.Wide2} />
            </Stack.Item>
            <Stack.Item baseSize='12rem' alignment={Alignment.Center}>
              <Text alignment={TextAlignment.Center}>{`${shortFormatEther(props.tokenTransfer.value)}`}</Text>
            </Stack.Item>
            <Stack.Item baseSize='12rem' alignment={Alignment.Center}>
              <Text alignment={TextAlignment.Center}>{`${formatDate(props.tokenTransfer.blockDate)} ago`}</Text>
            </Stack.Item>
            <Stack.Item alignment={Alignment.Center}>
              <IconButton icon={<KibaIcon iconId='ion-open-outline' />} target={`https://etherscan.io/tx/${props.tokenTransfer.transactionHash}`} />
            </Stack.Item>
          </Stack>
        </Box>
      </ResponsiveHidingView>
      <ResponsiveHidingView hiddenAbove={ScreenSize.Medium}>
        <Stack direction={Direction.Vertical}isFullWidth={true} isFullHeight={true} childAlignment={Alignment.Center} contentAlignment={Alignment.Center} paddingLeft={PaddingSize.Wide} paddingRight={PaddingSize.Wide}>
          <Box variant='tokenSaleRow' isFullWidth={true}>
            <Stack direction={Direction.Horizontal} childAlignment={Alignment.Center} contentAlignment={Alignment.Center} padding={PaddingSize.Narrow}>
              <Stack.Item alignment={Alignment.Center}>
                <Text alignment={TextAlignment.Right}>{`${shortFormatEther(props.tokenTransfer.value)}`}</Text>
              </Stack.Item>
              <Spacing variant={PaddingSize.Wide2} />
              <Stack.Item alignment={Alignment.Center}>
                <Text alignment={TextAlignment.Left}>{`${formatDate(props.tokenTransfer.blockDate)} ago`}</Text>
              </Stack.Item>
              <Stack.Item alignment={Alignment.Center}>
                <IconButton icon={<KibaIcon iconId='ion-open-outline' />} target={`https://etherscan.io/tx/${props.tokenTransfer.transactionHash}`} />
              </Stack.Item>
            </Stack>
          </Box>
          <Box variant='tokenSaleRow'>
            <Stack direction={Direction.Horizontal} childAlignment={Alignment.Center} contentAlignment={Alignment.Center}>
              <Box width='6rem'>
                <Account accountId={props.tokenTransfer?.fromAddress} />
              </Box>
              <Stack.Item baseSize='5rem'>
                <KibaIcon iconId='ion-arrow-forward' />
              </Stack.Item>
              <Box width='6rem'>
                <Account accountId={props.tokenTransfer?.toAddress} />
              </Box>
            </Stack>
          </Box>
        </Stack>
      </ResponsiveHidingView>
    </Stack>
  );
};
