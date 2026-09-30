from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.auth import current_user
from app.core.supabase import supabase


router = APIRouter(tags=["history"])
security = HTTPBearer()


def authenticated_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    return current_user(f"Bearer {credentials.credentials}")


@router.get("/history")
def get_history(
    limit: int = Query(default=20, ge=1, le=100),
    user=Depends(authenticated_user),
):
    try:
        user_id = user["id"]

        # Get the total number of analyses belonging
        # to the currently authenticated user.
        count_result = (
            supabase
            .table("analysis_history")
            .select("id")
            .eq("user_id", user_id)
            .execute()
        )

        total_count = len(count_result.data or [])

        # Load only the requested number of recent records
        # for displaying the history page.
        result = (
            supabase
            .table("analysis_history")
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )

        return {
            "success": True,
            "count": total_count,
            "history": result.data or [],
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load analysis history: {str(e)}",
        )


@router.delete("/history")
def delete_history(
    user=Depends(authenticated_user),
):
    try:
        user_id = user["id"]

        # Count the user's records before deleting them.
        count_result = (
            supabase
            .table("analysis_history")
            .select("id")
            .eq("user_id", user_id)
            .execute()
        )

        deleted_count = len(count_result.data or [])

        # Delete only this user's analysis history.
        (
            supabase
            .table("analysis_history")
            .delete()
            .eq("user_id", user_id)
            .execute()
        )

        return {
            "success": True,
            "message": "Analysis history deleted successfully.",
            "deleted_count": deleted_count,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete analysis history: {str(e)}",
        )
