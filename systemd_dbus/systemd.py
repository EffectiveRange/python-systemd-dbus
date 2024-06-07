# Copyright (C) 2024  Ferenc Nandor Janky
# Copyright (C) 2024  Attila Gombos
# Contact: info@effective-range.com
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301
# USA
from typing import Optional, Any

import dbus
from context_logger import get_logger
from dbus import SystemBus, DBusException, Interface

log = get_logger('SystemdDbus')


class Systemd(object):

    def subscribe_to_property_changes(self) -> bool:
        raise NotImplementedError()

    def unsubscribe_from_property_changes(self) -> bool:
        raise NotImplementedError()

    def add_property_change_handler(self, service_path: str, event_handler: Any) -> bool:
        raise NotImplementedError()

    def start_service(self, service_name: str, mode: Optional[str] = None) -> bool:
        raise NotImplementedError()

    def stop_service(self, service_name: str, mode: Optional[str] = None) -> bool:
        raise NotImplementedError()

    def restart_service(self, service_name: str, mode: Optional[str] = None) -> bool:
        raise NotImplementedError()

    def reload_service(self, service_name: str, mode: Optional[str] = None) -> bool:
        raise NotImplementedError()

    def enable_service(self, service_name: str) -> bool:
        raise NotImplementedError()

    def disable_service(self, service_name: str) -> bool:
        raise NotImplementedError()

    def mask_service(self, service_name: str) -> bool:
        raise NotImplementedError()

    def unmask_service(self, service_name: str) -> bool:
        raise NotImplementedError()

    def is_active(self, service_name: str) -> bool:
        raise NotImplementedError()

    def is_failed(self, service_name: str) -> bool:
        raise NotImplementedError()

    def is_enabled(self, service_name: str) -> bool:
        raise NotImplementedError()

    def is_masked(self, service_name: str) -> bool:
        raise NotImplementedError()

    def is_installed(self, service_name: str) -> bool:
        raise NotImplementedError()

    def get_active_state(self, service_name: str) -> Optional[str]:
        raise NotImplementedError()

    def get_error_code(self, service_name: str) -> Optional[int]:
        raise NotImplementedError()

    def get_service_file_state(self, service_name: str) -> Any:
        raise NotImplementedError()

    def get_service_properties(self, service_name: str) -> Any:
        raise NotImplementedError()

    def get_service_file_properties(self, service_name: str) -> Any:
        raise NotImplementedError()

    def reload_daemon(self) -> bool:
        raise NotImplementedError()


