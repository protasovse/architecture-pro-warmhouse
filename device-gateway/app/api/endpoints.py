import logging

from fastapi import APIRouter, HTTPException

from ..schemas import DeviceParameters
from ..services import SendParametersService

logger = logging.getLogger(__name__)
log = logger.info

router = APIRouter()


@router.post("/send-parameters/")
async def send_parameters(
    parameters: DeviceParameters | list[DeviceParameters],
):
    """Обработчик POST-запросов для отправки параметров в Kafka."""

    send_parameters_service = SendParametersService()

    try:
        await send_parameters_service(parameters)
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
