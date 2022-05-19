import { dateFromString } from '@kibalabs/core';
import { BigNumber } from 'ethers';

export class TokenTransfer {
  readonly tokenTransferId: number;
  readonly transactionHash: string;
  readonly registryAddress: string;
  readonly fromAddress: string;
  readonly toAddress: string;
  readonly tokenId: string;
  readonly value: number;
  readonly gasLimit: number;
  readonly gasPrice: number;
  readonly gasUsed: number;
  readonly blockNumber: number;
  readonly blockHash: string;
  readonly blockDate: Date;
  readonly token: CollectionToken;
  readonly collection: Collection;

  public constructor(tokenTransferId: number, transactionHash: string, registryAddress: string, fromAddress: string, toAddress: string, tokenId: string, value: number, gasLimit: number, gasPrice: number, gasUsed: number, blockNumber: number, blockHash: string, blockDate: Date, token: CollectionToken, collection: Collection) {
    this.tokenTransferId = tokenTransferId;
    this.transactionHash = transactionHash;
    this.registryAddress = registryAddress;
    this.fromAddress = fromAddress;
    this.toAddress = toAddress;
    this.tokenId = tokenId;
    this.value = value;
    this.gasLimit = gasLimit;
    this.gasPrice = gasPrice;
    this.gasUsed = gasUsed;
    this.blockNumber = blockNumber;
    this.blockHash = blockHash;
    this.blockDate = blockDate;
    this.token = token;
    this.collection = collection;
  }

  public static fromObject = (obj: Record<string, unknown>): TokenTransfer => {
    return new TokenTransfer(
      Number(obj.tokenTransferId),
      String(obj.transactionHash),
      String(obj.registryAddress),
      String(obj.fromAddress),
      String(obj.toAddress),
      String(obj.tokenId),
      Number(obj.value),
      Number(obj.gasLimit),
      Number(obj.gasPrice),
      Number(obj.gasUsed),
      Number(obj.blockNumber),
      String(obj.blockHash),
      dateFromString(obj.blockDate as string),
      CollectionToken.fromObject(obj.token as Record<string, unknown>),
      Collection.fromObject(obj.collection as Record<string, unknown>),
    );
  };
}

export class TradedToken {
  readonly token: CollectionToken;
  readonly collection: Collection;
  readonly latestTransfer: TokenTransfer;
  readonly transferCount: number;

  public constructor(token: CollectionToken, collection: Collection, latestTransfer: TokenTransfer, transferCount: number) {
    this.token = token;
    this.collection = collection;
    this.latestTransfer = latestTransfer;
    this.transferCount = transferCount;
  }

  public static fromObject = (obj: Record<string, unknown>): TradedToken => {
    return new TradedToken(
      CollectionToken.fromObject(obj.token as Record<string, unknown>),
      Collection.fromObject(obj.collection as Record<string, unknown>),
      TokenTransfer.fromObject(obj.latestTransfer as Record<string, unknown>),
      Number(obj.transferCount),
    );
  };
}

export class SponsoredToken {
  readonly token: CollectionToken;
  readonly collection: Collection;
  readonly date: Date;
  readonly latestTransfer: TokenTransfer | null;

  public constructor(token: CollectionToken, collection: Collection, date: Date, latestTransfer: TokenTransfer | null) {
    this.token = token;
    this.collection = collection;
    this.date = date;
    this.latestTransfer = latestTransfer;
  }

  public static fromObject = (obj: Record<string, unknown>): SponsoredToken => {
    return new SponsoredToken(
      CollectionToken.fromObject(obj.token as Record<string, unknown>),
      Collection.fromObject(obj.collection as Record<string, unknown>),
      dateFromString(obj.date as string),
      obj.latestTransfer ? TokenTransfer.fromObject(obj.latestTransfer as Record<string, unknown>) : null,
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
  readonly imageUrl: string | null;
  readonly description: string | null;
  readonly attributes: TokenAttribute[];

  public constructor(registryAddress: string, tokenId: string, name: string, imageUrl: string | null, description: string | null, attributes: TokenAttribute[]) {
    this.registryAddress = registryAddress;
    this.tokenId = tokenId;
    this.name = name;
    this.imageUrl = imageUrl;
    this.description = description;
    this.attributes = attributes;
  }

  public static fromObject = (obj: Record<string, unknown>): CollectionToken => {
    return new CollectionToken(
      String(obj.registryAddress),
      String(obj.tokenId),
      String(obj.name),
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
  readonly lowestSaleLast24Hours: BigNumber | null;
  readonly highestSaleLast24Hours: BigNumber | null;
  readonly tradeVolume24Hours: BigNumber | null;

  public constructor(itemCount: number, holderCount: number, totalTradeVolume: BigNumber, lowestSaleLast24Hours: BigNumber | null, highestSaleLast24Hours: BigNumber | null, tradeVolume24Hours: BigNumber | null) {
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
      obj.lowestSaleLast24Hours ? BigNumber.from(String(obj.lowestSaleLast24Hours)) : null,
      obj.highestSaleLast24Hours ? BigNumber.from(String(obj.highestSaleLast24Hours)) : null,
      obj.tradeVolume24Hours ? BigNumber.from(String(obj.tradeVolume24Hours)) : null,
    );
  };
}

export class CollectionActivities {
  readonly date: string;
  readonly transferCount: BigNumber| null;
  readonly saleCount: BigNumber | null;
  readonly totalValue: BigNumber| null;
  readonly minimumValue: BigNumber | null;
  readonly maximumValue: BigNumber| null;
  readonly averageValue: BigNumber| null;

  public constructor(date: string, transferCount: BigNumber | null, saleCount: BigNumber | null, totalValue: BigNumber | null, minimumValue: BigNumber | null, maximumValue: BigNumber | null, averageValue: BigNumber | null) {
    this.date = date;
    this.transferCount = transferCount;
    this.saleCount = saleCount;
    this.totalValue = totalValue;
    this.minimumValue = minimumValue;
    this.maximumValue = maximumValue;
    this.averageValue = averageValue;
  }

  public static fromObject = (obj: Record<string, unknown>): CollectionActivities => {
    return new CollectionActivities(
      String(obj.date),
      obj.transferCount ? BigNumber.from(String(obj.transferCount)) : null,
      obj.saleCount ? BigNumber.from(String(obj.saleCount)) : null,
      obj.totalValue ? BigNumber.from(String(obj.totalValue)) : null,
      obj.minimumValue ? BigNumber.from(String(obj.minimumValue)) : null,
      obj.maximumValue ? BigNumber.from(String(obj.maximumValue)) : null,
      obj.averageValue ? BigNumber.from(String(obj.averageValue)) : null,
    );
  };
}
