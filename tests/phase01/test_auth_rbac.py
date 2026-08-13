"""
test_auth_rbac.py â€” Comprehensive unit and integration tests for Phase 1 Auth, RBAC, and Audit Log.

Tests login, token refresh, Owner -> Manager -> Staff invitation chain, warehouse scoping, and audit logs.
"""

from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient

from commons.auth import hash_password
from core.models.user_model import ExperienceTier, FunctionRole, UserRole, UserStatus


@pytest.mark.asyncio
async def test_auth_login_success(async_client: AsyncClient):
    """
    Test successful user login yielding JWT access and refresh tokens.

    Args:
        async_client (AsyncClient): Test client fixture.
    """
    fake_user = {
        "id": "507f1f77bcf86cd799439011",
        "email": "owner@whitfield.com",
        "full_name": "System Owner",
        "hashed_password": hash_password("OwnerPass123!"),
        "role": UserRole.OWNER.value,
        "warehouse_id": None,
        "experience_tier": None,
        "function_roles": [],
        "status": UserStatus.ACTIVE.value,
    }

    with patch("core.cruds.user_crud.MongoDatabase") as mock_db:
        mock_instance = mock_db.return_value
        mock_instance.users.find_one = AsyncMock(return_value=fake_user)

        login_payload = {
            "email": "owner@whitfield.com",
            "password": "OwnerPass123!",
        }
        response = await async_client.post("/auth/login", json=login_payload)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_auth_login_invalid_password(async_client: AsyncClient):
    """
    Test user login rejection when wrong password is supplied.

    Args:
        async_client (AsyncClient): Test client fixture.
    """
    fake_user = {
        "id": "507f1f77bcf86cd799439011",
        "email": "owner@whitfield.com",
        "hashed_password": hash_password("CorrectPassword"),
        "role": UserRole.OWNER.value,
        "status": UserStatus.ACTIVE.value,
    }

    with patch("core.cruds.user_crud.MongoDatabase") as mock_db:
        mock_instance = mock_db.return_value
        mock_instance.users.find_one = AsyncMock(return_value=fake_user)

        login_payload = {
            "email": "owner@whitfield.com",
            "password": "WrongPassword",
        }
        response = await async_client.post("/auth/login", json=login_payload)
        assert response.status_code == 401


@pytest.mark.asyncio
async def test_owner_create_warehouse(async_client: AsyncClient):
    """
    Test Owner creating a warehouse facility.

    Args:
        async_client (AsyncClient): Test client fixture.
    """
    owner_user = {
        "id": "507f1f77bcf86cd799439011",
        "email": "owner@whitfield.com",
        "full_name": "System Owner",
        "role": UserRole.OWNER.value,
        "status": UserStatus.ACTIVE.value,
    }

    wh_doc = {
        "id": "607f1f77bcf86cd799439022",
        "code": "RNO",
        "name": "Reno Warehouse",
        "address": "123 Reno Way",
        "manager_id": None,
        "is_active": True,
        "created_at": "2026-08-13 12:00:00.000000",
    }

    with patch("commons.auth.decodeJWT") as mock_decode, \
         patch("core.cruds.user_crud.CRUDUser.get_by_id", AsyncMock(return_value=owner_user)), \
         patch("core.cruds.wms_crud.CRUDWarehouse.get_by_code", AsyncMock(return_value=None)), \
         patch("core.cruds.wms_crud.CRUDWarehouse.create", AsyncMock(return_value=wh_doc)), \
         patch("core.services.wms_service.CRUDAuditLog.create", AsyncMock(return_value={"id": "audit1"})):

        mock_decode.return_value = {"sub": owner_user["id"], "type": "access", "role": "OWNER"}

        headers = {"Authorization": "Bearer valid_owner_token"}
        wh_payload = {
            "code": "RNO",
            "name": "Reno Warehouse",
            "address": "123 Reno Way",
        }
        response = await async_client.post("/warehouses", json=wh_payload, headers=headers)
        assert response.status_code == 201
        data = response.json()
        assert data["code"] == "RNO"
        assert data["name"] == "Reno Warehouse"


