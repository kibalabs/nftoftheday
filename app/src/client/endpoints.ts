import { dateToString, RequestData, ResponseData } from '@kibalabs/core';

import * as Resources from './resources';

export class RetrieveUiDataRequest extends RequestData {
  readonly startDate?: Date;
  readonly endDate?: Date;

  public constructor(startDate?: Date, endDate?: Date) {
    super();
    this.startDate = startDate;
    this.endDate = endDate;
  }

  public toObject = (): Record<string, unknown> => {
    return {
      startDate: this.startDate ? dateToString(this.startDate) : null,
      endDate: this.endDate ? dateToString(this.endDate) : null,
    };
  }
}

export class RetrieveUiDataResponse extends ResponseData {
  readonly uiData: Resources.UiData;

  public constructor(uiData: Resources.UiData) {
    super();
    this.uiData = uiData;
  }

  public static fromObject = (obj: Record<string, unknown>): RetrieveUiDataResponse => {
    return new RetrieveUiDataResponse(
      Resources.UiData.fromObject(obj.uiData as Record<string, unknown>),
    );
  }
}

export class RetrieveCollectionTokenRequest extends RequestData {
  // NOTE(krishan711): uncomment when ServiceClient implements params filled into the path
  // readonly registryAddress: string;
  // readonly tokenId: string;

  // public constructor(registryAddress?: string, tokenId?: string) {
  //   super();
  //   this.registryAddress = registryAddress;
  //   this.tokenId = tokenId;
  // }

  public toObject = (): Record<string, unknown> => {
    return {
      //     registryAddress: this.registryAddress,
      //     tokenId: this.tokenId,
    };
  }
}

export class RetrieveCollectionTokenResponse extends ResponseData {
  readonly token: Resources.CollectionToken;

  public constructor(token: Resources.CollectionToken) {
    super();
    this.token = token;
  }

  public static fromObject = (obj: Record<string, unknown>): RetrieveCollectionTokenResponse => {
    return new RetrieveCollectionTokenResponse(
      Resources.CollectionToken.fromObject(obj.token as Record<string, unknown>),
    );
  }
}

export class RetrieveCollectionRequest extends RequestData {
  // NOTE(krishan711): uncomment when ServiceClient implements params filled into the path
  // readonly registryAddress: string;
  // readonly tokenId: string;

  // public constructor(registryAddress?: string, tokenId?: string) {
  //   super();
  //   this.registryAddress = registryAddress;
  //   this.tokenId = tokenId;
  // }

  public toObject = (): Record<string, unknown> => {
    return {
      //     registryAddress: this.registryAddress,
      //     tokenId: this.tokenId,
    };
  }
}

export class RetrieveCollectionResponse extends ResponseData {
  readonly collection: Resources.Collection;

  public constructor(collection: Resources.Collection) {
    super();
    this.collection = collection;
  }

  public static fromObject = (obj: Record<string, unknown>): RetrieveCollectionResponse => {
    return new RetrieveCollectionResponse(
      Resources.Collection.fromObject(obj.collection as Record<string, unknown>),
    );
  }
}

export class GetCollectionStatisticsRequest extends RequestData {
  public toObject = (): Record<string, unknown> => {
    return {
    };
  }
}

export class GetCollectionStatisticsResponse extends ResponseData {
  readonly collectionStatistics: Resources.CollectionStatistics;

  public constructor(collectionStatistics: Resources.CollectionStatistics) {
    super();
    this.collectionStatistics = collectionStatistics;
  }

  public static fromObject = (obj: Record<string, unknown>): GetCollectionStatisticsResponse => {
    return new GetCollectionStatisticsResponse(
      Resources.CollectionStatistics.fromObject(obj.collectionStatistics as Record<string, unknown>),
    );
  }
}

export class GetTokenRecentSalesRequest extends RequestData {
  readonly offset?: number;

  constructor(offset?: number) {
    super();
    this.offset = offset || 0;
  }

  public toObject = (): Record<string, unknown> => {
    return {
      offset: this.offset,
    };
  }
}

export class GetTokenRecentSalesResponse extends ResponseData {
  readonly tokenTransfers: Resources.TokenTransfer[];

  public constructor(TokenRecentSales: Resources.TokenTransfer[]) {
    super();
    this.tokenTransfers = TokenRecentSales;
  }

  public static fromObject = (obj: Record<string, unknown>): GetTokenRecentSalesResponse => {
    return new GetTokenRecentSalesResponse(
      (obj.tokenTransfers as Record<string, unknown>[]).map((innerObj: Record<string, unknown>) => Resources.TokenTransfer.fromObject(innerObj)),
    );
  }
}

export class GetCollectionRecentSalesRequest extends RequestData {
  public toObject = (): Record<string, unknown> => {
    return {
    };
  }
}

export class GetCollectionRecentSalesResponse extends ResponseData {
  readonly tokenTransfers: Resources.TokenTransfer[];

  public constructor(collectionRecentSales: Resources.TokenTransfer[]) {
    super();
    this.tokenTransfers = collectionRecentSales;
  }

  public static fromObject = (obj: Record<string, unknown>): GetCollectionRecentSalesResponse => {
    return new GetCollectionRecentSalesResponse(
      (obj.tokenTransfers as Record<string, unknown>[]).map((innerObj: Record<string, unknown>) => Resources.TokenTransfer.fromObject(innerObj)),
    );
  }
}

export class GetCollectionHoldingsRequest extends RequestData {
  public toObject = (): Record<string, unknown> => {
    return {
    };
  }
}

export class GetCollectionHoldingsResponse extends ResponseData {
  readonly tokens: Resources.CollectionToken[];

  public constructor(collectionHoldings: Resources.CollectionToken[]) {
    super();
    this.tokens = collectionHoldings;
  }

  public static fromObject = (obj: Record<string, unknown>): GetCollectionHoldingsResponse => {
    return new GetCollectionHoldingsResponse(
      (obj.tokens as Record<string, unknown>[]).map((innerObj: Record<string, unknown>) => Resources.CollectionToken.fromObject(innerObj)),
    );
  }
}

export class SubscribeRequest extends RequestData {
  readonly email: string;

  public constructor(email: string) {
    super();
    this.email = email;
  }

  public toObject = (): Record<string, unknown> => {
    return {
      email: this.email,
    };
  }
}

export class SubscribeResponse extends ResponseData {
  public static fromObject = (): SubscribeResponse => {
    return new SubscribeResponse();
  }
}
