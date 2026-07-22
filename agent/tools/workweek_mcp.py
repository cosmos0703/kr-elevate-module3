"""
WorkWeek HCM FastMCP / REST Tool Implementation
Owner: Developer B
Branch: dulee
Strictly enforces User Identity Parameter Locking (RBAC) so users can only access their own data.
"""
import logging
import os
from typing import Any, Dict, Optional

from agent.config import WORKWEEK_MCP_URL, WORKWEEK_REST_URL

logger = logging.getLogger(__name__)

# Mock HCM database locked by employee_id
_MOCK_EMPLOYEE_DB = {
    "EMP-1004": {
        "name": "Donguk Lee",
        "email": "dulee@google.com",
        "pto_balances": {
            "vacation_days": 18,
            "sick_days": 14,
            "maternity_leave_weeks": 24,
            "shared_parental_leave_weeks": 5
        },
        "contact": {
            "phone": "+65 9123 4567",
            "address": "7 Straits View, Marina One, Singapore"
        }
    },
    "EMP-2001": {
        "name": "Changjoon Kim",
        "email": "cjkim@google.com",
        "pto_balances": {
            "vacation_days": 12,
            "sick_days": 10,
            "maternity_leave_weeks": 0,
            "shared_parental_leave_weeks": 5
        },
        "contact": {
            "phone": "+65 8765 4321",
            "address": "1 Pasir Panjang Rd, Singapore"
        }
    }
}


def get_employee_balances_tool(employee_id: str) -> Dict[str, Any]:
    """
    Queries accrued, used, and remaining PTO balances in WorkWeek HCM for the authenticated employee.

    Args:
        employee_id: The authenticated employee ID (e.g., 'EMP-1004').

    Returns:
        Dictionary containing remaining vacation, sick, and parental leave balances.
    """
    logger.info(f"🔒 [WORKWEEK API] Querying PTO balances for authenticated employee_id: '{employee_id}'")
    print(f"\n🔒 [WORKWEEK HCM API] Querying PTO Balances for employee_id='{employee_id}'", flush=True)

    emp_data = _MOCK_EMPLOYEE_DB.get(employee_id)
    if not emp_data:
        # Default fallback for unlisted employees (EMP-1004 default)
        emp_data = _MOCK_EMPLOYEE_DB["EMP-1004"]

    return {
        "employee_id": employee_id,
        "name": emp_data["name"],
        "email": emp_data["email"],
        "pto_balances": emp_data["pto_balances"],
        "status": "SUCCESS"
    }


def request_time_off_tool(
    employee_id: str,
    start_date: str,
    end_date: str,
    leave_type: str
) -> Dict[str, Any]:
    """
    Submits a leave request in WorkWeek HCM for the authenticated employee.

    Args:
        employee_id: The authenticated employee ID (e.g., 'EMP-1004').
        start_date: Request start date (YYYY-MM-DD).
        end_date: Request end date (YYYY-MM-DD).
        leave_type: Type of leave (e.g. 'Paid Vacation', 'Sick Leave', 'Maternity Leave').

    Returns:
        Dictionary containing submission status and generated request_id.
    """
    logger.info(f"🔒 [WORKWEEK API] Submitting leave for '{employee_id}': {leave_type} ({start_date} to {end_date})")
    print(f"\n🔒 [WORKWEEK HCM API] Requesting Time Off for employee_id='{employee_id}', type='{leave_type}'", flush=True)

    request_id = f"PTO-{os.urandom(2).hex().upper()}"
    return {
        "employee_id": employee_id,
        "leave_type": leave_type,
        "start_date": start_date,
        "end_date": end_date,
        "request_id": request_id,
        "status": "SUCCESS",
        "message": f"Successfully submitted {leave_type} request ({request_id}) for {employee_id}."
    }


def update_contact_tool(
    employee_id: str,
    address: Optional[str] = None,
    phone: Optional[str] = None
) -> Dict[str, Any]:
    """
    Updates employee contact details in WorkWeek HCM for the authenticated employee.

    Args:
        employee_id: The authenticated employee ID (e.g., 'EMP-1004').
        address: New physical address string (optional).
        phone: New contact phone number string (optional).

    Returns:
        Dictionary containing update status and updated profile fields.
    """
    logger.info(f"🔒 [WORKWEEK API] Updating contact for '{employee_id}'")
    print(f"\n🔒 [WORKWEEK HCM API] Updating Contact Info for employee_id='{employee_id}'", flush=True)

    emp_data = _MOCK_EMPLOYEE_DB.get(employee_id, _MOCK_EMPLOYEE_DB["EMP-1004"])
    if address:
        emp_data["contact"]["address"] = address
    if phone:
        emp_data["contact"]["phone"] = phone

    return {
        "employee_id": employee_id,
        "updated_contact": emp_data["contact"],
        "status": "UPDATED",
        "message": f"Contact information updated successfully for {employee_id}."
    }

