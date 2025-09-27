from typing import List, Optional, Dict, Any
from app.db.models import User, UserCreate, UserUpdate
from app.db.interfaces.collection_interface import CollectionInterface
import logging

logger = logging.getLogger(__name__)


class UserRepository:
    def __init__(self, users_collection: CollectionInterface, apps_collection: CollectionInterface):
        self.collection = users_collection
        self.apps_collection = apps_collection

    def create(self, user_data: UserCreate) -> User:
        try:
            new_user = User.create_new(**user_data.model_dump())

            result = self.collection.insert_one(new_user.to_mongo())

            if result.inserted_id:
                logger.info(f"User created with ci_id: {new_user.ci_id}")
                return new_user
            else:
                raise Exception("Failed to insert user")

        except Exception as e:
            logger.error(f"Error creating user: {e}")
            raise

    def find_by_ci_id(self, ci_id: str) -> Optional[User]:
        try:
            user_data = self.collection.find_one({"ci_id": ci_id})
            if user_data:
                return User.from_mongo(user_data)
            return None
        except Exception as e:
            logger.error(f"Error finding user by ci_id {ci_id}: {e}")
            return None

    def find_by_user_id(self, user_id: str) -> Optional[User]:
        try:
            user_data = self.collection.find_one({"user_id": user_id})
            if user_data:
                return User.from_mongo(user_data)
            return None
        except Exception as e:
            logger.error(f"Error finding user by user_id {user_id}: {e}")
            return None

    def find_by_name(self, name: str) -> Optional[User]:
        try:
            user_data = self.collection.find_one({"name": name})
            if user_data:
                return User.from_mongo(user_data)
            return None
        except Exception as e:
            logger.error(f"Error finding user by name {name}: {e}")
            return None

    def find_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        try:
            cursor = self.collection.find().skip(skip).limit(limit)
            users = []
            for user_data in cursor:
                users.append(User.from_mongo(user_data))
            return users
        except Exception as e:
            logger.error(f"Error finding all users: {e}")
            return []

    def update(self, ci_id: str, user_update: UserUpdate) -> Optional[User]:
        try:
            update_data = user_update.model_dump(exclude_none=True)
            if not update_data:
                return self.find_by_ci_id(ci_id)

            result = self.collection.update_one(
                {"ci_id": ci_id},
                {"$set": update_data}
            )

            if result.modified_count > 0:
                logger.info(f"User {ci_id} updated")
                return self.find_by_ci_id(ci_id)
            elif result.matched_count > 0:
                return self.find_by_ci_id(ci_id)
            else:
                logger.warning(f"User {ci_id} not found for update")
                return None

        except Exception as e:
            logger.error(f"Error updating user {ci_id}: {e}")
            return None

    def delete(self, ci_id: str) -> bool:
        try:
            result = self.collection.delete_one({"ci_id": ci_id})

            if result.deleted_count > 0:
                self.apps_collection.update_many(
                    {"user_ids": ci_id},
                    {"$pull": {"user_ids": ci_id}}
                )
                logger.info(f"User {ci_id} deleted")
                return True
            else:
                logger.warning(f"User {ci_id} not found for deletion")
                return False

        except Exception as e:
            logger.error(f"Error deleting user {ci_id}: {e}")
            return False

    def add_application(self, user_ci_id: str, app_ci_id: str) -> bool:
        try:
            result = self.collection.update_one(
                {"ci_id": user_ci_id},
                {"$addToSet": {"assigned_application_ids": app_ci_id}}
            )

            if result.modified_count > 0:
                self.apps_collection.update_one(
                    {"ci_id": app_ci_id},
                    {"$addToSet": {"user_ids": user_ci_id}}
                )
                logger.info(f"Application {app_ci_id} added to user {user_ci_id}")
                return True
            return False

        except Exception as e:
            logger.error(f"Error adding application to user: {e}")
            return False

    def remove_application(self, user_ci_id: str, app_ci_id: str) -> bool:
        try:
            result = self.collection.update_one(
                {"ci_id": user_ci_id},
                {"$pull": {"assigned_application_ids": app_ci_id}}
            )

            if result.modified_count > 0:
                self.apps_collection.update_one(
                    {"ci_id": app_ci_id},
                    {"$pull": {"user_ids": user_ci_id}}
                )
                logger.info(f"Application {app_ci_id} removed from user {user_ci_id}")
                return True
            return False

        except Exception as e:
            logger.error(f"Error removing application from user: {e}")
            return False

    def find_by_team(self, team: str) -> List[User]:
        try:
            cursor = self.collection.find({"team": team})
            users = []
            for user_data in cursor:
                users.append(User.from_mongo(user_data))
            return users
        except Exception as e:
            logger.error(f"Error finding users by team {team}: {e}")
            return []

    def find_by_mfa_status(self, mfa_enabled: bool) -> List[User]:
        try:
            cursor = self.collection.find({"mfa_status": mfa_enabled})
            users = []
            for user_data in cursor:
                users.append(User.from_mongo(user_data))
            return users
        except Exception as e:
            logger.error(f"Error finding users by MFA status: {e}")
            return []