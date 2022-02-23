import React from 'react';

import { dateToString } from '@kibalabs/core';
import { Alignment, Box, Direction, KibaIcon, PaddingSize, ResponsiveHidingView, ScreenSize, Spacing, Stack, Text, TextAlignment } from '@kibalabs/ui-react';

import { TokenTransfer } from '../client/resources';
import { Account } from './Account';

export interface TokenSaleRowProps {
  tokenSale: TokenTransfer;
}

export const TokenSaleRow = (props: TokenSaleRowProps): React.ReactElement => {
  return (
    <Stack direction={Direction.Vertical} shouldWrapItems={true} isFullWidth={true} childAlignment={Alignment.Center} contentAlignment={Alignment.Center}>
      <ResponsiveHidingView hiddenBelow={ScreenSize.Medium}>
        <Stack direction={Direction.Horizontal} isFullWidth={true} isFullHeight={true}childAlignment={Alignment.Center} contentAlignment={Alignment.Center}>
          <Box variant='tokenTable'>
            <Stack direction={Direction.Horizontal} shouldWrapItems={true} isFullWidth={true} childAlignment={Alignment.Center} contentAlignment={Alignment.Center}>
              <Stack.Item baseSize='12rem' alignment={Alignment.Center}>
                <Account accountId={props.tokenSale?.fromAddress} />
              </Stack.Item>
              <Stack.Item baseSize='6rem' alignment={Alignment.Center}>
                <KibaIcon iconId='ion-arrow-forward' />
              </Stack.Item>
              <Stack.Item baseSize='12rem' alignment={Alignment.Center}>
                <Account accountId={props.tokenSale?.toAddress} />
              </Stack.Item>
              <Stack.Item baseSize='12rem' alignment={Alignment.Center}>
                <Spacing variant={PaddingSize.Wide2} />
              </Stack.Item>
              <Stack.Item baseSize='12rem' alignment={Alignment.Center}>
                <Text alignment={TextAlignment.Center}>
                  { `Ξ${props.tokenSale.value / 1000000000000000000.0}`}
                </Text>
              </Stack.Item>
              <Stack.Item baseSize='12rem' alignment={Alignment.Center}>
                <Text alignment={TextAlignment.Center}>
                  {dateToString(props.tokenSale.blockDate, 'HH:mm')}
                </Text>
              </Stack.Item>
            </Stack>
          </Box>
        </Stack>
      </ResponsiveHidingView>
      <ResponsiveHidingView hiddenAbove={ScreenSize.Medium}>
        <Stack direction={Direction.Vertical}isFullWidth={true} isFullHeight={true} childAlignment={Alignment.Center} contentAlignment={Alignment.Center} paddingLeft={PaddingSize.Wide} paddingRight={PaddingSize.Wide}>
          <Box variant='tokenTable' isFullWidth={true}>
            <Stack direction={Direction.Horizontal} childAlignment={Alignment.Center} contentAlignment={Alignment.Center} padding={PaddingSize.Narrow}>
              <Stack.Item alignment={Alignment.Center}>
                <Text alignment={TextAlignment.Right}>
                  { `Ξ${props.tokenSale.value / 1000000000000000000.0}`}
                </Text>
              </Stack.Item>
              <Spacing variant={PaddingSize.Wide2} />
              <Stack.Item alignment={Alignment.Center}>
                <Text alignment={TextAlignment.Left}>
                  {dateToString(props.tokenSale.blockDate, 'HH:mm')}
                </Text>
              </Stack.Item>
            </Stack>
          </Box>
          <Box variant='tokenTable'>
            <Stack direction={Direction.Horizontal} childAlignment={Alignment.Start} contentAlignment={Alignment.Start}>
              <Stack.Item baseSize='5rem' alignment={Alignment.Center}>
                <Account accountId={props.tokenSale?.fromAddress} />
              </Stack.Item>
              <Stack.Item baseSize='3rem' alignment={Alignment.Center}>
                <KibaIcon iconId='ion-arrow-forward' />
              </Stack.Item>
              <Stack.Item baseSize='5rem' alignment={Alignment.Center}>
                <Account accountId={props.tokenSale?.toAddress} />
              </Stack.Item>
            </Stack>
          </Box>
        </Stack>
      </ResponsiveHidingView>
    </Stack>
  );
};
