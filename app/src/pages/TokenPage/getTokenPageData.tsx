import { ethers } from 'ethers';

import { Collection, CollectionToken } from '../../client/resources';
import { IGlobals } from '../../globalsContext';

export interface ITokenPageData {
  collection: Collection | null;
  collectionToken: CollectionToken | null;
}

export const getTokenPageData = async (globals: IGlobals, params: Record<string, string>): Promise<ITokenPageData> => {
  const registryAddress = params.registryAddress;
  const tokenId = params.tokenId;
  if (!registryAddress) {
    console.error('Expected registryAddress and tokenId to be passed to getTokenPageData via params');
    return {
      collection: null,
      collectionToken: null,
    };
  }
  const checksumAddress = ethers.utils.getAddress(registryAddress);
  const collection = await globals.notdClient.getCollection(checksumAddress)
    .catch((error: unknown): void => {
      console.error(error);
    });
  const collectionToken = await globals.notdClient.getCollectionToken(checksumAddress, tokenId)
    .catch((error: unknown): void => {
      console.error(error);
    });
  return {
    collection: collection || null,
    collectionToken: collectionToken || null,
  };
};
