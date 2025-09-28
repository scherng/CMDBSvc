from app.db.db_factory import DatabaseFactory
from app.db.collection_operator.collection_interface import CollectionInterface
from app.db.data_operator.user_operator import UserOperator
from app.db.data_operator.application_operator import ApplicationOperator
from app.db.models import User, Application
import logging
from typing import Optional


logger = logging.getLogger(__name__)

class EntityManager:
    def __init__(self):
        self.user_op  = self.get_user_operator()
        self.app_op = self.get_application_operator()

    def get_users_collection(self) -> CollectionInterface:
        """Get the users collection interface."""
        database = DatabaseFactory.get_database()
        return database.get_collection("users")


    def get_applications_collection(self) -> CollectionInterface:
        """Get the applications collection interface."""
        database = DatabaseFactory.get_database()
        return database.get_collection("applications")


    def get_user_operator(self) -> UserOperator:
        users_collection = self.get_users_collection()
        apps_collection = self.get_applications_collection()
        return UserOperator(users_collection, apps_collection)


    def get_application_operator(self) -> ApplicationOperator:
        apps_collection = self.get_applications_collection()
        users_collection = self.get_users_collection()
        return ApplicationOperator(apps_collection, users_collection)

    def get_entity_by_ci_id(self, ci_id: str) -> Optional[User | Application]:
        """
        Retrieve an entity by its CI ID.

        Args:
            ci_id: Configuration Item ID

        Returns:
            User or Application entity if found, None otherwise
        """
        # TODO I think we need to add a lookup table 
        # Try to find as user first
        user = self.user_op.find_by_ci_id(ci_id)
        if user:
            return user

        # Try to find as application
        application = self.app_op.find_by_ci_id(ci_id)
        if application:
            return application

        return None

