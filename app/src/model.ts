

export interface TokenTransfer {
  transactionHash: string;
  registryAddress: string;
  fromAddress: string;
  toAddress: string;
  tokenId: number;
  value: number;
  gasLimit: number;
  gasPrice: number;
  gasUsed: number;
  blockDate: Date;
}

export interface AssetCollection {
  name: string;
  description: string;
  imageUrl: string;
  openSeaUrl: string;
  externalUrl: string;
}

export interface Asset {
  name: string;
  description: string;
  imageUrl: string;
  openSeaUrl: string;
  externalUrl: string;
  collection: AssetCollection;
}
