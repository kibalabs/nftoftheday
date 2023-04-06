import { dateFromString, ResponseData } from '@kibalabs/core';
import { BigNumber } from 'ethers';

export class TokenTransfer extends ResponseData {
  public constructor(
    readonly tokenTransferId: number,
    readonly transactionHash: string,
    readonly registryAddress: string,
    readonly fromAddress: string,
    readonly toAddress: string,
    readonly tokenId: string,
    readonly value: BigNumber,
    readonly gasLimit: number,
    readonly gasPrice: number,
    readonly gasUsed: number,
    readonly blockNumber: number,
    readonly blockHash: string,
    readonly blockDate: Date,
    readonly token: CollectionToken,
    readonly isMultiAddress: boolean,
    readonly isInterstitial: boolean,
    readonly isSwap: boolean,
    readonly isBatch: boolean,
    readonly isOutbound: boolean,

  ) { super(); }

  public static fromObject = (obj: Record<string, unknown>): TokenTransfer => {
    return new TokenTransfer(
      Number(obj.tokenTransferId),
      String(obj.transactionHash),
      String(obj.registryAddress),
      String(obj.fromAddress),
      String(obj.toAddress),
      String(obj.tokenId),
      BigNumber.from(String(obj.value)),
      Number(obj.gasLimit),
      Number(obj.gasPrice),
      Number(obj.gasUsed),
      Number(obj.blockNumber),
      String(obj.blockHash),
      dateFromString(obj.blockDate as string),
      CollectionToken.fromObject(obj.token as Record<string, unknown>),
      Boolean(obj.isMultiAddress),
      Boolean(obj.isInterstitial),
      Boolean(obj.isSwap),
      Boolean(obj.isBatch),
      Boolean(obj.isOutbound),
    );
  };
}


export class TokenTransferValue {
  readonly registryAddress: string;
  readonly tokenId: string;
  readonly value: BigNumber;
  readonly blockDate: Date;

  public constructor(registryAddress: string, tokenId: string, value: BigNumber, blockDate: Date) {
    this.registryAddress = registryAddress;
    this.tokenId = tokenId;
    this.value = value;
    this.blockDate = blockDate;
  }

  public static fromObject = (obj: Record<string, unknown>): TokenTransferValue => {
    return new TokenTransferValue(
      String(obj.registryAddress),
      String(obj.tokenId),
      BigNumber.from(String(obj.value)),
      dateFromString(obj.blockDate as string),
    );
  };
}


export class TokenAttribute {
  readonly traitType: string;
  readonly value: string;

  public constructor(traitType: string, value: string) {
    this.traitType = traitType;
    this.value = value;
  }

  public static fromObject = (obj: Record<string, unknown>): TokenAttribute => {
    return new TokenAttribute(
      String(obj.trait_type),
      String(obj.value),
    );
  };
}

export class CollectionToken {
  readonly registryAddress: string;
  readonly tokenId: string;
  readonly name: string;
  readonly resizableImageUrl: string | null;
  readonly imageUrl: string | null;
  readonly description: string | null;
  readonly attributes: TokenAttribute[];

  public constructor(registryAddress: string, tokenId: string, name: string, resizableImageUrl: string | null, imageUrl: string | null, description: string | null, attributes: TokenAttribute[]) {
    this.registryAddress = registryAddress;
    this.tokenId = tokenId;
    this.name = name;
    this.resizableImageUrl = resizableImageUrl;
    this.imageUrl = imageUrl;
    this.description = description;
    this.attributes = attributes;
  }

  public static fromObject = (obj: Record<string, unknown>): CollectionToken => {
    return new CollectionToken(
      String(obj.registryAddress),
      String(obj.tokenId),
      String(obj.name),
      obj.resizableImageUrl ? String(obj.resizableImageUrl) : null,
      obj.imageUrl ? String(obj.imageUrl) : null,
      obj.description ? String(obj.description) : null,
      (obj.attributes as Record<string, unknown>[]).map((innerObj: Record<string, unknown>) => TokenAttribute.fromObject(innerObj)),
    );
  };
}

export class Collection {
  readonly address: string;
  readonly name: string | null;
  readonly imageUrl: string | null;
  readonly description: string | null;
  readonly url: string | null;
  readonly openseaSlug: string | null;
  readonly bannerImageUrl: string | null;
  readonly discordUrl: string | null;
  readonly instagramUsername: string | null;
  readonly twitterUsername: string | null;

  public constructor(address: string, name: string | null, imageUrl: string | null, description: string | null, url: string | null, openseaSlug: string | null, bannerImageUrl: string | null, discordUrl: string | null, instagramUsername: string | null, twitterUsername: string | null) {
    this.address = address;
    this.name = name;
    this.imageUrl = imageUrl;
    this.description = description;
    this.url = url;
    this.openseaSlug = openseaSlug;
    this.bannerImageUrl = bannerImageUrl;
    this.discordUrl = discordUrl;
    this.instagramUsername = instagramUsername;
    this.twitterUsername = twitterUsername;
  }

