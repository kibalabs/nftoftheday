import { dateToString, RequestData, ResponseData } from '@kibalabs/core';

import * as Resources from './resources';

export class RetrieveUiDataRequest extends RequestData {
  readonly startDate: Date;
  readonly endDate: Date;

  public constructor(startDate: Date, endDate: Date) {
    super();
    this.startDate = startDate;
    this.endDate = endDate;
  }

  public toObject = (): Record<string, unknown> => {
    return {
      startDate: dateToString(this.startDate),
      endDate: dateToString(this.endDate),
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
