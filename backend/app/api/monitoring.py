from fastapi import APIRouter, Depends

from app.services.auth_service import get_authenticated_user
from app.services.monitoring_service import monitoring_service


router = APIRouter(
    prefix="/api/monitoring",
    tags=["Monitoring"],
)


@router.get("/live")
def get_live_monitoring(
    authenticated_user: str = Depends(get_authenticated_user),
):
    """
    Return live monitoring metrics for the authenticated user.
    """
    return monitoring_service.snapshot()