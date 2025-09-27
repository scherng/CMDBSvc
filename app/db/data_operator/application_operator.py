from typing import List, Optional, Dict, Any
from app.db.models import Application, ApplicationCreate, ApplicationUpdate, ApplicationType
from app.db.collection_operator.collection_interface import CollectionInterface
import logging

logger = logging.getLogger(__name__)


class ApplicationOperator:
    def __init__(self, apps_collection: CollectionInterface, users_collection: CollectionInterface):
        self.collection = apps_collection
        self.users_collection = users_collection

    def create(self, app_data: ApplicationCreate) -> Application:
        try:
            new_app = Application.create_new(**app_data.model_dump())

            result = self.collection.insert_one(new_app.to_mongo())

            if result.inserted_id:
                logger.info(f"Application created with ci_id: {new_app.ci_id}")
                return new_app
            else:
                raise Exception("Failed to insert application")

        except Exception as e:
            logger.error(f"Error creating application: {e}")
            raise

    def find_by_ci_id(self, ci_id: str) -> Optional[Application]:
        try:
            app_data = self.collection.find_one({"ci_id": ci_id})
            if app_data:
                return Application.from_mongo(app_data)
            return None
        except Exception as e:
            logger.error(f"Error finding application by ci_id {ci_id}: {e}")
            return None

    def find_by_app_id(self, app_id: str) -> Optional[Application]:
        try:
            app_data = self.collection.find_one({"app_id": app_id})
            if app_data:
                return Application.from_mongo(app_data)
            return None
        except Exception as e:
            logger.error(f"Error finding application by app_id {app_id}: {e}")
            return None

    def find_by_name(self, name: str) -> Optional[Application]:
        try:
            app_data = self.collection.find_one({"name": name})
            if app_data:
                return Application.from_mongo(app_data)
            return None
        except Exception as e:
            logger.error(f"Error finding application by name {name}: {e}")
            return None

    def find_all(self, skip: int = 0, limit: int = 100) -> List[Application]:
        try:
            cursor = self.collection.find().skip(skip).limit(limit)
            apps = []
            for app_data in cursor:
                apps.append(Application.from_mongo(app_data))
            return apps
        except Exception as e:
            logger.error(f"Error finding all applications: {e}")
            return []

    def add_user(self, app_ci_id: str, user_ci_id: str) -> bool:
        try:
            result = self.collection.update_one(
                {"ci_id": app_ci_id},
                {"$addToSet": {"user_ids": user_ci_id}}
            )

            if result.modified_count > 0:
                self.users_collection.update_one(
                    {"ci_id": user_ci_id},
                    {"$addToSet": {"assigned_application_ids": app_ci_id}}
                )
                logger.info(f"User {user_ci_id} added to application {app_ci_id}")
                return True
            return False

        except Exception as e:
            logger.error(f"Error adding user to application: {e}")
            return False
        
    def find_by_owner(self, owner: str) -> List[Application]:
        try:
            cursor = self.collection.find({"owner": owner})
            apps = []
            for app_data in cursor:
                apps.append(Application.from_mongo(app_data))
            return apps
        except Exception as e:
            logger.error(f"Error finding applications by owner {owner}: {e}")
            return []

    def find_by_type(self, app_type: ApplicationType) -> List[Application]:
        try:
            cursor = self.collection.find({"type": app_type.value})
            apps = []
            for app_data in cursor:
                apps.append(Application.from_mongo(app_data))
            return apps
        except Exception as e:
            logger.error(f"Error finding applications by type {app_type}: {e}")
            return []

    def increment_usage(self, ci_id: str) -> bool:
        try:
            result = self.collection.update_one(
                {"ci_id": ci_id},
                {"$inc": {"usage_count": 1}}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error incrementing usage for application {ci_id}: {e}")
            return False

    def add_integration(self, ci_id: str, integration: str) -> bool:
        try:
            result = self.collection.update_one(
                {"ci_id": ci_id},
                {"$addToSet": {"integrations": integration}}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error adding integration to application {ci_id}: {e}")
            return False

    def remove_integration(self, ci_id: str, integration: str) -> bool:
        try:
            result = self.collection.update_one(
                {"ci_id": ci_id},
                {"$pull": {"integrations": integration}}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error removing integration from application {ci_id}: {e}")
            return False