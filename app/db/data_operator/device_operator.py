from typing import List, Optional, Dict, Any, Union
from app.db.models import Device, DeviceCreate, DeviceStatus, OS
from app.db.collection_operator.collection_interface import CollectionInterface
import logging

logger = logging.getLogger(__name__)


class DeviceOperator:
    def __init__(self, devices_collection: CollectionInterface, users_collection: CollectionInterface):
        self.collection = devices_collection
        self.users_collection = users_collection

    def create(self, device_data: DeviceCreate) -> Device:
        try:
            new_device = Device.create_new(**device_data.model_dump())

            result = self.collection.insert_one(new_device.to_mongo())

            if result.inserted_id:
                logger.info(f"Device created with ci_id: {new_device.ci_id}")
                return new_device
            else:
                raise Exception("Failed to insert device")

        except Exception as e:
            logger.error(f"Error creating device: {e}")
            raise

    def find_by_ci_id(self, ci_id: str) -> Optional[Device]:
        try:
            device_data = self.collection.find_one({"ci_id": ci_id})
            if device_data:
                return Device.from_mongo(device_data)
            return None
        except Exception as e:
            logger.error(f"Error finding device by ci_id {ci_id}: {e}")
            return None

    def find_by_device_id(self, device_id: str) -> Optional[Device]:
        try:
            device_data = self.collection.find_one({"device_id": device_id})
            if device_data:
                return Device.from_mongo(device_data)
            return None
        except Exception as e:
            logger.error(f"Error finding device by device_id {device_id}: {e}")
            return None

    def find_by_hostname(self, hostname: str) -> Optional[Device]:
        try:
            device_data = self.collection.find_one({"hostname": hostname})
            if device_data:
                return Device.from_mongo(device_data)
            return None
        except Exception as e:
            logger.error(f"Error finding device by hostname {hostname}: {e}")
            return None

    def find_all(self, skip: int = 0, limit: int = 100) -> List[Device]:
        try:
            cursor = self.collection.find().skip(skip).limit(limit)
            devices = []
            for device_data in cursor:
                devices.append(Device.from_mongo(device_data))
            return devices
        except Exception as e:
            logger.error(f"Error finding all devices: {e}")
            return []

    def find_by_status(self, status: DeviceStatus) -> List[Device]:
        try:
            cursor = self.collection.find({"status": status.value})
            devices = []
            for device_data in cursor:
                devices.append(Device.from_mongo(device_data))
            return devices
        except Exception as e:
            logger.error(f"Error finding devices by status {status}: {e}")
            return []

    def find_by_os(self, os: OS) -> List[Device]:
        try:
            cursor = self.collection.find({"os": os.value})
            devices = []
            for device_data in cursor:
                devices.append(Device.from_mongo(device_data))
            return devices
        except Exception as e:
            logger.error(f"Error finding devices by OS {os}: {e}")
            return []

    def find_by_assigned_user(self, assigned_user: str) -> List[Device]:
        try:
            cursor = self.collection.find({"assigned_user": assigned_user})
            devices = []
            for device_data in cursor:
                devices.append(Device.from_mongo(device_data))
            return devices
        except Exception as e:
            logger.error(f"Error finding devices by assigned user {assigned_user}: {e}")
            return []

    def find_by_location(self, location: str) -> List[Device]:
        try:
            cursor = self.collection.find({"location": location})
            devices = []
            for device_data in cursor:
                devices.append(Device.from_mongo(device_data))
            return devices
        except Exception as e:
            logger.error(f"Error finding devices by location {location}: {e}")
            return []

    def find_by_filter(self, filter_dict: Dict[str, Any], limit: int = 100) -> List[Device]:
        """Find devices by arbitrary filter criteria."""
        try:
            cursor = self.collection.find(filter_dict).limit(limit)
            devices = []
            for device_data in cursor:
                devices.append(Device.from_mongo(device_data))
            logger.info(f"Found {len(devices)} devices matching filter")
            return devices
        except Exception as e:
            logger.error(f"Error finding devices by filter {filter_dict}: {e}")
            return []

    def execute_aggregation(self, pipeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute aggregation pipeline on devices collection."""
        try:
            results = self.collection.aggregate(pipeline)
            logger.info(f"Aggregation executed on devices collection, returned {len(results)} results")
            return results
        except Exception as e:
            logger.error(f"Error executing aggregation on devices collection: {e}")
            return []

    def execute_query(self, query: Dict[str, Any]) -> Union[List[Device], List[Dict[str, Any]], int]:
        """Execute a MongoDB query generated by LLM on devices collection."""
        try:
            if "pipeline" in query:
                # Aggregation pipeline
                pipeline = query["pipeline"]
                return self.execute_aggregation(pipeline)

            elif "query" in query:
                # Simple find query
                filter_dict = query["query"]
                limit = query.get("limit", 100)

                # Check if this is a count operation
                if query.get("operation") == "count" or query.get("count"):
                    return self.collection.count_documents(filter_dict)

                return self.find_by_filter(filter_dict, limit)

            elif "count" in query:
                # Count operation
                filter_dict = query.get("filter", {})
                return self.collection.count_documents(filter_dict)

            else:
                logger.error(f"Unsupported query format: {query}")
                return []

        except Exception as e:
            logger.error(f"Error executing query on devices collection: {e}")
            return []