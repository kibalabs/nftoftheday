import React from 'react';

import { Requester, RestMethod } from '@kibalabs/core';
import { useFavicon } from '@kibalabs/core-react';
import { Alignment, BackgroundView, Direction, EqualGrid, KibaApp, Link, LoadingSpinner, PaddingSize, Spacing, Stack, Text, TextAlignment } from '@kibalabs/ui-react';
// eslint-disable-next-line import/no-extraneous-dependencies
import { hot } from 'react-hot-loader/root';

import { NotdClient } from './client/client';
import { TokenTransfer, UiData } from './client/resources';
import { NftCard } from './components/nftCard';
import { Asset, AssetCollection } from './model';
import { buildNotdTheme } from './theme';
import './fonts.css';

const theme = buildNotdTheme();

const requester = new Requester();
const notdClient = new NotdClient(requester);

export const App = hot((): React.ReactElement => {
  useFavicon('/assets/favicon.svg');
  const [highestPricedTokenTransfer, setHighestPricedTokenTransfer] = React.useState<TokenTransfer | null>(null);
  const [asset, setAsset] = React.useState<Asset | null>(null);

  React.useEffect((): void => {
    const startDate = new Date(2021, 2, 10);
    startDate.setHours(0, 0, 0, 0);
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

  return (
    <KibaApp theme={theme}>
      <BackgroundView linearGradient='#200122,#6F0000'>
        <Stack direction={Direction.Vertical} isFullWidth={true} isFullHeight={true} childAlignment={Alignment.Center} contentAlignment={Alignment.Start} paddingStart={PaddingSize.Wide3} paddingEnd={PaddingSize.Wide3}>
          <Text variant='header1'>NFT of the day</Text>
          <Spacing variant={PaddingSize.Wide} />
          <Text variant='header3'>Today</Text>
          <Spacing variant={PaddingSize.Wide3} />
          <EqualGrid childSizeResponsive={{ base: 12, small: 6, medium: 3 }} contentAlignment={Alignment.Center} shouldAddGutters={true}>
            {!asset ? (
              <LoadingSpinner variant='light-large' />
            ) : (
            /*
             * when 4 card are added then it doesn't look that good
             * I was not sure what to pass in subtitle and button target
             */
              <React.Fragment>
                <NftCard
                  label='Random'
                  title={asset.name}
                  subtitle='Sold at 14:00 for 0.04Ξ'
                  collectionImage={asset.collection.imageUrl}
                  collectionTitle={asset.collection.name}
                  imageUrl={asset.imageUrl}
                  secondaryButtonText='View Transaction'
                  secondaryButtonTarget={asset.externalUrl}
                  primaryButtonText='View Token'
                  primaryButtonTarget={asset.collection.name}
                />
                <NftCard
                  label='Highest Priced Trade'
                  title={asset.name}
                  subtitle='Sold at 14:00 for 0.04Ξ'
                  collectionTitle={asset.collection.name}
                  imageUrl={asset.imageUrl}
                />
                <NftCard
                  label='Sponsored'
                  title={asset.name}
                  subtitle='Sold at 14:00 for 0.04Ξ'
                  collectionImage={asset.collection.imageUrl}
                  collectionTitle={asset.collection.name}
                  imageUrl={asset.imageUrl}
                  secondaryButtonText='View Transaction'
                  secondaryButtonTarget={asset.externalUrl}
                />
              </React.Fragment>
            )}
          </EqualGrid>
        </Stack>
        <Spacing variant={PaddingSize.Wide4}/>
        <Text alignment={TextAlignment.Center}>Made by <Link target='//#endregion' text='KibaLabs' /></Text>
      </BackgroundView>
    </KibaApp>
  );
});
