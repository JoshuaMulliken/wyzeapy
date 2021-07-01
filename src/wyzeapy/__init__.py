#  Copyright (c) 2021. Mulliken, LLC - All Rights Reserved
#  You may use, distribute and modify this code under the terms
#  of the attached license. You should have received a copy of
#  the license with this file. If not, please write to:
#  joshua@mulliken.net to receive a copy
import logging
from typing import Dict

from wyzeapy.services.bulb_service import BulbService
from wyzeapy.services.camera_service import CameraService
from wyzeapy.services.hms_service import HMSService
from wyzeapy.services.lock_service import LockService
from wyzeapy.services.sensor_service import SensorService
from wyzeapy.services.switch_service import SwitchService
from wyzeapy.services.thermostat_service import ThermostatService
from wyzeapy.wyze_auth_lib import WyzeAuthLib

_LOGGER = logging.getLogger(__name__)


class Wyzeapy:
    """A module to assist developers in interacting with the Wyze service"""
    # _client: Client
    _auth_lib: WyzeAuthLib

    def __init__(self):
        self._token: Dict[str, str] = {}
        self._bulb_service = None
        self._switch_service = None
        self._camera_service = None
        self._thermostat_service = None
        self._hms_service = None
        self._lock_service = None
        self._sensor_service = None
        self._email = None
        self._password = None

    @classmethod
    async def create(cls):
        """
        Creates the Wyzeapy class

        :return: An instance of the Wyzeapy class
        """
        self = cls()
        return self

    async def async_close(self):
        # await self._client.async_close()
        await self._auth_lib.close()
        pass

    async def login(self, email, password):
        _LOGGER.debug(f"Email: {email}")
        self._email = email
        _LOGGER.debug(f"Password: {password}")
        self._password = password
        self._auth_lib = await WyzeAuthLib.create(email, password)

    @classmethod
    async def valid_login(cls, email: str, password: str) -> bool:
        self = cls()
        await self.login(email, password)
        return not self._auth_lib.should_refresh

    @property
    async def bulb_service(self) -> BulbService:
        if self._bulb_service is None:
            self._bulb_service = BulbService(self._auth_lib)
        return self._bulb_service

    @property
    async def switch_service(self) -> SwitchService:
        if self._switch_service is None:
            self._switch_service = SwitchService(self._auth_lib)
        return self._switch_service

    @property
    async def camera_service(self) -> CameraService:
        if self._camera_service is None:
            self._camera_service = CameraService(self._auth_lib)
        return self._camera_service

    @property
    async def thermostat_service(self) -> ThermostatService:
        if self._thermostat_service is None:
            self._thermostat_service = ThermostatService(self._auth_lib)
        return self._thermostat_service

    @property
    async def hms_service(self) -> HMSService:
        if self._hms_service is None:
            self._hms_service = await HMSService.create(self._auth_lib)
        return self._hms_service

    @property
    async def lock_service(self) -> LockService:
        if self._lock_service is None:
            self._lock_service = LockService(self._auth_lib)
        return self._lock_service

    @property
    async def sensor_service(self) -> SensorService:
        if self._sensor_service is None:
            self._sensor_service = SensorService(self._auth_lib)
        return self._sensor_service
