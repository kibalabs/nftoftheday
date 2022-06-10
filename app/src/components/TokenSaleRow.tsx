import React from 'react';

import { dateToRelativeString, shortFormatEther } from '@kibalabs/core';
import { Alignment, Box, Direction, IconButton, KibaIcon, PaddingSize, ResponsiveHidingView, ScreenSize, Spacing, Stack, Text, TextAlignment } from '@kibalabs/ui-react';

import { TokenTransfer } from '../client/resources';
import { Account } from './Account';

export interface ITokenSaleRowProps {
  tokenTransfer: TokenTransfer;
}

export const TokenSaleRow = (props: ITokenSaleRowProps): React.ReactElement => {
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
              <Text alignment={TextAlignment.Center}>{dateToRelativeString(props.tokenTransfer.blockDate)}</Text>
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
                <Text alignment={TextAlignment.Left}>{dateToRelativeString(props.tokenTransfer.blockDate)}</Text>
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
