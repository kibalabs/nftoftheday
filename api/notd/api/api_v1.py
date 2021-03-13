from fastapi import Request
from fastapi import Response

from notd.api.models_v1 import *
from notd.manager import NotdManager
from notd.core.kiba_router import KibaRouter
from notd.core.util import date_util

def create_api(notdManager: NotdManager) -> KibaRouter():
    router = KibaRouter()

    @router.post('/retrieve-ui-data', response_model=RetrieveUiDataResponse)
    async def retrieve_ui_data(rawRequest: Request, response: Response, startDate: Optional[datetime.datetime] = None, endDate: Optional[datetime.datetime] = None):  # request: RetrieveUiDataRequest
        startDate = startDate or date_util.start_of_day(dt=datetime.datetime.now())
        endDate = endDate or date_util.start_of_day(dt=date_util.datetime_from_datetime(dt=datetime.datetime.now(), days=1))
        uiData = await notdManager.retrieve_ui_data(startDate=startDate, endDate=endDate)
        return RetrieveUiDataResponse(uiData=ApiUiData.from_model(model=uiData))

    return router
