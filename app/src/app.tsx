import React from 'react';

import { ApolloClient, ApolloQueryResult, gql, InMemoryCache } from '@apollo/client';
import { Requester, RestMethod } from '@kibalabs/core';
import { useFavicon, useInitialization } from '@kibalabs/core-react';
import { Alignment, BackgroundView, Direction, KibaApp, PaddingSize, Stack, Text } from '@kibalabs/ui-react';
// eslint-disable-next-line import/no-extraneous-dependencies
import { hot } from 'react-hot-loader/root';
import Web3 from 'web3';

import { buildNotdTheme } from './theme';

const theme = buildNotdTheme();

const web3Client = new Web3(window.ethereum);
const requester = new Requester();

const nftGraphClient = new ApolloClient({
  uri: 'https://api.thegraph.com/subgraphs/name/amxx/eip721-subgraph',
  cache: new InMemoryCache()
});

export const App = hot((): React.ReactElement => {
  useFavicon('/assets/favicon.svg');

  React.useEffect((): void => {
    nftGraphClient.query({
      query: gql`
        query getLatestNft {
          transfers(first: 10, orderBy: timestamp, orderDirection: desc) {
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
      `
    })
    .then(async (result: ApolloQueryResult<unknown>) => {
      const transfers = result.data.transfers;
      console.log('transfers', transfers);
      transfers.forEach(async (transfer: unknown): Promise<void> => {
        const transferDate = new Date(parseInt(transfer.timestamp, 10) * 1000);
        console.log(`Transfer at ${transferDate} from ${transfer.from.id} to ${transfer.to.id} at ${transfer.transaction.id}`);
        const transaction = await web3Client.eth.getTransaction(transfer.transaction.id);
        console.log('transaction', transaction);
        const assetResponse = await requester.makeRequest(RestMethod.GET, `https://api.opensea.io/api/v1/asset/${transfer.token.registry.id}/${transfer.token.identifier}/`)
        console.log('assetResponse', JSON.parse(assetResponse.content));
      });
    });
  }, []);

  return (
    <KibaApp theme={theme}>
      <BackgroundView linearGradient='#E56B6F, #6D597A'>
        <Stack direction={Direction.Vertical} isFullWidth={true} isFullHeight={true} childAlignment={Alignment.Center} paddingStart={PaddingSize.Wide3} paddingEnd={PaddingSize.Wide3}>
          <Text variant='header1'>NFT of the day</Text>
        </Stack>
      </BackgroundView>
    </KibaApp>
  );
});
