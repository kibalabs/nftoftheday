import { dateFromString, Requester, RestMethod } from '@kibalabs/core';

import { Asset, AssetCollection } from './model';

export const retrieveAsset = async (requester: Requester, registryAddress: string, tokenId: string): Promise<Asset> => {
  const assetResponse = await requester.makeRequest(RestMethod.GET, `https://api.opensea.io/api/v1/asset/${registryAddress}/${tokenId}/`, undefined, { 'x-api-key': '' });
  const assetJson = JSON.parse(assetResponse.content);
  console.log('assetJson', assetJson);
  const assetCollection: AssetCollection = {
    name: assetJson.collection.name,
    imageUrl: assetJson.collection.large_image_url ?? assetJson.collection.image_url,
    openSeaUrl: assetJson.collection.permalink,
    externalUrl: assetJson.collection.external_url,
    description: assetJson.collection.description,
  };
  const asset: Asset = {
    name: assetJson.name,
    imageUrl: assetJson.animation_url ?? assetJson.image_url ?? assetJson.original_image_url,
    openSeaUrl: assetJson.permalink,
    externalUrl: assetJson.external_link,
    description: assetJson.description,
    lastSaleDate: assetJson.last_sale ? dateFromString(assetJson.last_sale.created_date as string) : null,
    lastSalePrice: assetJson.last_sale ? Number(assetJson.last_sale.total_price) : null,
    collection: assetCollection,
  };
  return asset;
};
