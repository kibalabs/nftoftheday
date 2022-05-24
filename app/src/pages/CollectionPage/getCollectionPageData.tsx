import { ethers } from 'ethers';

import { Collection } from '../../client/resources';
import { IGlobals } from '../../globalsContext';

export interface ICollectionPageData {
  collection: Collection | null;
}

export const getCollectionPageData = async (globals: IGlobals, params: Record<string, string>): Promise<ICollectionPageData> => {
  const address = params.address;
  if (!address) {
    console.error('Expected address to be passed to getCollectionPageData via params');
    return {
      collection: null,
    };
  }
  const checksumAddress = ethers.utils.getAddress(address);
  const collection = await globals.notdClient.getCollection(checksumAddress)
    .catch((error: unknown): void => {
      console.error(error);
    });
  return {
    collection: collection || null,
  };
};
