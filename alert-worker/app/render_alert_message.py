import logging

from schemas import AlertExceededSchema, ResolveStatus, ResolveStatusLabel

logger = logging.getLogger(__name__)


def render_alert_message(
    exceeded_alert: AlertExceededSchema,
) -> str:
    logger.info(f"Обрабатываем сообщение из {exceeded_alert.model_dump()}")
    tpl = (
        exceeded_alert.subscription.template.message
        if exceeded_alert.resolve_status == ResolveStatus.EXCEEDED
        else exceeded_alert.subscription.template.resolve_message
    )
    return (
        f"{ResolveStatusLabel[exceeded_alert.resolve_status]}\n"
        f"{tpl.format(**exceeded_alert.model_dump())}"
    )
