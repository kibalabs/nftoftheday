import { ethers } from 'ethers';

import { Collection } from '../../client/resources';
import { IGlobals } from '../../globalsContext';

export interface ICollectionPageData {
  collection: Collection;
}

export const getCollectionPageData = async (globals: IGlobals, params: Record<string, string>): Promise<ICollectionPageData | null> => {
  const address = params.address;
  if (!address) {
    console.error('Expected address to be passed to getCollectionPageData via params');
    return null;
  }
  const checksumAddress = ethers.utils.getAddress(address);
  const collection = await globals.notdClient.getCollection(checksumAddress)
    .catch((error: unknown): void => {
      console.error(error);
    });
  if (collection) {
    return { collection };
  }
  return null;
};
