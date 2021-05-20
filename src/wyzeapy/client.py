#  Copyright (c) 2021. Mulliken, LLC - All Rights Reserved
#  You may use, distribute and modify this code under the terms
#  of the attached license. You should have received a copy of
#  the license with this file. If not, please write to:
#  joshua@mulliken.net to receive a copy

import re

from typing import List, Any
from .base_client import BaseClient, Device, DeviceTypes, ActionNotSupported, PropertyIDs, Group, EventTypes


class File:
    file_id: str
    type: Any
    url: str
    status: int
    en_algorithm: int
    en_password: str
    is_ai: int
    ai_tag_list: List
    ai_url: str
    file_params: dict

    def __init__(self, dictionary):
        for k, v in dictionary.items():
            setattr(self, k, v)

        if self.type == 1:
            self.type = "Image"
        else:
            self.type = "Video"

    def __repr__(self):
        return "<File: {}, {}>".format(self.file_id, self.type)


class Event:
    event_id: str
    device_mac: str
    device_model: str
    event_category: int
    event_value: str
    event_ts: int
    event_ack_result: int
    is_feedback_correct: int
    is_feedback_face: int
    is_feedback_person: int
    file_list: List[File]
    event_params: dict
    recognized_instance_list: List
    tag_list: List
    read_state: int

    def __init__(self, dictionary):
        for k, v in dictionary.items():
            setattr(self, k, v)
        temp_file_list = []
        if len(self.file_list) > 0:
            for file in self.file_list:
                temp_file_list.append(File(file))
        self.file_list = temp_file_list

    def __repr__(self):
        return "<Event: {}, {}>".format(self.event_id, self.event_ts)


class Client:
    def __init__(self, email, password):
        self.email = email
        self.password = password

        self.client = BaseClient()
        self.client.login(self.email, self.password)

    def reauthenticate(self):
        self.client.login(self.email, self.password)

    @staticmethod
    def create_pid_pair(pid_enum: PropertyIDs, value):
        return {"pid": pid_enum.value, "pvalue": value}

    def get_devices(self):
        object_list = self.client.get_object_list()

        devices = []
        for device in object_list['data']['device_list']:
            devices.append(Device(device))

        return devices

    def get_groups(self):
        object_list = self.client.get_auto_group_list()

        groups = []
        for group in object_list['data']['auto_group_list']:
            groups.append(Group(group))

        return groups

    def activate_group(self, group: Group):
            self.client.auto_group_run(group)

    def turn_on(self, device: Device, extra_pids=None):
        device_type: DeviceTypes = DeviceTypes(device.product_type)

        if device_type in [
            DeviceTypes.PLUG,
            DeviceTypes.OUTDOOR_PLUG
        ]:
            self.client.set_property(device, PropertyIDs.ON.value, "1")
        elif device_type in [
            DeviceTypes.LIGHT
        ]:
            plist = [
                self.create_pid_pair(PropertyIDs.ON, "1")
            ]
            if extra_pids is not None:
                plist.extend(extra_pids)

            self.client.set_property_list(device, plist)
        elif device_type in [
            DeviceTypes.MESH_LIGHT
        ]:
            plist = [
                self.create_pid_pair(PropertyIDs.ON, "1")
            ]
            if extra_pids is not None:
                plist.extend(extra_pids)

            self.client.run_action_list(device, plist)
        elif device_type in [
            DeviceTypes.LOCK
        ]:
            self.client.lock_control(device, "remoteLock")
        elif device_type in [
            DeviceTypes.CAMERA
        ]:
            self.client.run_action(device, "power_on")
        else:
            raise ActionNotSupported(device_type.value)

    def turn_off(self, device: Device, extra_pids=None):
        device_type: DeviceTypes = DeviceTypes(device.product_type)

        if device_type in [
            DeviceTypes.PLUG,
            DeviceTypes.OUTDOOR_PLUG
        ]:
            self.client.set_property(device, PropertyIDs.ON.value, "0")
        elif device_type in [
            DeviceTypes.LIGHT
        ]:
            plist = [
                self.create_pid_pair(PropertyIDs.ON, "0")
            ]
            if extra_pids is not None:
                plist.extend(extra_pids)

            self.client.set_property_list(device, plist)
        elif device_type in [
            DeviceTypes.MESH_LIGHT
        ]:
            plist = [
                self.create_pid_pair(PropertyIDs.ON, "0")
            ]
            if extra_pids is not None:
                plist.extend(extra_pids)

            self.client.run_action_list(device, plist)
        elif device_type in [
            DeviceTypes.LOCK
        ]:
            self.client.lock_control(device, "remoteUnlock")
        elif device_type in [
            DeviceTypes.CAMERA
        ]:
            self.client.run_action(device, "power_off")
        else:
            raise ActionNotSupported(device_type.value)

    def notifications_on(self, device: Device, notification: PropertyIDs):
        if DeviceTypes(device.product_type) not in [
            DeviceTypes.CAMERA
        ]:
            raise ActionNotSupported(device.product_type)

        plist = [
            self.create_pid_pair(notification, "1")
        ]
        self.client.set_property_list(device, plist)

    def notifications_off(self, device: Device, notification: PropertyIDs):
        if DeviceTypes(device.product_type) not in [
            DeviceTypes.CAMERA
        ]:
            raise ActionNotSupported(device.product_type)

        plist = [
            self.create_pid_pair(notification, "0")
        ]
        self.client.set_property_list(device, plist)

    def set_brightness(self, device: Device, brightness: int):
        if DeviceTypes(device.product_type) not in [
            DeviceTypes.LIGHT,
            DeviceTypes.MESH_LIGHT
        ]:
            raise ActionNotSupported(device.product_type)

        if brightness > 100 or brightness < 0:
            raise AttributeError("Value must be between 0 and 100")

        self.turn_on(device, extra_pids=[
            self.create_pid_pair(PropertyIDs.BRIGHTNESS, str(brightness))
        ])

    def set_color(self, device, rgb_hex_string):
        if DeviceTypes(device.product_type) not in [
            DeviceTypes.MESH_LIGHT
        ]:
            raise ActionNotSupported(device.product_type)

        if len(rgb_hex_string) != 6 or bool(re.compile(r'[^A-F0-9]').search(rgb_hex_string)):
            raise AttributeError("Value must be a valid hex string in the format: 000000-FFFFFF")

        self.turn_on(device, extra_pids=[
            self.create_pid_pair(PropertyIDs.COLOR, rgb_hex_string)
        ])

    def get_info(self, device):
        properties = self.client.get_property_list(device)['data']['property_list']

        property_list = []
        for property in properties:
            try:
                property_id = PropertyIDs(property['pid'])
                property_list.append((
                    property_id,
                    property['value']
                ))
            except ValueError:
                pass

        return property_list

    def get_events(self, device, requested_event_type: EventTypes = EventTypes.MOTION):
        raw_events = self.client.get_event_list(device, 10, requested_event_type)

        events = []
        if len(raw_events) > 0:
            for raw_event in raw_events:
                event = Event(raw_event)
                events.append(event)

        return events

    def get_latest_event(self, device, requested_event_type: EventTypes = EventTypes.MOTION):
        raw_events = self.client.get_event_list(device, 10, requested_event_type)
        if len(raw_events) > 0:
            return Event(raw_events[0])

        return None
