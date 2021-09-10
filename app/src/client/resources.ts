import { dateFromString } from '@kibalabs/core';

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

  public constructor(tokenTransferId: number, transactionHash: string, registryAddress: string, fromAddress: string, toAddress: string, tokenId: string, value: number, gasLimit: number, gasPrice: number, gasUsed: number, blockNumber: number, blockHash: string, blockDate: Date) {
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
    );
  }
}

export class Token {
  readonly registryAddress: string;
  readonly tokenId: string;

  public constructor(registryAddress: string, tokenId: string) {
    this.registryAddress = registryAddress;
    this.tokenId = tokenId;
  }

  public static fromObject = (obj: Record<string, unknown>): Token => {
    return new Token(
      String(obj.registryAddress),
      String(obj.tokenId),
    );
  }
}

export class UiData {
  readonly highestPricedTokenTransfer: TokenTransfer;
  readonly mostTradedTokenTransfers: TokenTransfer[];
  readonly randomTokenTransfer: TokenTransfer;
  readonly sponsoredToken: Token;
  readonly transactionCount: number;

  public constructor(highestPricedTokenTransfer: TokenTransfer, mostTradedTokenTransfers: TokenTransfer[], randomTokenTransfer: TokenTransfer, sponsoredToken: Token, transactionCount: number) {
    this.highestPricedTokenTransfer = highestPricedTokenTransfer;
    this.mostTradedTokenTransfers = mostTradedTokenTransfers;
    this.randomTokenTransfer = randomTokenTransfer;
    this.sponsoredToken = sponsoredToken;
    this.transactionCount = transactionCount;
  }

  public static fromObject = (obj: Record<string, unknown>): UiData => {
    return new UiData(
      TokenTransfer.fromObject(obj.highestPricedTokenTransfer as Record<string, unknown>),
      (obj.mostTradedTokenTransfers as Record<string, unknown>[]).map((innerObj: Record<string, unknown>) => TokenTransfer.fromObject(innerObj)),
      TokenTransfer.fromObject(obj.randomTokenTransfer as Record<string, unknown>),
      Token.fromObject(obj.sponsoredToken as Record<string, unknown>),
      Number(obj.transactionCount as Record<string, unknown>),
    );
  }
}

export class RegistryToken {
  readonly name: string;
  readonly imageUrl: string | null;
  readonly openSeaUrl: string | null;
  readonly externalUrl: string | null;
  readonly lastSaleDate: Date | null;
  readonly lastSalePrice: number | null;
  readonly collectionName: string;
  readonly collectionImageUrl: string | null;
  readonly collectionOpenSeaUrl: string | null;
  readonly collectionExternalUrl: string | null;
  readonly registryAddress: string;
  readonly tokenId: string;

  public constructor(name: string, imageUrl: string | null, openSeaUrl: string | null, externalUrl: string | null, lastSaleDate: Date | null, lastSalePrice: number | null, collectionName: string, collectionImageUrl: string | null, collectionOpenSeaUrl: string | null, collectionExternalUrl: string | null, registryAddress: string, tokenId: string) {
    this.name = name;
    this.imageUrl = imageUrl;
    this.openSeaUrl = openSeaUrl;
    this.externalUrl = externalUrl;
    this.lastSaleDate = lastSaleDate;
    this.lastSalePrice = lastSalePrice;
    this.collectionName = collectionName;
    this.collectionImageUrl = collectionImageUrl;
    this.collectionOpenSeaUrl = collectionOpenSeaUrl;
    this.collectionExternalUrl = collectionExternalUrl;
    this.registryAddress = registryAddress;
    this.tokenId = tokenId;
  }

  public static fromObject = (obj: Record<string, unknown>): RegistryToken => {
    return new RegistryToken(
      String(obj.name),
      obj.imageUrl ? String(obj.imageUrl) : null,
      obj.openSeaUrl ? String(obj.openSeaUrl) : null,
      obj.externalUrl ? String(obj.externalUrl) : null,
      obj.lastSaleDate ? dateFromString(obj.lastSaleDate as string) : null,
      obj.lastSalePrice ? Number(obj.lastSalePrice) : null,
      String(obj.collectionName),
      obj.collectionImageUrl ? String(obj.collectionImageUrl) : null,
      obj.collectionOpenSeaUrl ? String(obj.collectionOpenSeaUrl) : null,
      obj.collectionExternalUrl ? String(obj.collectionExternalUrl) : null,
      String(obj.registryAddress),
      String(obj.tokenId),
    );
  }
}
