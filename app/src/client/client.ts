import { Requester, RestMethod, ServiceClient } from '@kibalabs/core';

import * as Endpoints from './endpoints';
import * as Resources from './resources';

export class NotdClient extends ServiceClient {
  public constructor(requester: Requester, baseUrl?: string) {
    super(requester, baseUrl || 'https://api.tokenhunt.io');
  }

  public listCollectionTokens = async (registryAddress: string): Promise<Resources.CollectionToken[]> => {
    const method = RestMethod.GET;
    const path = `v1/collections/${registryAddress}/tokens`;
    const request = new Endpoints.ListCollectionTokensRequest();
    const response = await this.makeRequest(method, path, request, Endpoints.ListCollectionTokensResponse);
    return response.tokens;
  };

  public getCollectionToken = async (registryAddress: string, tokenId: string): Promise<Resources.CollectionToken> => {
    const method = RestMethod.GET;
    const path = `v1/collections/${registryAddress}/tokens/${tokenId}`;
    const request = new Endpoints.GetCollectionTokenRequest();
    const response = await this.makeRequest(method, path, request, Endpoints.GetCollectionTokenResponse);
    return response.token;
  };

  public getCollection = async (registryAddress: string): Promise<Resources.Collection> => {
    const method = RestMethod.GET;
    const path = `v1/collections/${registryAddress}`;
    const request = new Endpoints.GetCollectionRequest();
    const response = await this.makeRequest(method, path, request, Endpoints.GetCollectionResponse);
    return response.collection;
  };

  public listCollectionRecentSales = async (address: string): Promise<Resources.TokenTransfer[]> => {
    const method = RestMethod.GET;
    const path = `v1/collections/${address}/recent-sales`;
    const request = new Endpoints.GetCollectionRecentSalesRequest();
    const response = await this.makeRequest(method, path, request, Endpoints.GetCollectionRecentSalesResponse);
    return response.tokenTransfers;
  };

  public listCollectionTransferValues = async (address: string, minDate?: Date, maxDate?: Date, minValue?: bigint): Promise<Resources.TokenTransferValue[]> => {
    const method = RestMethod.GET;
    const path = `v1/collections/${address}/token-transfer-values`;
    const request = new Endpoints.ListCollectionTransferValuesRequest(minDate, maxDate, minValue);
    const response = await this.makeRequest(method, path, request, Endpoints.ListCollectionTransferValuesResponse);
    return response.tokenTransferValues;
  };

  public getCollectionHoldings = async (address: string, ownerAddress: string): Promise<Resources.CollectionToken[]> => {
    const method = RestMethod.GET;
    const path = `v1/collections/${address}/tokens/owner/${ownerAddress}`;
    const request = new Endpoints.GetCollectionHoldingsRequest();
    const response = await this.makeRequest(method, path, request, Endpoints.GetCollectionHoldingsResponse);
    return response.tokens;
  };

  public getCollectionStatistics = async (address: string): Promise<Resources.CollectionStatistics> => {
    const method = RestMethod.GET;
    const path = `v1/collections/${address}/statistics`;
    const request = new Endpoints.GetCollectionStatisticsRequest();
    const response = await this.makeRequest(method, path, request, Endpoints.GetCollectionStatisticsResponse);
    return response.collectionStatistics;
  };

  public getTokenRecentSales = async (registryAddress: string, tokenId: string, limit?: number, offset?: number): Promise<Resources.TokenTransfer[]> => {
    const method = RestMethod.GET;
    const path = `v1/collections/${registryAddress}/tokens/${tokenId}/recent-sales`;
    const request = new Endpoints.GetTokenRecentSalesRequest(limit, offset);
    const response = await this.makeRequest(method, path, request, Endpoints.GetTokenRecentSalesResponse);
    return response.tokenTransfers;
  };

  public getTokenRecentTransfers = async (registryAddress: string, tokenId: string, limit?: number, offset?: number): Promise<Resources.TokenTransfer[]> => {
    const method = RestMethod.GET;
    const path = `v1/collections/${registryAddress}/tokens/${tokenId}/recent-transfers`;
    const request = new Endpoints.GetTokenRecentTransfersRequest(limit, offset);
    const response = await this.makeRequest(method, path, request, Endpoints.GetTokenRecentTransfersResponse);
    return response.tokenTransfers;
  };

  public subscribe = async (email: string): Promise<void> => {
    const method = RestMethod.POST;
    const path = 'v1/subscribe';
    const request = new Endpoints.SubscribeRequest(email);
    await this.makeRequest(method, path, request, Endpoints.SubscribeResponse);
  };

  public updateCollection = async (address: string, userAddress: string): Promise<void> => {
    const method = RestMethod.POST;
    const path = `v1/collections/${address}/update`;
    const request = new Endpoints.UpdateCollectionRequest(userAddress);
    await this.makeRequest(method, path, request, Endpoints.UpdateCollectionResponse);
  };

