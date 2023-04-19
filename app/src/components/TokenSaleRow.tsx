import React from 'react';

import { dateToRelativeString, shortFormatEther } from '@kibalabs/core';
import { Alignment, Box, Direction, IconButton, KibaIcon, PaddingSize, ResponsiveHidingView, ScreenSize, Spacing, Stack, Text, TextAlignment } from '@kibalabs/ui-react';

import { Account } from './Account';
import { SmallTokenViewLink } from './SmallTokenView';
import { TokenTransfer } from '../client/resources';

export interface ITokenSaleRowProps {
  tokenTransfer: TokenTransfer;
  showToken?: boolean;
}

export const TokenSaleRow = (props: ITokenSaleRowProps): React.ReactElement => {
  return (
    <Stack direction={Direction.Vertical} shouldWrapItems={true} isFullWidth={true} childAlignment={Alignment.Center} contentAlignment={Alignment.Center}>
      <ResponsiveHidingView hiddenBelow={ScreenSize.Medium}>
        <Box variant='tokenSaleRow'>
          <Stack direction={Direction.Horizontal} paddingHorizontal={PaddingSize.Default} shouldWrapItems={true} isFullWidth={true} childAlignment={Alignment.Center} contentAlignment={Alignment.Center}>
            {props.showToken && (
              <Box width='10rem'>
                <SmallTokenViewLink registryAddress={props.tokenTransfer.registryAddress} tokenId={props.tokenTransfer.tokenId} target={`/collections/${props.tokenTransfer.registryAddress}/tokens/${props.tokenTransfer.tokenId}`} />
              </Box>
            )}
            <Box width='9rem'>
              <Account accountId={props.tokenTransfer?.fromAddress} target={`/accounts/${props.tokenTransfer?.fromAddress}`} />
            </Box>
            <Stack.Item baseSize='2rem' alignment={Alignment.Center}>
              <KibaIcon iconId='ion-arrow-forward' />
            </Stack.Item>
            <Box width='9rem'>
              <Account accountId={props.tokenTransfer?.toAddress} target={`/accounts/${props.tokenTransfer?.toAddress}`} />
            </Box>
            <Stack.Item growthFactor={1} shrinkFactor={1}>
              <Spacing variant={PaddingSize.Wide} />
            </Stack.Item>
            <Stack.Item baseSize='5rem' alignment={Alignment.Center}>
              <Text alignment={TextAlignment.Center}>{`${shortFormatEther(BigInt(props.tokenTransfer.value.toString()))}`}</Text>
            </Stack.Item>
            <Stack.Item baseSize='7rem' alignment={Alignment.Center}>
              <Text alignment={TextAlignment.Center}>{dateToRelativeString(props.tokenTransfer.blockDate)}</Text>
            </Stack.Item>
            <Stack.Item alignment={Alignment.Center}>
              <IconButton icon={<KibaIcon iconId='ion-open-outline' />} target={`https://etherscan.io/tx/${props.tokenTransfer.transactionHash}`} />
            </Stack.Item>
          </Stack>
        </Box>
      </ResponsiveHidingView>
      <ResponsiveHidingView hiddenAbove={ScreenSize.Medium}>
        <Box variant='tokenSaleRow' isFullWidth={true}>
          <Stack direction={Direction.Vertical} isFullWidth={true} isFullHeight={true} childAlignment={Alignment.Center} contentAlignment={Alignment.Center} paddingHorizontal={PaddingSize.Wide} paddingVertical={PaddingSize.Default}>
            {props.showToken && (
              <SmallTokenViewLink registryAddress={props.tokenTransfer.registryAddress} tokenId={props.tokenTransfer.tokenId} target={`/collections/${props.tokenTransfer.registryAddress}/tokens/${props.tokenTransfer.tokenId}`} />
            )}
            <Stack direction={Direction.Horizontal} childAlignment={Alignment.Center} contentAlignment={Alignment.Center}>
              <Box width='6rem'>
                <Account accountId={props.tokenTransfer?.fromAddress} target={`/accounts/${props.tokenTransfer?.fromAddress}`} />
              </Box>
              <Stack.Item baseSize='5rem'>
                <KibaIcon iconId='ion-arrow-forward' />
              </Stack.Item>
              <Box width='6rem'>
                <Account accountId={props.tokenTransfer?.toAddress} target={`/accounts/${props.tokenTransfer?.toAddress}`} />
              </Box>
            </Stack>
            <Stack direction={Direction.Horizontal} childAlignment={Alignment.Center} contentAlignment={Alignment.Center} padding={PaddingSize.Narrow}>
              <Stack.Item alignment={Alignment.Center}>
                <Text alignment={TextAlignment.Right}>{`${shortFormatEther(BigInt(props.tokenTransfer.value.toString()))}`}</Text>
              </Stack.Item>
              <Spacing variant={PaddingSize.Wide2} direction={Direction.Horizontal} />
              <Stack.Item alignment={Alignment.Center}>
                <Text alignment={TextAlignment.Left}>{dateToRelativeString(props.tokenTransfer.blockDate)}</Text>
              </Stack.Item>
              <Stack.Item alignment={Alignment.Center}>
                <IconButton variant='small' icon={<KibaIcon variant='small' iconId='ion-open-outline' />} target={`https://etherscan.io/tx/${props.tokenTransfer.transactionHash}`} />
              </Stack.Item>
            </Stack>
          </Stack>
        </Box>
      </ResponsiveHidingView>
    </Stack>
  );
};
TokenSaleRow.displayName = 'TokenSaleRow';
