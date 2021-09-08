import { RegistryToken } from '../client/resources';

export const shouldUseIframe = (nft: RegistryToken): boolean => {
  const registryAddress = nft.registryAddress;
  const imageUrl = nft.imageUrl ?? nft.collectionImageUrl ?? null;
  if (imageUrl?.startsWith('https://api.artblocks.io/generator') || imageUrl?.startsWith('https://generator.artblocks.io')) {
    return (true);
  }
  if (registryAddress === '0x80416304142fa37929f8a4eee83ee7d2dac12d7c') {
    return (true);
  }

  return (false);
};
