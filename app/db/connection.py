from app.db.factory import DatabaseFactory
from app.db.interfaces.collection_interface import CollectionInterface
from app.db.data_operator.user_operator import UserOperator
from app.db.data_operator.application_operator import ApplicationOperator
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


def get_user_operator() -> UserOperator:
    users_collection = get_users_collection()
    apps_collection = get_applications_collection()
    return UserOperator(users_collection, apps_collection)


def get_application_operator() -> ApplicationOperator:
    apps_collection = get_applications_collection()
    users_collection = get_users_collection()
    return ApplicationOperator(apps_collection, users_collection)


