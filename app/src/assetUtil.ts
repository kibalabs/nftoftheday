import { dateFromString, Requester, RestMethod } from '@kibalabs/core';

import { asyncSleep } from './asyncUtil';
import { RegistryToken } from './client/resources';

export const retrieveAsset = async (requester: Requester, registryAddress: string, tokenId: string): Promise<RegistryToken> => {
  let assetResponse = null;
  let retryCount = 0;
  while (!assetResponse) {
    try {
      // eslint-disable-next-line no-await-in-loop
      assetResponse = await requester.makeRequest(RestMethod.GET, `https://api.opensea.io/api/v1/asset/${registryAddress}/${tokenId}/`, undefined, { 'x-api-key': '' });
    } catch (exception) {
      if (retryCount >= 3) {
        throw exception;
      }
      // eslint-disable-next-line no-console
      console.log(`Retrying due to: ${exception}`);
      // eslint-disable-next-line no-await-in-loop
      await asyncSleep(1.5);
      retryCount += 1;
    }
  }
  const assetJson = JSON.parse(assetResponse.content);
  const asset: RegistryToken = {
    name: assetJson.name ?? `${assetJson.collection.name} #${tokenId}`,
    imageUrl: assetJson.animation_url ?? assetJson.image_url ?? assetJson.original_image_url,
    openSeaUrl: `${assetJson.permalink}?ref=0x18090cda49b21deaffc21b4f886aed3eb787d032`,
    externalUrl: assetJson.external_link,
    lastSaleDate: assetJson.last_sale ? dateFromString(assetJson.last_sale.created_date as string) : null,
    lastSalePrice: assetJson.last_sale ? Number(assetJson.last_sale.total_price) : null,
    collectionName: assetJson.collection.name,
    collectionImageUrl: assetJson.collection.large_image_url ?? assetJson.collection.image_url,
    collectionOpenSeaUrl: assetJson.collection.permalink ? `${assetJson.collection.permalink}?ref=0x18090cda49b21deaffc21b4f886aed3eb787d032` : null,
    collectionExternalUrl: assetJson.collection.external_url,
  };
  return asset;
};
