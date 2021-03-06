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

  public retrieveRegistryToken = async (registryAddress: string, tokenId: string): Promise<Resources.RegistryToken> => {
    const method = RestMethod.GET;
    const path = `v1/registries/${registryAddress}/tokens/${tokenId}`;
    const request = new Endpoints.RetrieveRegistryTokenRequest();
    const response = await this.makeRequest(method, path, request, Endpoints.RetrieveRegistryTokenResponse);
    return response.registryToken;
  }

  public subscribe = async (email: string): Promise<void> => {
    const method = RestMethod.POST;
    const path = 'v1/subscribe';
    const request = new Endpoints.SubscribeRequest(email);
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    const response = await this.makeRequest(method, path, request, Endpoints.SubscribeResponse);
  }
}
