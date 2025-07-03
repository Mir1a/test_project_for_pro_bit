# region -----External Imports-----
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from datetime import datetime
# endregion

# region -----Internal Imports-----
from . import database
# endregion

# region -----Association Tables-----
organization_owners = Table(
    'organization_owners',
    database.Base.metadata,
    Column('user_id', Integer, ForeignKey('core_users.id'), primary_key=True),
    Column('organization_id', Integer, ForeignKey('organizations.id'), primary_key=True)
)
# endregion


# region -----Core Database Models-----
class CoreUser(database.Base):
    __tablename__ = 'core_users'

    # region -----Basic Info-----
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    # endregion

    # region -----Relations-----
    owned_organizations = relationship(
        "Organization",
        secondary=organization_owners,
        back_populates="owners"
    )
    # endregion


class Organization(database.Base):
    __tablename__ = 'organizations'

    # region -----Basic Info-----
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    # endregion

    # region -----Database Connection-----
    database_name = Column(String(100), nullable=False, unique=True)
    # endregion

    # region -----Relations-----
    owners = relationship(
        "CoreUser",
        secondary=organization_owners,
        back_populates="owned_organizations"
    )
    # endregion
# endregion


# region -----Tenant Database Models-----
class TenantUser(database.Base):
    __tablename__ = 'tenant_users'

    # region -----Basic Info-----
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    # endregion

    # region -----Profile Info-----
    avatar = Column(String(500), nullable=True)
    bio = Column(String(1000), nullable=True)
    # endregion

    # region -----Organization Link-----
    organization_id = Column(Integer, nullable=False)
    # endregion
# endregion
