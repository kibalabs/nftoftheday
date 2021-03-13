import React from 'react';

import { dateToString, Requester, RestMethod } from '@kibalabs/core';
import { useFavicon } from '@kibalabs/core-react';
import { Alignment, BackgroundView, Box, Direction, IconButton, Image, KibaApp, KibaIcon, LoadingSpinner, Markdown, MarkdownText, PaddingSize, Spacing, Stack, Text } from '@kibalabs/ui-react';
// eslint-disable-next-line import/no-extraneous-dependencies
import { hot } from 'react-hot-loader/root';

import { NotdClient } from './client/client';
import { TokenTransfer, UiData } from './client/resources';
import { Asset, AssetCollection } from './model';
import { buildNotdTheme } from './theme';
import './fonts.css';

const theme = buildNotdTheme();

const requester = new Requester();
const notdClient = new NotdClient(requester);

const defaultDate = new Date(2021, 2, 13);
defaultDate.setHours(0, 0, 0, 0);

export const App = hot((): React.ReactElement => {
  useFavicon('/assets/favicon.svg');
  const [highestPricedTokenTransfer, setHighestPricedTokenTransfer] = React.useState<TokenTransfer | null>(null);
  const [asset, setAsset] = React.useState<Asset | null>(null);
  const [startDate, setStartDate] = React.useState<Date | null>(defaultDate);

  React.useEffect((): void => {
    notdClient.retrieveUiData(startDate).then((uiData: UiData): void => {
      setHighestPricedTokenTransfer(uiData.highestPricedTokenTransfer);
    });
  }, []);

  const updateAsset = React.useCallback(async (): Promise<void> => {
    const assetResponse = await requester.makeRequest(RestMethod.GET, `https://api.opensea.io/api/v1/asset/${highestPricedTokenTransfer.registryAddress}/${highestPricedTokenTransfer.tokenId}/`, undefined, { 'x-api-key': '' });
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
  }, [highestPricedTokenTransfer]);

  React.useEffect((): void => {
    if (!highestPricedTokenTransfer) {
      setAsset(null);
      return;
    }
    updateAsset();
  }, [highestPricedTokenTransfer, updateAsset]);

  const getDateString = (): string => {
    const currentDate = new Date();
    if (startDate.getDate() == currentDate.getDate()) {
      return 'Today';
    }
    if (startDate.getDate() == new Date(currentDate.setDate(currentDate.getDate() - 1)).getDate()) {
      return 'Yesterday';
    }
    return dateToString(startDate, 'dd MMMM yyyy')
  }

  return (
    <KibaApp theme={theme}>
      <BackgroundView linearGradient='#200122,#6F0000'>
        <Stack direction={Direction.Vertical} isFullWidth={true} isFullHeight={true} childAlignment={Alignment.Center} contentAlignment={Alignment.Start}>
          <Spacing variant={PaddingSize.Wide3} />
          <Text variant='header1'>NFT of the day</Text>
          <Spacing variant={PaddingSize.Default} />
          <Text variant='header3'>{getDateString()}</Text>
          <Stack.Item growthFactor={1} shrinkFactor={1}>
            <Spacing variant={PaddingSize.Wide3} />
          </Stack.Item>
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
              <Text>{`Bought for Ξ${highestPricedTokenTransfer.value / 1000000000000000000.0}`}</Text>
            </React.Fragment>
          )}
          <Stack.Item growthFactor={1} shrinkFactor={1}>
            <Spacing variant={PaddingSize.Wide3} />
          </Stack.Item>
          <MarkdownText source='Made by [Kiba Labs](https://www.kibalabs.com)' />
        </Stack>
      </BackgroundView>
    </KibaApp>
  );
});
