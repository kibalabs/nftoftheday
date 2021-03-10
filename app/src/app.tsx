import React from 'react';

import { Requester, RestMethod } from '@kibalabs/core';
import { useFavicon } from '@kibalabs/core-react';
import { Alignment, BackgroundView, Box, Direction, IconButton, Image, KibaApp, KibaIcon, LoadingSpinner, PaddingSize, Spacing, Stack, Text } from '@kibalabs/ui-react';
// eslint-disable-next-line import/no-extraneous-dependencies
import { hot } from 'react-hot-loader/root';

import { Asset, AssetCollection, TokenTransfer } from './model';
import { asyncSleep } from './asyncUtil';
import { buildNotdTheme } from './theme';

const theme = buildNotdTheme();

const requester = new Requester();

const EXAMPLE_TOKEN_TRANSFER: TokenTransfer = {
  transactionHash: "0xcd2be787b6efa1006dd19a312ee9dea50340d77ac7546fbb62dd17242e83c458",
  registryAddress: "0x31af195db332bc9203d758c74df5a5c5e597cdb7",
  fromAddress: "0x0000000000000000000000000000000000000000",
  toAddress: "0xf55161739672929a20b94d611d2d98352e837e44",
  tokenId: 19894,
  value: 0,
  gasLimit: 2000000,
  gasPrice: 2200000000,
  gasUsed: 793693,
  blockDate: new Date(2019, 3, 17, 8, 58, 17),
}

export const App = hot((): React.ReactElement => {
  useFavicon('/assets/favicon.svg');
  const [tokenTransfer, setTokenTransfer] = React.useState<TokenTransfer | null>(null);
  const [asset, setAsset] = React.useState<Asset | null>(null);

  React.useEffect((): void => {
    asyncSleep(2).then(async (): Promise<void> => {
      setTokenTransfer(EXAMPLE_TOKEN_TRANSFER);
    });
  }, []);

  React.useEffect(async (): void => {
    if (!tokenTransfer) {
      setAsset(null);
      return;
    }
    const assetResponse = await requester.makeRequest(RestMethod.GET, `https://api.opensea.io/api/v1/asset/${tokenTransfer.registryAddress}/${tokenTransfer.tokenId}/`, undefined, { 'x-api-key': '' });
    const assetJson = JSON.parse(assetResponse.content);
    const assetCollection: AssetCollection = {
      name: assetJson.collection.name,
      imageUrl: assetJson.collection.large_image_url ?? assetJson.collection.image_url,
      openSeaUrl: assetJson.collection.permalink,
      externalUrl: assetJson.collection.external_link,
      description: assetJson.collection.description,
    };
    const latestAsset: Asset = {
      name: assetJson.name,
      imageUrl: assetJson.image_url ?? assetJson.original_image_url,
      openSeaUrl: assetJson.permalink,
      externalUrl: assetJson.external_link,
      description: assetJson.description,
      collection: assetCollection,
    };
    setAsset(latestAsset);
  }, [tokenTransfer]);

  return (
    <KibaApp theme={theme}>
      <BackgroundView linearGradient='#E56B6F, #6D597A'>
        <Stack direction={Direction.Vertical} isFullWidth={true} isFullHeight={true} childAlignment={Alignment.Center} contentAlignment={Alignment.Start} paddingStart={PaddingSize.Wide3} paddingEnd={PaddingSize.Wide3}>
          <Text variant='header1'>NFT of the day</Text>
          <Spacing variant={PaddingSize.Wide3} />
          {!asset ? (
            <LoadingSpinner variant='light-large' />
          ) : (
            <React.Fragment>
              <Box width='100px' height='100px'>
                <Image source={asset.imageUrl || asset.collection.imageUrl} alternativeText={`${asset.name} image`} />
              </Box>
              <Stack direction={Direction.Horizontal} childAlignment={Alignment.Center} contentAlignment={Alignment.Start} shouldAddGutters={true}>
                <IconButton icon={<KibaIcon iconId='ion-globe' />} target={asset.externalUrl || asset.openSeaUrl} />
                <Text variant='header2'>{`${asset.name || '(unnamed)'}`}</Text>
              </Stack>
              <Text>{`Part of ${asset.collection.name}`}</Text>
              <Text>{`Bought for Ξ${tokenTransfer.value / 1000000000000000000.0}`}</Text>
            </React.Fragment>
          )}
        </Stack>
      </BackgroundView>
    </KibaApp>
  );
});
