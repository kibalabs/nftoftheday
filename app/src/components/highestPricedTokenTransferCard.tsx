import React from 'react';

import { dateToString, Requester } from '@kibalabs/core';
import { Alignment, Box, Button, Direction, LoadingSpinner, Media, PaddingSize, Spacing, Stack, Text, TextAlignment } from '@kibalabs/ui-react';

import { retrieveAsset } from '../assetUtil';
import { TokenTransfer } from '../client/resources';
import { Asset } from '../model';

export type HighestPricedTokenTransferCardProps = {
  tokenTransfer: TokenTransfer;
}

export const HighestPricedTokenTransferCard = (props: HighestPricedTokenTransferCardProps): React.ReactElement => {
  const [asset, setAsset] = React.useState<Asset | null>(null);

  const updateAsset = React.useCallback(async (): Promise<void> => {
    retrieveAsset(new Requester(), props.tokenTransfer.registryAddress, props.tokenTransfer.tokenId).then((retrievedAsset: Asset): void => {
      setAsset(retrievedAsset);
    });
  }, [props.tokenTransfer]);

  React.useEffect((): void => {
    if (!props.tokenTransfer) {
      setAsset(null);
      return;
    }
    updateAsset();
  }, [props.tokenTransfer, updateAsset]);

  return (
    <Box variant='card' isFullWidth={true} isFullHeight={false}>
      <Stack direction={Direction.Vertical} isFullWidth={true} isFullHeight={true} childAlignment={Alignment.Center} contentAlignment={Alignment.Start}>
        { !asset ? (
          <LoadingSpinner variant='light' />
        ) : (
          <React.Fragment>
            <Stack.Item gutterAfter={PaddingSize.Wide2}>
              <Box width='150px' height='150px'>
                <Media source={asset.imageUrl || asset.collection.imageUrl} alternativeText={`${asset.name} image`} />
              </Box>
            </Stack.Item>
            <Text variant='header3' alignment={TextAlignment.Center}>{`${asset.name || '(unnamed)'}`}</Text>
            <Text alignment={TextAlignment.Center}>{`Sold at ${dateToString(props.tokenTransfer.blockDate, 'HH:mm')} for Ξ${props.tokenTransfer.value / 1000000000000000000.0}`}</Text>
            <Spacing variant={PaddingSize.Wide2} />
            <Text>{`Part of ${asset.collection.name}`}</Text>
            <Spacing variant={PaddingSize.Wide2} />
            <Stack direction={Direction.Horizontal} childAlignment={Alignment.Center} contentAlignment={Alignment.Start} shouldAddGutters={true}>
              <Button variant='secondary' target={`https://etherscan.io/tx/${props.tokenTransfer.transactionHash}`} text='View Tx' />
              <Button variant='primary' target={asset.openSeaUrl} text='View Token' />
            </Stack>
          </React.Fragment>
        )}
      </Stack>
    </Box>
  );
};