class SystemdDbus(Systemd):
    SYSTEMD_BUS_NAME = 'org.freedesktop.systemd1'
    SYSTEMD_OBJECT_PATH = '/org/freedesktop/systemd1'
    SYSTEMD_MANAGER_INTERFACE = f'{SYSTEMD_BUS_NAME}.Manager'
    SYSTEMD_UNIT_INTERFACE = f'{SYSTEMD_BUS_NAME}.Unit'
    SYSTEMD_SERVICE_INTERFACE = f'{SYSTEMD_BUS_NAME}.Service'
    DBUS_PROPERTIES_INTERFACE = 'org.freedesktop.DBus.Properties'

    def __init__(self, system_bus: SystemBus = SystemBus()) -> None:
        self._system_bus = system_bus

    def __enter__(self) -> 'SystemdDbus':
        self.subscribe_to_property_changes()
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        self.unsubscribe_from_property_changes()

    def subscribe_to_property_changes(self) -> bool:
        try:
            self._get_interface().Subscribe()
            return True
        except DBusException as error:
            log.error('Failed to subscribe to state changes', reason=error)
            return False

    def unsubscribe_from_property_changes(self) -> bool:
        try:
            self._get_interface().Unsubscribe()
            return True
        except DBusException as error:
            log.error('Failed to unsubscribe from state changes', reason=error)
            return False

    def add_property_change_handler(self, service_path: str, handler: Any) -> bool:
        try:
            self._system_bus.add_signal_receiver(handler, 'PropertiesChanged',
                                                 self.DBUS_PROPERTIES_INTERFACE, path=service_path)
            log.debug('Added property change handler', service_path=service_path)
            return True
        except DBusException as error:
            log.error('Failed to add property change handler', service_path=service_path, reason=error)
            return False

    def start_service(self, service_name: str, mode: Optional[str] = None) -> bool:
        return self._service_operation('start', service_name, mode)

    def stop_service(self, service_name: str, mode: Optional[str] = None) -> bool:
        return self._service_operation('stop', service_name, mode)

    def restart_service(self, service_name: str, mode: Optional[str] = None) -> bool:
        return self._service_operation('restart', service_name, mode)

    def reload_service(self, service_name: str, mode: Optional[str] = None) -> bool:
        return self._service_operation('reload-or-restart', service_name, mode)

    def enable_service(self, service_name: str) -> bool:
        return self._service_file_operation('enable', [dbus.Boolean(False), dbus.Boolean(True)], service_name)

    def disable_service(self, service_name: str) -> bool:
        return self._service_file_operation('disable', [dbus.Boolean(False)], service_name)

    def mask_service(self, service_name: str) -> bool:
        return self._service_file_operation('mask', [dbus.Boolean(False), dbus.Boolean(True)], service_name)

    def unmask_service(self, service_name: str) -> bool:
        return self._service_file_operation('unmask', [dbus.Boolean(False)], service_name)

    def is_active(self, service_name: str) -> bool:
        service_state = self.get_active_state(service_name)
        return service_state == 'active'

    def is_failed(self, service_name: str) -> bool:
        service_state = self.get_active_state(service_name)
        return service_state == 'failed'

    def is_enabled(self, service_name: str) -> bool:
        service_file_state = self.get_service_file_state(service_name)
        return service_file_state in ['enabled', 'static']

    def is_masked(self, service_name: str) -> bool:
        service_file_state = self.get_service_file_state(service_name)
        return service_file_state == 'masked'

    def is_installed(self, service_name: str) -> bool:
        load_state = str(self.get_service_file_properties(service_name).get('LoadState', 'not-found'))
        return load_state != 'not-found'

    def get_active_state(self, service_name: str) -> Optional[str]:
        service_name = self._postfix_service_name(service_name)
        properties = self._get_service_properties(service_name, self.SYSTEMD_UNIT_INTERFACE)

        try:
            return str(properties['ActiveState'])
        except Exception as error:
            log.error('Failed to get active state', service=service_name, reason=error)
            return None

    def get_error_code(self, service_name: str) -> Optional[int]:
        service_name = self._postfix_service_name(service_name)
        properties = self._get_service_properties(service_name, self.SYSTEMD_SERVICE_INTERFACE)

        try:
            return int(properties['ExecMainStatus'])
        except Exception as error:
            log.error('Failed to get error code', service=service_name, reason=error)
            return None

    def get_service_file_state(self, service_name: str) -> Optional[str]:
        try:
            service_name = self._postfix_service_name(service_name)
            interface = self._get_interface()
            state = interface.GetUnitFileState(service_name)
            return str(state)
        except DBusException as error:
            log.error('Failed to get service file state', service=service_name, reason=error)
            return None

    def get_service_properties(self, service_name: str) -> Any:
        return self._get_service_properties(service_name, self.SYSTEMD_SERVICE_INTERFACE)

    def get_service_file_properties(self, service_name: str) -> Any:
        return self._get_service_properties(service_name, self.SYSTEMD_UNIT_INTERFACE)

    def reload_daemon(self) -> bool:
        method = 'Reload'

        try:
            interface = self._get_interface()
            getattr(interface, method)()
            return True
        except DBusException as error:
            log.error('Failed to reload systemd daemon', method=method, reason=error)
        return False

    def _service_operation(self, operation: str, service_name: str, mode: Optional[str]) -> bool:
        try:
            service_name = self._postfix_service_name(service_name)
            interface = self._get_interface()
            method = f'{self._convert_operation(operation)}Unit'
            if mode is None:
                mode = 'replace'
            getattr(interface, method)(service_name, mode)
            return True
        except DBusException as error:
            log.error(f'Failed to {operation} service',
                      operation=operation, service=service_name, mode=mode, reason=error)
            return False

    def _service_file_operation(self, operation: str, args: list[Any], service_name: str) -> bool:
        try:
            service_name = self._postfix_service_name(service_name)
            interface = self._get_interface()
            method = f'{self._convert_operation(operation)}UnitFiles'
            getattr(interface, method)([service_name], *args)
            return True
        except DBusException as error:
            log.error(f'Failed to {operation} service file',
                      operation=operation, service=service_name, reason=error)
            return False

    def _get_service_properties(self, service_name: str, service_interface: str) -> Any:
        try:
            service_name = self._postfix_service_name(service_name)
            interface = self._get_interface()
            unit_path = interface.LoadUnit(service_name)
            proxy_object = self._system_bus.get_object(self.SYSTEMD_BUS_NAME, unit_path)
            properties = Interface(proxy_object, self.DBUS_PROPERTIES_INTERFACE)
            return properties.GetAll(service_interface)
        except DBusException as error:
            log.error('Failed to get service properties',
                      service=service_name, interface=service_interface, reason=error)
            return None

    def _get_interface(self) -> Interface:
        proxy_object = self._system_bus.get_object(self.SYSTEMD_BUS_NAME, self.SYSTEMD_OBJECT_PATH)
        return Interface(proxy_object, self.SYSTEMD_MANAGER_INTERFACE)

    def _postfix_service_name(self, service_name: str) -> str:
        if not service_name.endswith('.service'):
            return f'{service_name}.service'
        return service_name

    def _convert_operation(self, operation: str) -> str:
        if '-' in operation:
            return ''.join(word.capitalize() for word in operation.split('-'))
        else:
            return operation.capitalize()
