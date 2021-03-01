

export interface Transaction {
  hash: string;
  from: string;
  to: string;
  value: number;
  gasPrice: string;
  gasUsed: number;
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
