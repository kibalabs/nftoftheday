import { Requester, RestMethod, ServiceClient } from '@kibalabs/core';

import * as Endpoints from './endpoints';
import * as Resources from './resources';

export class NotdClient extends ServiceClient {
  public constructor(requester: Requester, baseUrl?: string) {
    super(requester, baseUrl || 'https://notd-api.kibalabs.com');
  }

  public retrieveHighestPriceTransfer = async (startDate?: Date, endDate?: Date): Promise<Resources.TokenTransfer> => {
    const method = RestMethod.POST;
    const path = 'v1/retrieve-highest-price-transfer';
    const request = new Endpoints.RetrieveHighestPriceTransferRequest(startDate, endDate);
    const response = await this.makeRequest(method, path, request, Endpoints.RetrieveHighestPriceTransferResponse);
    return response.transfer;
  };

  public retrieveMostTradedToken = async (startDate?: Date, endDate?: Date): Promise<Resources.TradedToken> => {
    const method = RestMethod.POST;
    const path = 'v1/retrieve-most-traded-token';
    const request = new Endpoints.RetrieveMostTradedTokenRequest(startDate, endDate);
    const response = await this.makeRequest(method, path, request, Endpoints.RetrieveMostTradedTokenResponse);
    return response.tradedToken;
  };

  public retrieveRandomTokenTransfer = async (startDate?: Date, endDate?: Date): Promise<Resources.TokenTransfer> => {
    const method = RestMethod.POST;
    const path = 'v1/retrieve-random-token-transfer';
    const request = new Endpoints.RetrieveRandomTokenTransferRequest(startDate, endDate);
    const response = await this.makeRequest(method, path, request, Endpoints.RetrieveRandomTokenTransferResponse);
    return response.transfer;
  };

  public retrieveSponsoredTokenTransfer = async (startDate?: Date, endDate?: Date): Promise<Resources.SponsoredToken> => {
    const method = RestMethod.POST;
    const path = 'v1/retrieve-sponsored-token';
    const request = new Endpoints.RetrieveSponsoredTokenRequest(startDate, endDate);
    const response = await this.makeRequest(method, path, request, Endpoints.RetrieveSponsoredTokenResponse);
    return response.sponsoredToken;
  };

  public retrieveTransferCount = async (startDate?: Date, endDate?: Date): Promise<number> => {
    const method = RestMethod.POST;
    const path = 'v1/retrieve-transfer-count';
    const request = new Endpoints.RetrieveTransferCountRequest(startDate, endDate);
    const response = await this.makeRequest(method, path, request, Endpoints.RetrieveTransferCountResponse);
    return response.count;
  };

  public getCollectionTokens = async (registryAddress: string): Promise<Resources.CollectionToken[]> => {
    const method = RestMethod.GET;
    const path = `v1/collections/${registryAddress}/tokens`;
    const request = new Endpoints.RetrieveCollectionTokensRequest();
    const response = await this.makeRequest(method, path, request, Endpoints.RetrieveCollectionTokensResponse);
    return response.tokens;
  };

  public getCollectionToken = async (registryAddress: string, tokenId: string): Promise<Resources.CollectionToken> => {
    const method = RestMethod.GET;
    const path = `v1/collections/${registryAddress}/tokens/${tokenId}`;
    const request = new Endpoints.RetrieveCollectionTokenRequest();
    const response = await this.makeRequest(method, path, request, Endpoints.RetrieveCollectionTokenResponse);
    return response.token;
  };

  public getCollection = async (registryAddress: string): Promise<Resources.Collection> => {
    const method = RestMethod.GET;
    const path = `v1/collections/${registryAddress}`;
    const request = new Endpoints.RetrieveCollectionRequest();
    const response = await this.makeRequest(method, path, request, Endpoints.RetrieveCollectionResponse);
    return response.collection;
  };

  public getCollectionRecentSales = async (address: string): Promise<Resources.TokenTransfer[]> => {
    const method = RestMethod.GET;
    const path = `v1/collections/${address}/recent-sales`;
    const request = new Endpoints.GetCollectionRecentSalesRequest();
    const response = await this.makeRequest(method, path, request, Endpoints.GetCollectionRecentSalesResponse);
    return response.tokenTransfers;
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
}
