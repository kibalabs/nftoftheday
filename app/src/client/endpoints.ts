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


export class RetrieveRegistryTokenRequest extends RequestData {
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

export class RetrieveRegistryTokenResponse extends ResponseData {
  readonly registryToken: Resources.RegistryToken;

  public constructor(registryToken: Resources.RegistryToken) {
    super();
    this.registryToken = registryToken;
  }

  public static fromObject = (obj: Record<string, unknown>): RetrieveRegistryTokenResponse => {
    return new RetrieveRegistryTokenResponse(
      Resources.RegistryToken.fromObject(obj.registryToken as Record<string, unknown>),
    );
  }
}
