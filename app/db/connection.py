from app.db.factory import DatabaseFactory
from app.db.interfaces.collection_interface import CollectionInterface
from app.db.repositories.user_repository import UserRepository
from app.db.repositories.application_repository import ApplicationRepository
import logging

logger = logging.getLogger(__name__)


def get_users_collection() -> CollectionInterface:
    """Get the users collection interface."""
    database = DatabaseFactory.get_database()
    return database.get_collection("users")


def get_applications_collection() -> CollectionInterface:
    """Get the applications collection interface."""
    database = DatabaseFactory.get_database()
    return database.get_collection("applications")


def get_user_repository() -> UserRepository:
    """Get a UserRepository instance with injected dependencies."""
    users_collection = get_users_collection()
    apps_collection = get_applications_collection()
    return UserRepository(users_collection, apps_collection)


def get_application_repository() -> ApplicationRepository:
    """Get an ApplicationRepository instance with injected dependencies."""
    apps_collection = get_applications_collection()
    users_collection = get_users_collection()
    return ApplicationRepository(apps_collection, users_collection)