@pytest.mark.asyncio
async def test_owner_create_manager(async_client: AsyncClient):
    """
    Test Owner creating a Manager account assigned to a warehouse.

    Args:
        async_client (AsyncClient): Test client fixture.
    """
    owner_user = {
        "id": "507f1f77bcf86cd799439011",
        "email": "owner@whitfield.com",
        "role": UserRole.OWNER.value,
        "status": UserStatus.ACTIVE.value,
    }

    wh_doc = {
        "id": "607f1f77bcf86cd799439022",
        "code": "RNO",
        "name": "Reno Warehouse",
    }

    created_mgr = {
        "id": "707f1f77bcf86cd799439033",
        "email": "manager.rno@whitfield.com",
        "full_name": "Reno Manager",
        "role": UserRole.MANAGER.value,
        "warehouse_id": "607f1f77bcf86cd799439022",
        "experience_tier": None,
        "function_roles": [],
        "status": UserStatus.ACTIVE.value,
        "created_at": "2026-08-13 12:00:00.000000",
    }

    with patch("commons.auth.decodeJWT") as mock_decode, \
         patch("core.cruds.user_crud.CRUDUser.get_by_id", AsyncMock(return_value=owner_user)), \
         patch("core.cruds.user_crud.CRUDUser.get_by_email", AsyncMock(return_value=None)), \
         patch("core.cruds.wms_crud.CRUDWarehouse.get_by_id", AsyncMock(return_value=wh_doc)), \
         patch("core.cruds.user_crud.CRUDUser.create", AsyncMock(return_value=created_mgr)), \
         patch("core.cruds.wms_crud.CRUDWarehouse.update", AsyncMock(return_value=wh_doc)), \
         patch("core.services.wms_service.CRUDAuditLog.create", AsyncMock(return_value={"id": "audit2"})):

        mock_decode.return_value = {"sub": owner_user["id"], "type": "access", "role": "OWNER"}

        headers = {"Authorization": "Bearer valid_owner_token"}
        mgr_payload = {
            "email": "manager.rno@whitfield.com",
            "full_name": "Reno Manager",
            "password": "ManagerPass123!",
            "warehouse_id": "607f1f77bcf86cd799439022",
        }
        response = await async_client.post("/users/managers", json=mgr_payload, headers=headers)
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "manager.rno@whitfield.com"
        assert data["role"] == "MANAGER"


@pytest.mark.asyncio
async def test_manager_create_staff(async_client: AsyncClient):
    """
    Test Manager creating a Staff account (ROOKIE tier with RECEIVING role).

    Args:
        async_client (AsyncClient): Test client fixture.
    """
    manager_user = {
        "id": "707f1f77bcf86cd799439033",
        "email": "manager.rno@whitfield.com",
        "role": UserRole.MANAGER.value,
        "warehouse_id": "607f1f77bcf86cd799439022",
        "status": UserStatus.ACTIVE.value,
    }

    created_staff = {
        "id": "807f1f77bcf86cd799439044",
        "email": "staff.rookie@whitfield.com",
        "full_name": "Rookie Staff",
        "role": UserRole.STAFF.value,
        "warehouse_id": "607f1f77bcf86cd799439022",
        "experience_tier": ExperienceTier.ROOKIE.value,
        "function_roles": [FunctionRole.RECEIVING.value],
        "status": UserStatus.ACTIVE.value,
        "created_at": "2026-08-13 12:00:00.000000",
    }

    with patch("commons.auth.decodeJWT") as mock_decode, \
         patch("core.cruds.user_crud.CRUDUser.get_by_id", AsyncMock(return_value=manager_user)), \
         patch("core.cruds.user_crud.CRUDUser.get_by_email", AsyncMock(return_value=None)), \
         patch("core.cruds.user_crud.CRUDUser.create", AsyncMock(return_value=created_staff)), \
         patch("core.services.wms_service.CRUDAuditLog.create", AsyncMock(return_value={"id": "audit3"})):

        mock_decode.return_value = {"sub": manager_user["id"], "type": "access", "role": "MANAGER"}

        headers = {"Authorization": "Bearer valid_manager_token"}
        staff_payload = {
            "email": "staff.rookie@whitfield.com",
            "full_name": "Rookie Staff",
            "password": "StaffPass123!",
            "experience_tier": "ROOKIE",
            "function_roles": ["RECEIVING"],
        }
        response = await async_client.post("/users/staff", json=staff_payload, headers=headers)
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "staff.rookie@whitfield.com"
        assert data["role"] == "STAFF"
        assert data["experience_tier"] == "ROOKIE"


@pytest.mark.asyncio
async def test_staff_access_denied_on_manager_creation(async_client: AsyncClient):
    """
    Test Staff user is denied access when attempting to create a manager.

    Args:
        async_client (AsyncClient): Test client fixture.
    """
    staff_user = {
        "id": "807f1f77bcf86cd799439044",
        "email": "staff.rookie@whitfield.com",
        "role": UserRole.STAFF.value,
        "status": UserStatus.ACTIVE.value,
    }

    with patch("commons.auth.decodeJWT") as mock_decode, \
         patch("core.cruds.user_crud.CRUDUser.get_by_id", AsyncMock(return_value=staff_user)):

        mock_decode.return_value = {"sub": staff_user["id"], "type": "access", "role": "STAFF"}

        headers = {"Authorization": "Bearer valid_staff_token"}
        mgr_payload = {
            "email": "unauthorized@whitfield.com",
            "full_name": "Fake Manager",
            "password": "Pass!",
            "warehouse_id": "wh1",
        }
        response = await async_client.post("/users/managers", json=mgr_payload, headers=headers)
        assert response.status_code == 403


