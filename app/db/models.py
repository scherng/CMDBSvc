from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
import uuid


class ApplicationType(str, Enum):
    SAAS = "SaaS"
    ON_PREM = "on-prem"


class UserBase(BaseModel):
    name: str
    team: Optional[str] = None
    mfa_status: bool = False
    last_login: Optional[datetime] = None
    assigned_application_ids: List[str] = Field(default_factory=list)


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    name: Optional[str] = None
    team: Optional[str] = None
    mfa_status: Optional[bool] = None
    last_login: Optional[datetime] = None
    assigned_application_ids: Optional[List[str]] = None


class User(UserBase):
    ci_id: str = Field(..., description="Configuration item ID")
    user_id: str = Field(..., description="Unique user ID")

    @classmethod
    def create_new(cls, **data) -> "User":
        return cls(
            ci_id=f"CI-USER-{uuid.uuid4().hex[:8].upper()}",
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

class OS (str, enum):
    WINDOWS = "windows"
    MACOS = "macOS"
    LINUX = "ubuntu"

class DeviceBase(BaseModel):
    hostname: str
    ip_address: str
    os: OS.WINDOWS
    assigned_user: str #indicates the id



class ApplicationBase(BaseModel):
    name: str
    owner: str
    #TODO check default value
    type: ApplicationType = ApplicationType.SAAS
    integrations: List[str] = Field(default_factory=list)
    usage_count: int = 0


class ApplicationCreate(ApplicationBase):
    pass


class ApplicationUpdate(BaseModel):
    name: Optional[str] = None
    owner: Optional[str] = None
    type: Optional[ApplicationType] = None
    integrations: Optional[List[str]] = None
    usage_count: Optional[int] = None


class Application(ApplicationBase):
    ci_id: str = Field(..., description="Configuration item ID")
    app_id: str = Field(..., description="Unique application ID")
    user_ids: List[str] = Field(default_factory=list)

    @classmethod
    def create_new(cls, **data) -> "Application":
        return cls(
            ci_id=f"CI-APP-{uuid.uuid4().hex[:8].upper()}",
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

