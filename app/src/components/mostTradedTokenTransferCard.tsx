import React from 'react';

import { Requester } from '@kibalabs/core';
import { Alignment, Box, Button, Direction, LoadingSpinner, Media, PaddingSize, Spacing, Stack, Text, TextAlignment } from '@kibalabs/ui-react';

import { retrieveAsset } from '../assetUtil';
import { TokenTransfer } from '../client/resources';
import { Asset } from '../model';

export type MostTradedTokenTransferCardProps = {
  tokenTransfers: TokenTransfer[];
}

export const MostTradedTokenTransferCard = (props: MostTradedTokenTransferCardProps): React.ReactElement => {
  const [asset, setAsset] = React.useState<Asset | null>(null);

  const updateAsset = React.useCallback(async (): Promise<void> => {
    retrieveAsset(new Requester(), props.tokenTransfers[0].registryAddress, props.tokenTransfers[0].tokenId).then((retrievedAsset: Asset): void => {
      setAsset(retrievedAsset);
    });
  }, [props.tokenTransfers]);

  React.useEffect((): void => {
    if (!props.tokenTransfers) {
      setAsset(null);
      return;
    }
    updateAsset();
  }, [props.tokenTransfers, updateAsset]);

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
            <Text alignment={TextAlignment.Center}>{`Sold ${props.tokenTransfers.length} times today`}</Text>
            <Spacing variant={PaddingSize.Wide2} />
            <Text>{`Part of ${asset.collection.name}`}</Text>
            <Spacing variant={PaddingSize.Wide2} />
            <Stack direction={Direction.Horizontal} childAlignment={Alignment.Center} contentAlignment={Alignment.Start} shouldAddGutters={true}>
              <Button variant='secondary' target={`https://etherscan.io/tx/${props.tokenTransfers[0].transactionHash}`} text='View Tx' />
              <Button variant='primary' target={asset.openSeaUrl} text='View Token' />
            </Stack>
          </React.Fragment>
        )}
      </Stack>
    </Box>
  );
};
