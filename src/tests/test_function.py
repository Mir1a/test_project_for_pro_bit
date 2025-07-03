# region -----External Imports-----
import pytest
from datetime import timedelta
from unittest.mock import patch, AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession
# endregion

# region -----Internal Imports-----
from ..api import services, schemas, jwt
from ..models import CoreUser, Organization
# endregion


class TestAuthUtils:

    def test_create_access_token(self):
        data = {"sub": "123", "context": "core"}
        token = jwt.create_access_token(data)

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_refresh_token(self):
        data = {"sub": "123", "context": "core"}
        token = jwt.create_refresh_token(data)

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_decode_valid_token(self):
        original_data = {"sub": "123", "context": "core"}
        token = jwt.create_access_token(original_data)

        decoded_data = jwt.decode_token(token)

        assert decoded_data["sub"] == "123"
        assert decoded_data["context"] == "core"
        assert "exp" in decoded_data

    def test_decode_invalid_token(self):
        with pytest.raises(ValueError, match="Invalid token"):
            jwt.decode_token("invalid.token.here")

    def test_token_expiration(self):
        data = {"sub": "123", "context": "core"}
        expired_delta = timedelta(seconds=-10)
        token = jwt.create_access_token(data, expired_delta)

        with pytest.raises(ValueError, match="Token has expired"):
            jwt.decode_token(token)


class TestPasswordFunctions:

    def test_hash_password(self):
        password = "TestPassword123"
        hashed = services.hash_password(password)

        assert hashed is not None
        assert isinstance(hashed, str)
        assert hashed != password
        assert len(hashed) > 0

    def test_verify_correct_password(self):
        password = "TestPassword123"
        hashed = services.hash_password(password)

        assert services.verify_password(password, hashed) is True

    def test_verify_incorrect_password(self):
        password = "TestPassword123"
        wrong_password = "WrongPassword456"
        hashed = services.hash_password(password)

        assert services.verify_password(wrong_password, hashed) is False

    def test_hash_different_passwords_different_hashes(self):
        password1 = "Password123"
        password2 = "Password456"

        hash1 = services.hash_password(password1)
        hash2 = services.hash_password(password2)

        assert hash1 != hash2


class TestCoreUserServices:

    @pytest.mark.asyncio
    async def test_create_core_user_success(self):
        mock_session = AsyncMock(spec=AsyncSession)

        with patch('src.api.query.get_core_user_by_email', return_value=None):
            user_data = schemas.CoreUserCreate(
                email="test@example.com",
                password="TestPass123",
                first_name="John",
                last_name="Doe"
            )

            result = await services.create_core_user(user_data, mock_session)

            mock_session.add.assert_called_once()
            mock_session.commit.assert_called_once()
            mock_session.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_core_user_email_exists(self):
        mock_session = AsyncMock(spec=AsyncSession)
        existing_user = CoreUser(email="test@example.com")

        with patch('src.api.query.get_core_user_by_email', return_value=existing_user):
            user_data = schemas.CoreUserCreate(
                email="test@example.com",
                password="TestPass123"
            )

            with pytest.raises(ValueError, match="Email already registered"):
                await services.create_core_user(user_data, mock_session)

    @pytest.mark.asyncio
    async def test_authenticate_core_user_success(self):
        mock_session = AsyncMock(spec=AsyncSession)

        hashed_password = services.hash_password("TestPass123")
        mock_user = CoreUser(
            id=1,
            email="test@example.com",
            hashed_password=hashed_password,
            is_active=True
        )

        with patch('src.api.query.get_core_user_by_email', return_value=mock_user):
            result = await services.authenticate_core_user(
                "test@example.com",
                "TestPass123",
                mock_session
            )

            assert result["success"] is True
            assert result["user_id"] == 1
            assert result["context"] == "core"
            assert "access_token" in result
            assert "refresh_token" in result

    @pytest.mark.asyncio
    async def test_authenticate_core_user_invalid_credentials(self):
        mock_session = AsyncMock(spec=AsyncSession)

        with patch('src.api.query.get_core_user_by_email', return_value=None):
            with pytest.raises(ValueError, match="Invalid credentials"):
                await services.authenticate_core_user(
                    "test@example.com",
                    "WrongPassword",
                    mock_session
                )

    @pytest.mark.asyncio
    async def test_authenticate_inactive_user(self):
        mock_session = AsyncMock(spec=AsyncSession)

        hashed_password = services.hash_password("TestPass123")
        inactive_user = CoreUser(
            id=1,
            email="test@example.com",
            hashed_password=hashed_password,
            is_active=False
        )

        with patch('src.api.query.get_core_user_by_email', return_value=inactive_user):
            with pytest.raises(ValueError, match="Account is inactive"):
                await services.authenticate_core_user(
                    "test@example.com",
                    "TestPass123",
                    mock_session
                )


class TestOrganizationServices:

    @pytest.mark.asyncio
    async def test_create_organization_success(self):
        mock_session = AsyncMock(spec=AsyncSession)

        with patch('src.api.query.get_organization_by_slug', return_value=None):
            mock_owner = CoreUser(id=1, email="owner@example.com")
            with patch('src.api.query.get_core_user_by_id', return_value=mock_owner):
                org_data = schemas.OrganizationCreate(
                    name="Test Company",
                    slug="test-company",
                    description="Test organization"
                )

                result = await services.create_organization(org_data, 1, mock_session)

                mock_session.add.assert_called_once()
                mock_session.commit.assert_called_once()
                mock_session.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_organization_slug_exists(self):
        mock_session = AsyncMock(spec=AsyncSession)

        existing_org = Organization(slug="test-company")
        with patch('src.api.query.get_organization_by_slug', return_value=existing_org):
            org_data = schemas.OrganizationCreate(
                name="Test Company",
                slug="test-company"
            )

            with pytest.raises(ValueError, match="Organization with this slug already exists"):
                await services.create_organization(org_data, 1, mock_session)


class TestSchemaValidation:

    def test_core_user_create_valid_password(self):
        user_data = schemas.CoreUserCreate(
            email="test@example.com",
            password="ValidPass123",
            first_name="John"
        )
        assert user_data.password == "ValidPass123"

    def test_core_user_create_weak_password(self):
        with pytest.raises(ValueError, match="Password must contain at least 8 characters"):
            schemas.CoreUserCreate(
                email="test@example.com",
                password="weak",
                first_name="John"
            )

    def test_core_user_create_password_no_uppercase(self):
        with pytest.raises(ValueError, match="Password must contain at least one uppercase letter"):
            schemas.CoreUserCreate(
                email="test@example.com",
                password="lowercase123",
                first_name="John"
            )

    def test_organization_create_valid_slug(self):
        org_data = schemas.OrganizationCreate(
            name="Test Company",
            slug="test-company-123"
        )
        assert org_data.slug == "test-company-123"

    def test_organization_create_invalid_slug(self):
        with pytest.raises(ValueError):
            schemas.OrganizationCreate(
                name="Test Company",
                slug="Test_Company!"
            )