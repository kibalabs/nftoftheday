
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
