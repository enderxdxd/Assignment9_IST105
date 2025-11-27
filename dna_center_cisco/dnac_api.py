import requests
from requests.auth import HTTPBasicAuth
from dnac_config import DNAC
import urllib3
from django.conf import settings
from pymongo import MongoClient
from datetime import datetime

# Disable SSL warnings for sandbox
urllib3.disable_warnings()

class DNAC_Manager:
    def __init__(self):
        self.token = None

    def get_auth_token(self):
        """Authenticates to DNA Center and stores token. Returns (success, error_msg)."""
        try:
            url = f"https://{DNAC['host']}:{DNAC['port']}/dna/system/api/v1/auth/token"
            response = requests.post(
                url,
                auth=HTTPBasicAuth(DNAC['username'], DNAC['password']),
                verify=False,
                timeout=10
            )
            response.raise_for_status()
            self.token = response.json()['Token']
            return True, None
        except Exception as e:
            return False, str(e)

    def get_network_devices(self):
        """Retrieves all network devices. Returns (devices_list_or_None, error_msg)."""
        if not self.token:
            return None, "Missing authentication token. Please authenticate first."

        try:
            url = f"https://{DNAC['host']}:{DNAC['port']}/api/v1/network-device"
            headers = {"X-Auth-Token": self.token}
            response = requests.get(
                url,
                headers=headers,
                verify=False,
                timeout=10
            )
            response.raise_for_status()
            devices = response.json().get('response', [])
            return devices, None
        except Exception as e:
            return None, str(e)

    def get_device_interfaces(self, device_ip):
        """Retrieves interfaces for specific device IP. Returns (interfaces_or_None, error_msg)."""
        if not self.token:
            return None, "Missing authentication token. Please authenticate first."

        try:
            # Find device by IP
            devices, err = self.get_network_devices()
            if devices is None:
                return None, err or "Could not retrieve devices."

            device = next(
                (d for d in devices if d.get('managementIpAddress') == device_ip),
                None
            )
            if not device:
                return None, f"Device {device_ip} not found."

            # Get interfaces
            url = f"https://{DNAC['host']}:{DNAC['port']}/api/v1/interface"
            headers = {"X-Auth-Token": self.token}
            params = {"deviceId": device['id']}
            response = requests.get(
                url,
                headers=headers,
                params=params,
                verify=False,
                timeout=10
            )
            response.raise_for_status()
            interfaces = response.json().get('response', [])
            return interfaces, None

        except Exception as e:
            return None, str(e)


# Singleton DNAC manager used by all views
dnac_manager = DNAC_Manager()


def get_mongo_collection():
    """
    Returns MongoDB collection handle.
    MONGO_URI must be configured in Django settings.
    """
    client = MongoClient(settings.MONGO_URI)
    db = client["assignment9"]
    return db["dnac_logs"]


def log_action(action, status, device_ip=None, message=None):
    """
    Stores:
      - timestamp
      - action (authenticate, list_devices, show_interfaces)
      - status (success/failure)
      - device_ip (optional)
      - message (optional error or info)
    """
    try:
        collection = get_mongo_collection()
        doc = {
            "timestamp": datetime.utcnow(),
            "action": action,
            "status": status,
            "device_ip": device_ip,
            "message": message
        }
        collection.insert_one(doc)
    except Exception:
        # Em produção você poderia logar isso em outro lugar.
        # Para o assignment, ignorar erro de log é suficiente.
        pass