  public updateToken = async (registryAddress: string, tokenId: string, userAddress: string): Promise<void> => {
    const method = RestMethod.POST;
    const path = `v1/collections/${registryAddress}/tokens/${tokenId}/update`;
    const request = new Endpoints.UpdateTokenRequest(userAddress);
    await this.makeRequest(method, path, request, Endpoints.UpdateTokenResponse);
  };

  public updateCollectionTokens = async (registryAddress: string, userAddress: string): Promise<void> => {
    const method = RestMethod.POST;
    const path = `v1/collections/${registryAddress}/update-tokens`;
    const request = new Endpoints.UpdateCollectionTokenRequest(userAddress);
    await this.makeRequest(method, path, request, Endpoints.UpdateCollectionTokenResponse);
  };

  public getOwnerTokens = async (accountAddress: string): Promise<Resources.CollectionToken[]> => {
    const method = RestMethod.GET;
    const path = `v1/accounts/${accountAddress}/tokens`;
    const request = new Endpoints.GetOwnerTokensRequest();
    const response = await this.makeRequest(method, path, request, Endpoints.GetOwnerTokensResponse);
    return response.tokens;
  };

  public getCollectionDailyActivities = async (address: string): Promise<Resources.CollectionActivity[]> => {
    const method = RestMethod.GET;
    const path = `v1/collections/${address}/daily-activities`;
    const request = new Endpoints.GetCollectionActivitiesRequest();
    const response = await this.makeRequest(method, path, request, Endpoints.GetCollectionActivitiesResponse);
    return response.collectionActivities;
  };

  public retrieveTrendingCollections = async (duration?: string, limit?: number, order?: string): Promise<Resources.TrendingCollection[]> => {
    const method = RestMethod.GET;
    const path = 'v1/collections/trending';
    const request = new Endpoints.RetrieveTrendingCollectionsRequest(duration, limit, order);
    const response = await this.makeRequest(method, path, request, Endpoints.RetrieveTrendingCollectionsResponse);
    return response.trendingCollections;
  };

  public retrieveMintedTokenCounts = async (duration?: string): Promise<Resources.MintedTokenCount[]> => {
    const method = RestMethod.GET;
    const path = 'v1/minted-token-counts';
    const request = new Endpoints.RetrieveMintedTokenCountsRequest(duration);
    const response = await this.makeRequest(method, path, request, Endpoints.RetrieveMintedTokenCountsResponse);
    return response.mintedTokenCounts;
  };

  public retrieveHeroTokens = async (): Promise<Resources.CollectionToken[]> => {
    const method = RestMethod.GET;
    const path = 'v1/hero-tokens';
    const request = new Endpoints.RetrieveHeroTokensRequest();
    const response = await this.makeRequest(method, path, request, Endpoints.RetrieveHeroTokensResponse);
    return response.tokens;
  };

  public listUserOwnedCollections = async (userAddress: string): Promise<Resources.OwnedCollection[]> => {
    const method = RestMethod.GET;
    const path = `v1/accounts/${userAddress}/owned-collections`;
    const request = new Endpoints.ListUserOwnedCollectionsRequest();
    const response = await this.makeRequest(method, path, request, Endpoints.ListUserOwnedCollectionsResponse);
    return response.ownedCollections;
  };

  public listUserRecentTransfers = async (address: string, limit?: number, offset?: number): Promise<Resources.TokenTransfer[]> => {
    const method = RestMethod.GET;
    const path = `v1/accounts/${address}/recent-transfers`;
    const request = new Endpoints.ListUserRecentTransfersRequest(limit, offset);
    const response = await this.makeRequest(method, path, request, Endpoints.ListUserRecentTransfersResponse);
    return response.tokenTransfers;
  };

  public listUserTradingHistories = async (address: string, offset?: number): Promise<Resources.TradingHistory[]> => {
    const method = RestMethod.GET;
    const path = `v1/accounts/${address}/trading-histories`;
    const request = new Endpoints.ListUserTradingHistoriesRequest(offset);
    const response = await this.makeRequest(method, path, request, Endpoints.ListUserTradingHistoriesResponse);
    return response.tradingHistories;
  };

  public listUserBlueChipCollectionToken = async (address: string): Promise<Resources.CollectionToken[]> => {
    const method = RestMethod.GET;
    const path = `v1/accounts/${address}/tokens/blue-chip-collections`;
    const request = new Endpoints.ListUserBlueChipCollectionsTokenRequest();
    const response = await this.makeRequest(method, path, request, Endpoints.ListUserBlueChipCollectionTokensResponse);
    return response.tokens;
  };
}