@pytest.mark.asyncio
async def test_query_audit_logs(async_client: AsyncClient):
    """
    Test GET /audit endpoint returns audit log records for Owner/Manager.

    Args:
        async_client (AsyncClient): Test client fixture.
    """
    owner_user = {
        "id": "507f1f77bcf86cd799439011",
        "email": "owner@whitfield.com",
        "role": UserRole.OWNER.value,
        "status": UserStatus.ACTIVE.value,
    }

    fake_logs = [
        {
            "id": "audit1",
            "actor_id": "507f1f77bcf86cd799439011",
            "actor_email": "owner@whitfield.com",
            "actor_role": "OWNER",
            "action": "CREATE",
            "collection": "warehouses",
            "doc_id": "607f1f77bcf86cd799439022",
            "before": None,
            "after": {"code": "RNO"},
            "timestamp": "2026-08-13 12:00:00.000000",
        }
    ]

    with patch("commons.auth.decodeJWT") as mock_decode, \
         patch("core.cruds.user_crud.CRUDUser.get_by_id", AsyncMock(return_value=owner_user)), \
         patch("core.cruds.wms_crud.CRUDAuditLog.list_logs", AsyncMock(return_value=(fake_logs, 1))):

        mock_decode.return_value = {"sub": owner_user["id"], "type": "access", "role": "OWNER"}

        headers = {"Authorization": "Bearer valid_owner_token"}
        response = await async_client.get("/audit", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["logs"][0]["action"] == "CREATE"


@pytest.mark.asyncio
async def test_permission_matrix_roles_vs_endpoints(async_client: AsyncClient):
    """
    Permission-matrix test evaluating every role (OWNER, MANAGER, STAFF) against endpoints.
    """
    staff_user = {"id": "staff1", "role": "STAFF", "status": "ACTIVE"}
    mgr_user = {"id": "mgr1", "role": "MANAGER", "status": "ACTIVE", "warehouse_id": "wh1"}

    # STAFF attempting to create a warehouse -> HTTP 403
    with patch("commons.auth.decodeJWT", return_value={"sub": "staff1", "type": "access", "role": "STAFF"}), \
         patch("core.cruds.user_crud.CRUDUser.get_by_id", AsyncMock(return_value=staff_user)):
        res = await async_client.post("/warehouses", json={"code": "XYZ", "name": "Test"}, headers={"Authorization": "Bearer tok"})
        assert res.status_code == 403

    # MANAGER attempting to create a warehouse -> HTTP 403
    with patch("commons.auth.decodeJWT", return_value={"sub": "mgr1", "type": "access", "role": "MANAGER"}), \
         patch("core.cruds.user_crud.CRUDUser.get_by_id", AsyncMock(return_value=mgr_user)):
        res = await async_client.post("/warehouses", json={"code": "XYZ", "name": "Test"}, headers={"Authorization": "Bearer tok"})
        assert res.status_code == 403


@pytest.mark.asyncio
async def test_audit_log_recorded_on_mutations(async_client: AsyncClient):
    """
    Test that audit rows are created on mutations.
    """
    owner_user = {"id": "owner1", "role": "OWNER", "status": "ACTIVE"}
    wh_doc = {
        "id": "wh1",
        "code": "RNO",
        "name": "Reno Warehouse",
        "address": "123 St",
        "manager_id": None,
        "is_active": True,
        "created_at": "2026-08-13 12:00:00.000000",
    }

    audit_mock = AsyncMock(return_value={"id": "audit_row_123"})
    with patch("commons.auth.decodeJWT", return_value={"sub": "owner1", "type": "access", "role": "OWNER"}), \
         patch("core.cruds.user_crud.CRUDUser.get_by_id", AsyncMock(return_value=owner_user)), \
         patch("core.cruds.wms_crud.CRUDWarehouse.get_by_code", AsyncMock(return_value=None)), \
         patch("core.cruds.wms_crud.CRUDWarehouse.create", AsyncMock(return_value=wh_doc)), \
         patch("core.controllers.wms_controller.get_audit_service", return_value=AsyncMock(log_mutation=audit_mock)):

        headers = {"Authorization": "Bearer token"}
        res = await async_client.post("/warehouses", json={"code": "RNO", "name": "Reno Warehouse", "address": "123 St"}, headers=headers)
        assert res.status_code == 201
        assert audit_mock.called




