import React from 'react';

import { ApolloClient, ApolloQueryResult, gql, InMemoryCache } from '@apollo/client';
import { Requester, RestMethod } from '@kibalabs/core';
import { useFavicon } from '@kibalabs/core-react';
import { Alignment, BackgroundView, Box, Direction, IconButton, Image, KibaApp, KibaIcon, LoadingSpinner, PaddingSize, Spacing, Stack, Text } from '@kibalabs/ui-react';
// eslint-disable-next-line import/no-extraneous-dependencies
import { hot } from 'react-hot-loader/root';
import Web3 from 'web3';

import { Asset, AssetCollection, Transaction } from './model';
import { buildNotdTheme } from './theme';

const theme = buildNotdTheme();

const web3Client = new Web3(window.ethereum);
// const web3Provider = new Web3.providers.HttpProvider('https://mainnet.infura.io');
// const openSeaClient = new OpenSeaPort(web3Provider);

const requester = new Requester();

const nftGraphClient = new ApolloClient({
  uri: 'https://api.thegraph.com/subgraphs/name/amxx/eip721-subgraph',
  cache: new InMemoryCache(),
});

export const App = hot((): React.ReactElement => {
  useFavicon('/assets/favicon.svg');
  const [asset, setAsset] = React.useState<Asset | null>(null);
  const [assetTransaction, setAssetTransaction] = React.useState<Transaction | null>(null);

  React.useEffect((): void => {
    nftGraphClient.query({
      query: gql`
        query getLatestNft {
          transfers(first: 1, orderBy: timestamp, orderDirection: desc) {
            id
            transaction {
              id
              timestamp
            }
            timestamp
            token {
              id
              registry {
                id
                name
                symbol
              }
              identifier
            }
            from {
              id
            }
            to {
              id
            }
          }
        }
      `,
    })
      .then(async (result: ApolloQueryResult<unknown>) => {
        const transfers = result.data.transfers;
        // console.log('transfers', transfers);
        transfers.forEach(async (transfer: unknown): Promise<void> => {
          // const transferDate = new Date(parseInt(transfer.timestamp, 10) * 1000);
          // console.log(`Transfer at ${transferDate} from ${transfer.from.id} to ${transfer.to.id} at ${transfer.transaction.id}`);
          const transaction = await web3Client.eth.getTransaction(transfer.transaction.id);
          // console.log('transaction', transaction);
          const transactionReceipt = await web3Client.eth.getTransactionReceipt(transfer.transaction.id);
          // console.log('transactionReceipt', transactionReceipt);
          setAssetTransaction({
            hash: transaction.hash,
            from: transaction.from,
            to: transaction.to,
            value: parseInt(transaction.value, 10),
            gasPrice: transaction.gasPrice,
            gasUsed: transactionReceipt.gasUsed,
          });
          const assetResponse = await requester.makeRequest(RestMethod.GET, `https://api.opensea.io/api/v1/asset/${transfer.token.registry.id}/${transfer.token.identifier}/`, undefined, { 'x-api-key': '' });
          const assetJson = JSON.parse(assetResponse.content);
          // console.log('assetJson', assetJson);
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
          // console.log('asset', asset);
          setAsset(latestAsset);
        });
      });
  }, []);

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
              <Text>{`Bought for Ξ${assetTransaction.value / 1000000000000000000.0}`}</Text>
            </React.Fragment>
          )}
        </Stack>
      </BackgroundView>
    </KibaApp>
  );
});
