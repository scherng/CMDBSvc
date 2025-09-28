from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
import uuid

class ApplicationType(str, Enum):
    SAAS = "SaaS"
    ON_PREM = "on-prem"

class EntityType(str, Enum):
    USER = "user"
    APPLICATION = "application"
    DEVICE = "device"

class UserBase(BaseModel):
    name: str
    team: Optional[str] = None
    permission_group: List[str] = Field(default_factory=list, description="User's provisioned permission") 
    mfa_enabled: bool = False
    last_login: Optional[datetime] = None
    assigned_application_ids: List[str] = Field(default_factory=list)

class User(UserBase):
    ci_id: str = Field(..., description="Configuration item ID")
    user_id: str = Field(..., description="Unique user ID")

    @classmethod
    def create_new(cls, **data) -> "User":
        return cls(
            ci_id=f"CI-{uuid.uuid4().hex[:12].upper()}",
            user_id=f"USR-{uuid.uuid4().hex[:12].upper()}",
            **data
        )

    def to_mongo(self) -> Dict[str, Any]:
        data = self.model_dump(exclude_none=True)
        return data

    @classmethod
    def from_mongo(cls, data: Dict[str, Any]) -> "User":
        if "_id" in data:
            data.pop("_id")
        return cls(**data)

class UserCreate(UserBase):
    pass

class OS (str, Enum):
    WINDOWS = "windows"
    MACOS = "macOS"
    LINUX = "ubuntu"

class DeviceStatus(str, Enum):
    INACTIVE = "inactive"
    ACTIVE = "active"
    SUSPENDED = "suspended"

class DeviceBase(BaseModel):
    hostname: str = Field(..., description="Device Hostname")
    ip_address: str = Field(..., description="Unique device ID")
    os: OS.WINDOWS
    assigned_user: str = Field(description="User Id of the device's assigned user")
    location: str
    status: DeviceStatus.INACTIVE

class Device(DeviceBase):
    ci_id: str = Field(..., description="Configuration item ID")
    device_id: str = Field(..., description="Unique device ID")

    @classmethod
    def create_new(cls, **data) -> "Device":
        return cls(
            ci_id=f"CI-{uuid.uuid4().hex[:12].upper()}",
            app_id=f"DVC-{uuid.uuid4().hex[:12].upper()}",
            **data
        )

    def to_mongo(self) -> Dict[str, Any]:
        data = self.model_dump(exclude_none=True)
        return data

    @classmethod
    def from_mongo(cls, data: Dict[str, Any]) -> "Device":
        if "_id" in data:
            data.pop("_id")
        return cls(**data)

class DeviceCreate(DeviceBase):
    pass

class ApplicationBase(BaseModel):
    name: str
    owner: str
    #TODO check default value
    type: ApplicationType = ApplicationType.SAAS
    integrations: List[str] = Field(default_factory=list)
    usage_count: int = 0

class Application(ApplicationBase):
    ci_id: str = Field(..., description="Configuration item ID")
    app_id: str = Field(..., description="Unique application ID")

    @classmethod
    def create_new(cls, **data) -> "Application":
        return cls(
            ci_id=f"CI-{uuid.uuid4().hex[:12].upper()}",
            app_id=f"APP-{uuid.uuid4().hex[:12].upper()}",
            **data
        )

    def to_mongo(self) -> Dict[str, Any]:
        data = self.model_dump(exclude_none=True)
        return data

    @classmethod
    def from_mongo(cls, data: Dict[str, Any]) -> "Application":
        if "_id" in data:
            data.pop("_id")
        return cls(**data)

class ApplicationCreate(ApplicationBase):
    pass