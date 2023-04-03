import { RequestData, ResponseData } from '@kibalabs/core';

import * as Resources from './resources';

export class ListCollectionTokensRequest extends RequestData {
}

export class ListCollectionTokensResponse extends ResponseData {
  readonly tokens: Resources.CollectionToken[];

  public constructor(tokens: Resources.CollectionToken[]) {
    super();
    this.tokens = tokens;
  }

  public static fromObject = (obj: Record<string, unknown>): ListCollectionTokensResponse => {
    return new ListCollectionTokensResponse(
      (obj.tokens as Record<string, unknown>[]).map((innerObj: Record<string, unknown>) => Resources.CollectionToken.fromObject(innerObj)),
    );
  };
}

export class GetCollectionTokenRequest extends RequestData {
}

export class GetCollectionTokenResponse extends ResponseData {
  readonly token: Resources.CollectionToken;

  public constructor(token: Resources.CollectionToken) {
    super();
    this.token = token;
  }

  public static fromObject = (obj: Record<string, unknown>): GetCollectionTokenResponse => {
    return new GetCollectionTokenResponse(
      Resources.CollectionToken.fromObject(obj.token as Record<string, unknown>),
    );
  };
}

export class GetCollectionRequest extends RequestData {
}

export class GetCollectionResponse extends ResponseData {
  readonly collection: Resources.Collection;

  public constructor(collection: Resources.Collection) {
    super();
    this.collection = collection;
  }

  public static fromObject = (obj: Record<string, unknown>): GetCollectionResponse => {
    return new GetCollectionResponse(
      Resources.Collection.fromObject(obj.collection as Record<string, unknown>),
    );
  };
}

export class GetCollectionStatisticsRequest extends RequestData {
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
  };
}

export class GetTokenRecentSalesRequest extends RequestData {
  readonly limit?: number;
  readonly offset?: number;

  constructor(limit?: number, offset?: number) {
    super();
    this.limit = limit;
    this.offset = offset;
  }

  public toObject = (): Record<string, unknown> => {
    return {
      limit: this.limit,
      offset: this.offset,
    };
  };
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
  };
}

export class GetTokenRecentTransfersRequest extends RequestData {
  readonly limit?: number;
  readonly offset?: number;

  constructor(limit?: number, offset?: number) {
    super();
    this.limit = limit;
    this.offset = offset;
  }

  public toObject = (): Record<string, unknown> => {
    return {
      limit: this.limit,
      offset: this.offset,
    };
  };
}

export class GetTokenRecentTransfersResponse extends ResponseData {
  readonly tokenTransfers: Resources.TokenTransfer[];

  public constructor(TokenRecentTransfers: Resources.TokenTransfer[]) {
    super();
    this.tokenTransfers = TokenRecentTransfers;
  }

  public static fromObject = (obj: Record<string, unknown>): GetTokenRecentTransfersResponse => {
    return new GetTokenRecentTransfersResponse(
      (obj.tokenTransfers as Record<string, unknown>[]).map((innerObj: Record<string, unknown>) => Resources.TokenTransfer.fromObject(innerObj)),
    );
  };
}

export class GetCollectionRecentSalesRequest extends RequestData {
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
  };
}

export class GetCollectionHoldingsRequest extends RequestData {
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
  };
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
  };
}

export class SubscribeResponse extends ResponseData {
  public static fromObject = (): SubscribeResponse => {
    return new SubscribeResponse();
  };
}

export class UpdateCollectionRequest extends RequestData {
  readonly userAddress: string;

  constructor(userAddress: string) {
    super();
    this.userAddress = userAddress;
  }

  public toObject = (): Record<string, unknown> => {
    return {
      userAddress: this.userAddress,
    };
  };
}

export class UpdateCollectionResponse extends ResponseData {
  public static fromObject = (): UpdateCollectionResponse => {
    return new UpdateCollectionResponse();
  };
}

export class UpdateTokenRequest extends RequestData {
  readonly userAddress: string;

  constructor(userAddress: string) {
    super();
    this.userAddress = userAddress;
  }

  public toObject = (): Record<string, unknown> => {
    return {
      userAddress: this.userAddress,
    };
  };
}

export class UpdateTokenResponse extends ResponseData {
  public static fromObject = (): UpdateTokenResponse => {
    return new UpdateTokenResponse();
  };
}

export class UpdateCollectionTokenRequest extends RequestData {
  readonly userAddress: string;

  constructor(userAddress: string) {
    super();
    this.userAddress = userAddress;
  }

  public toObject = (): Record<string, unknown> => {
    return {
      userAddress: this.userAddress,
    };
  };
}

export class UpdateCollectionTokenResponse extends ResponseData {
  public static fromObject = (): UpdateCollectionTokenResponse => {
    return new UpdateCollectionTokenResponse();
  };
}

export class GetOwnerTokensRequest extends RequestData {
}

export class GetOwnerTokensResponse extends ResponseData {
  readonly tokens: Resources.CollectionToken[];

  public constructor(token: Resources.CollectionToken[]) {
    super();
    this.tokens = token;
  }

  public static fromObject = (obj: Record<string, unknown>): GetOwnerTokensResponse => {
    return new GetOwnerTokensResponse(
      (obj.tokens as Record<string, unknown>[]).map((innerObj: Record<string, unknown>) => Resources.CollectionToken.fromObject(innerObj)),
    );
  };
}

export class GetCollectionActivitiesRequest extends RequestData {
}

export class GetCollectionActivitiesResponse extends ResponseData {
  readonly collectionActivities: Resources.CollectionActivity[];

  public constructor(collectionActivities: Resources.CollectionActivity[]) {
    super();
    this.collectionActivities = collectionActivities;
  }

  public static fromObject = (obj: Record<string, unknown>): GetCollectionActivitiesResponse => {
    return new GetCollectionActivitiesResponse(
      (obj.collectionActivities as Record<string, unknown>[]).map((innerObj: Record<string, unknown>) => Resources.CollectionActivity.fromObject(innerObj)),
    );
  };
}


export class ListTrendingCollectionsRequest extends RequestData {
  readonly duration?: string;
  readonly limit?: number;
  readonly order?: string;

  constructor(duration?: string, limit?: number, order?: string) {
    super();
    this.duration = duration;
    this.limit = limit;
    this.order = order;
  }

  public toObject = (): Record<string, unknown> => {
    return {
      duration: this.duration,
      limit: this.limit,
      order: this.order,
    };
  };
}

export class ListTrendingCollectionsResponse extends ResponseData {
  readonly trendingCollections: Resources.TrendingCollection[];

  public constructor(trendingCollections: Resources.TrendingCollection[]) {
    super();
    this.trendingCollections = trendingCollections;
  }

  public static fromObject = (obj: Record<string, unknown>): ListTrendingCollectionsResponse => {
    return new ListTrendingCollectionsResponse(
      (obj.trendingCollections as Record<string, unknown>[]).map((innerObj: Record<string, unknown>) => Resources.TrendingCollection.fromObject(innerObj)),
    );
  };
}
