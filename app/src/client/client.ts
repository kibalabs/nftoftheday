import { Requester, RestMethod, ServiceClient } from '@kibalabs/core';

import * as Endpoints from './endpoints';
import * as Resources from './resources';

export class NotdClient extends ServiceClient {
  public constructor(requester: Requester, baseUrl?: string) {
    super(requester, baseUrl || 'https://notd-api.kibalabs.com');
  }

  public retrieveUiData = async (startDate?: Date, endDate?: Date): Promise<Resources.UiData> => {
    const method = RestMethod.POST;
    const path = 'v1/retrieve-ui-data';
    const request = new Endpoints.RetrieveUiDataRequest(startDate, endDate);
    const response = await this.makeRequest(method, path, request, Endpoints.RetrieveUiDataResponse);
    return response.uiData;
  }

  public retrieveCollectionToken = async (registryAddress: string, tokenId: string): Promise<Resources.CollectionToken> => {
    const method = RestMethod.GET;
    const path = `v1/collections/${registryAddress}/tokens/${tokenId}`;
    const request = new Endpoints.RetrieveCollectionTokenRequest();
    const response = await this.makeRequest(method, path, request, Endpoints.RetrieveCollectionTokenResponse);
    return response.token;
  }

  public retrieveCollection = async (registryAddress: string): Promise<Resources.Collection> => {
    const method = RestMethod.GET;
    const path = `v1/collections/${registryAddress}`;
    const request = new Endpoints.RetrieveCollectionRequest();
    const response = await this.makeRequest(method, path, request, Endpoints.RetrieveCollectionResponse);
    return response.collection;
  }

  public getCollectionRecentSales = async (address: string): Promise<Resources.TokenTransfer[]> => {
    const method = RestMethod.GET;
    const path = `v1/collections/${address}/recent-sales`;
    const request = new Endpoints.GetCollectionRecentSalesRequest();
    const response = await this.makeRequest(method, path, request, Endpoints.GetCollectionRecentSalesResponse);
    return response.tokenTransfers;
  }

  public getCollectionStatistics = async (address: string): Promise<Resources.CollectionStatistics> => {
    const method = RestMethod.GET;
    const path = `v1/collections/${address}/statistics`;
    const request = new Endpoints.GetCollectionStatisticsRequest();
    const response = await this.makeRequest(method, path, request, Endpoints.GetCollectionStatisticsResponse);
    return response.collectionStatistics;
  }

  public getCollectionRecentSales = async (address: string): Promise<Resources.TokenTransfer[]> => {
    const method = RestMethod.GET;
    const path = `v1/collections/${address}/recent-sales`;
    const request = new Endpoints.GetTokenRecentSalesRequest();
    const response = await this.makeRequest(method, path, request, Endpoints.GetTokenRecentSalesResponse);
    return response.tokenTransfers;
  }

  public subscribe = async (email: string): Promise<void> => {
    const method = RestMethod.POST;
    const path = 'v1/subscribe';
    const request = new Endpoints.SubscribeRequest(email);
    await this.makeRequest(method, path, request, Endpoints.SubscribeResponse);
  }
}
