import React from 'react';

import { Requester, RestMethod } from '@kibalabs/core';
import { useFavicon } from '@kibalabs/core-react';
import { Alignment, BackgroundView, Box, Direction, IconButton, Image, KibaApp, KibaIcon, LoadingSpinner, PaddingSize, Spacing, Stack, Text } from '@kibalabs/ui-react';
// eslint-disable-next-line import/no-extraneous-dependencies
import { hot } from 'react-hot-loader/root';

import { NotdClient } from './client/client';
import { TokenTransfer, UiData } from './client/resources';
import { Asset, AssetCollection } from './model';
import { buildNotdTheme } from './theme';

const theme = buildNotdTheme();

const requester = new Requester();
const notdClient = new NotdClient(requester, 'http://localhost:5000');

export const App = hot((): React.ReactElement => {
  useFavicon('/assets/favicon.svg');
  const [tokenTransfer, setTokenTransfer] = React.useState<TokenTransfer | null>(null);
  const [asset, setAsset] = React.useState<Asset | null>(null);

  React.useEffect((): void => {
    const startDate = new Date(2021, 2, 10);
    startDate.setHours(0, 0, 0, 0);
    notdClient.retrieveUiData(startDate).then((uiData: UiData): void => {
      setTokenTransfer(uiData.highestPricedTokenTransfer);
    });
  }, []);

  const updateAsset = React.useCallback(async (): Promise<void> => {
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

  React.useEffect((): void => {
    if (!tokenTransfer) {
      setAsset(null);
      return;
    }
    updateAsset();
  }, [tokenTransfer, updateAsset]);

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
