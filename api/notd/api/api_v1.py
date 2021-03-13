from fastapi import Request
from fastapi import Response

from notd.api.models_v1 import *
from notd.manager import NotdManager
from notd.core.kiba_router import KibaRouter
from notd.core.util import date_util

def create_api(notdManager: NotdManager) -> KibaRouter():
    router = KibaRouter()

    @router.post('/retrieve-ui-data', response_model=RetrieveUiDataResponse)
    async def retrieve_ui_data(request: RetrieveUiDataRequest, rawRequest: Request, response: Response, startDate: Optional[datetime.datetime] = None, endDate: Optional[datetime.datetime] = None):
        startDate = request.startDate.replace(tzinfo=None) if request.startDate else date_util.start_of_day(dt=datetime.datetime.now())
        endDate = request.endDate.replace(tzinfo=None) if request.endDate else date_util.start_of_day(dt=date_util.datetime_from_datetime(dt=startDate, days=1))
        uiData = await notdManager.retrieve_ui_data(startDate=startDate, endDate=endDate)
        return RetrieveUiDataResponse(uiData=ApiUiData.from_model(model=uiData))

    @router.post('/receive-new-blocks-deferred', response_model=ReceiveNewBlocksDeferredResponse)
    async def receive_new_blocks_deferred(rawRequest: Request, response: Response):  # request: ReceiveNewBlocksDeferredRequest
        await notdManager.receive_new_blocks_deferred()
        return ReceiveNewBlocksDeferredResponse()

    return router