  public static fromObject = (obj: Record<string, unknown>): Collection => {
    return new Collection(
      String(obj.address),
      obj.name ? String(obj.name) : null,
      obj.imageUrl ? String(obj.imageUrl) : null,
      obj.description ? String(obj.description) : null,
      obj.url ? String(obj.url) : null,
      obj.openseaSlug ? String(obj.openseaSlug) : null,
      obj.bannerImageUrl ? String(obj.bannerImageUrl) : null,
      obj.discordUrl ? String(obj.discordUrl) : null,
      obj.instagramUsername ? String(obj.instagramUsername) : null,
      obj.twitterUsername ? String(obj.twitterUsername) : null,
    );
  };
}


export class CollectionStatistics {
  readonly itemCount: number;
  readonly holderCount: number;
  readonly totalTradeVolume: BigNumber;
  readonly lowestSaleLast24Hours: BigNumber;
  readonly highestSaleLast24Hours: BigNumber;
  readonly tradeVolume24Hours: BigNumber;

  public constructor(itemCount: number, holderCount: number, totalTradeVolume: BigNumber, lowestSaleLast24Hours: BigNumber, highestSaleLast24Hours: BigNumber, tradeVolume24Hours: BigNumber) {
    this.itemCount = itemCount;
    this.holderCount = holderCount;
    this.totalTradeVolume = totalTradeVolume;
    this.lowestSaleLast24Hours = lowestSaleLast24Hours;
    this.highestSaleLast24Hours = highestSaleLast24Hours;
    this.tradeVolume24Hours = tradeVolume24Hours;
  }

  public static fromObject = (obj: Record<string, unknown>): CollectionStatistics => {
    return new CollectionStatistics(
      Number(obj.itemCount),
      Number(obj.holderCount),
      BigNumber.from(String(obj.totalTradeVolume)),
      BigNumber.from(String(obj.lowestSaleLast24Hours)),
      BigNumber.from(String(obj.highestSaleLast24Hours)),
      BigNumber.from(String(obj.tradeVolume24Hours)),
    );
  };
}

export class CollectionActivity {
  readonly date: Date;
  readonly transferCount: BigNumber;
  readonly saleCount: BigNumber;
  readonly totalValue: BigNumber;
  readonly minimumValue: BigNumber;
  readonly maximumValue: BigNumber;
  readonly averageValue: BigNumber;

  public constructor(date: Date, transferCount: BigNumber, saleCount: BigNumber, totalValue: BigNumber, minimumValue: BigNumber, maximumValue: BigNumber, averageValue: BigNumber) {
    this.date = date;
    this.transferCount = transferCount;
    this.saleCount = saleCount;
    this.totalValue = totalValue;
    this.minimumValue = minimumValue;
    this.maximumValue = maximumValue;
    this.averageValue = averageValue;
  }

  public static fromObject = (obj: Record<string, unknown>): CollectionActivity => {
    return new CollectionActivity(
      dateFromString(obj.date as string),
      BigNumber.from(String(obj.transferCount)),
      BigNumber.from(String(obj.saleCount)),
      BigNumber.from(String(obj.totalValue)),
      BigNumber.from(String(obj.minimumValue)),
      BigNumber.from(String(obj.maximumValue)),
      BigNumber.from(String(obj.averageValue)),
    );
  };
}

export class TrendingCollection {
  readonly collection: Collection;
  readonly previousSaleCount: BigNumber;
  readonly previousTotalVolume: BigNumber;
  readonly totalVolume: BigNumber;
  readonly totalSaleCount: BigNumber;

  public constructor(collection: Collection, previousSaleCount: BigNumber, previousTotalVolume: BigNumber, totalVolume: BigNumber, totalSaleCount: BigNumber) {
    this.collection = collection;
    this.previousSaleCount = previousSaleCount;
    this.previousTotalVolume = previousTotalVolume;
    this.totalVolume = totalVolume;
    this.totalSaleCount = totalSaleCount;
  }

  public static fromObject = (obj: Record<string, unknown>): TrendingCollection => {
    return new TrendingCollection(
      Collection.fromObject(obj.collection as Record<string, unknown>),
      BigNumber.from(String(obj.previousSaleCount)),
      BigNumber.from(String(obj.previousTotalVolume)),
      BigNumber.from(String(obj.totalVolume)),
      BigNumber.from(String(obj.totalSaleCount)),
    );
  };
}


export class MintedTokenCount {
  readonly date: Date;
  readonly mintedTokenCount: BigNumber;
  readonly newRegistryCount: BigNumber;

  public constructor(date: Date, mintedTokenCount: BigNumber, newRegistryCount: BigNumber) {
    this.date = date;
    this.mintedTokenCount = mintedTokenCount;
    this.newRegistryCount = newRegistryCount;
  }

  public static fromObject = (obj: Record<string, unknown>): MintedTokenCount => {
    return new MintedTokenCount(
      dateFromString(obj.date as string),
      BigNumber.from(String(obj.mintedTokenCount)),
      BigNumber.from(String(obj.newRegistryCount)),
    );
  };
}


export class OwnedCollection extends ResponseData {
  public constructor(
    readonly collection: Collection,
    readonly tokens: CollectionToken[],
  ) { super(); }

  public static fromObject = (obj: Record<string, unknown>): OwnedCollection => {
    return new OwnedCollection(
      Collection.fromObject(obj.collection as Record<string, unknown>),
      (obj.tokens as Record<string, unknown>[]).map((innerObj: Record<string, unknown>): CollectionToken => CollectionToken.fromObject(innerObj)),
    );
  };
}
