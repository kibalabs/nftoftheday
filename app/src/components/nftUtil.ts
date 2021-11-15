export const shouldUseIframe = (imageUrl: string, registryAddress: string): boolean => {
  if (imageUrl?.startsWith('https://api.artblocks.io/generator') || imageUrl?.startsWith('https://generator.artblocks.io')) {
    return true;
  }
  if (registryAddress === '0x80416304142fa37929f8a4eee83ee7d2dac12d7c') {
    return true;
  }
  return false;
};
