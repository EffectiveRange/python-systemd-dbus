import unittest
from unittest import TestCase
from unittest.mock import MagicMock

import dbus
from context_logger import setup_logging
from dbus import DBusException

from systemd_dbus import SystemdDbus


class SystemdDbusTest(TestCase):

    @classmethod
    def setUpClass(cls):
        setup_logging('systemd-dbus', warn_on_overwrite=False)

    def setUp(self):
        print()

    def test_context_handling(self):
        # Given
        system_bus = MagicMock(spec=dbus.SystemBus)
        handler = MagicMock()

        # When
        with SystemdDbus(system_bus) as systemd:
            systemd.add_property_change_handler('/path/to/unit', handler)

            # Then
            system_bus.get_object.assert_called_with('org.freedesktop.systemd1', '/org/freedesktop/systemd1')
            system_bus.get_object().get_dbus_method.assert_called_with('Subscribe', 'org.freedesktop.systemd1.Manager')

        system_bus.get_object.assert_called_with('org.freedesktop.systemd1', '/org/freedesktop/systemd1')
        system_bus.get_object().get_dbus_method.assert_called_with('Unsubscribe', 'org.freedesktop.systemd1.Manager')

    def test_returns_true_when_subscribed_to_property_changes(self):
        # Given
        system_bus = MagicMock(spec=dbus.SystemBus)
        systemd = SystemdDbus(system_bus)

        # When
        result = systemd.subscribe_to_property_changes()

        # Then
        self.assertTrue(result)
        system_bus.get_object.assert_called_with('org.freedesktop.systemd1', '/org/freedesktop/systemd1')
        system_bus.get_object().get_dbus_method.assert_called_with('Subscribe', 'org.freedesktop.systemd1.Manager')

    def test_returns_false_when_subscribe_to_property_changes_fails(self):
        # Given
        system_bus = MagicMock(spec=dbus.SystemBus)
        system_bus.get_object().get_dbus_method.side_effect = DBusException('Failure')
        systemd = SystemdDbus(system_bus)

        # When
        result = systemd.subscribe_to_property_changes()

        # Then
        self.assertFalse(result)
        system_bus.get_object.assert_called_with('org.freedesktop.systemd1', '/org/freedesktop/systemd1')
        system_bus.get_object().get_dbus_method.assert_called_with('Subscribe', 'org.freedesktop.systemd1.Manager')

    def test_returns_true_when_unsubscribed_from_property_changes(self):
        # Given
        system_bus = MagicMock(spec=dbus.SystemBus)
        systemd = SystemdDbus(system_bus)

        # When
        result = systemd.unsubscribe_from_property_changes()

        # Then
        self.assertTrue(result)
        system_bus.get_object.assert_called_with('org.freedesktop.systemd1', '/org/freedesktop/systemd1')
        system_bus.get_object().get_dbus_method.assert_called_with('Unsubscribe', 'org.freedesktop.systemd1.Manager')

    def test_returns_false_when_unsubscribe_from_property_changes_fails(self):
        # Given
        system_bus = MagicMock(spec=dbus.SystemBus)
        system_bus.get_object().get_dbus_method.side_effect = DBusException('Failure')
        systemd = SystemdDbus(system_bus)

        # When
        result = systemd.unsubscribe_from_property_changes()

        # Then
        self.assertFalse(result)
        system_bus.get_object.assert_called_with('org.freedesktop.systemd1', '/org/freedesktop/systemd1')
        system_bus.get_object().get_dbus_method.assert_called_with('Unsubscribe', 'org.freedesktop.systemd1.Manager')

    def test_returns_true_when_property_change_handler_is_added(self):
        # Given
        system_bus = MagicMock(spec=dbus.SystemBus)
        systemd = SystemdDbus(system_bus)
        handler = MagicMock()

        # When
        result = systemd.add_property_change_handler('/path/to/unit', handler)

        # Then
        self.assertTrue(result)
        system_bus.add_signal_receiver.assert_called_with(
            handler, 'PropertiesChanged', 'org.freedesktop.DBus.Properties', path='/path/to/unit')

    def test_returns_false_when_add_property_change_handler(self):
        # Given
        system_bus = MagicMock(spec=dbus.SystemBus)
        system_bus.add_signal_receiver.side_effect = DBusException('Failure')
        systemd = SystemdDbus(system_bus)
        handler = MagicMock()

        # When
        result = systemd.add_property_change_handler('/path/to/unit', handler)

        # Then
        self.assertFalse(result)
        system_bus.add_signal_receiver.assert_called_with(
            handler, 'PropertiesChanged', 'org.freedesktop.DBus.Properties', path='/path/to/unit')

    def test_returns_true_when_service_is_started_successfully(self):
        # Given
        system_bus = MagicMock(spec=dbus.SystemBus)
        systemd = SystemdDbus(system_bus)

        # When
        result = systemd.start_service('test')

        # Then
        self.assertTrue(result)
        system_bus.get_object.assert_called_with('org.freedesktop.systemd1', '/org/freedesktop/systemd1')
        system_bus.get_object().get_dbus_method.assert_called_with('StartUnit', 'org.freedesktop.systemd1.Manager')
        system_bus.get_object().get_dbus_method().assert_called_with('test.service', 'replace')

    def test_returns_true_when_service_is_stopped_successfully(self):
        # Given
        system_bus = MagicMock(spec=dbus.SystemBus)
        systemd = SystemdDbus(system_bus)

        # When
        result = systemd.stop_service('test', 'isolate')

        # Then
        self.assertTrue(result)
        system_bus.get_object.assert_called_with('org.freedesktop.systemd1', '/org/freedesktop/systemd1')
        system_bus.get_object().get_dbus_method.assert_called_with('StopUnit', 'org.freedesktop.systemd1.Manager')
        system_bus.get_object().get_dbus_method().assert_called_with('test.service', 'isolate')

    def test_returns_false_when_failed_to_restart_service(self):
        # Given
        system_bus = MagicMock(spec=dbus.SystemBus)
        system_bus.get_object().get_dbus_method.side_effect = DBusException('Failure')
        systemd = SystemdDbus(system_bus)

        # When
        result = systemd.restart_service('test.service')

        # Then
        self.assertFalse(result)
        system_bus.get_object.assert_called_with('org.freedesktop.systemd1', '/org/freedesktop/systemd1')
        system_bus.get_object().get_dbus_method.assert_called_with('RestartUnit', 'org.freedesktop.systemd1.Manager')

    def test_returns_true_when_reloaded_service_successfully(self):
        # Given
        system_bus = MagicMock(spec=dbus.SystemBus)
        systemd = SystemdDbus(system_bus)

        # When
        result = systemd.reload_service('test.service')

        # Then
        self.assertTrue(result)
        system_bus.get_object.assert_called_with('org.freedesktop.systemd1', '/org/freedesktop/systemd1')
        system_bus.get_object().get_dbus_method.assert_called_with('ReloadOrRestartUnit',
                                                                   'org.freedesktop.systemd1.Manager')
        system_bus.get_object().get_dbus_method().assert_called_with('test.service', 'replace')

    def test_returns_true_when_service_is_enabled_successfully(self):
        # Given
        system_bus = MagicMock(spec=dbus.SystemBus)
        systemd = SystemdDbus(system_bus)

        # When
        result = systemd.enable_service('test')

        # Then
        self.assertTrue(result)
        system_bus.get_object.assert_called_with('org.freedesktop.systemd1', '/org/freedesktop/systemd1')
        system_bus.get_object().get_dbus_method(
            'EnableUnitFiles', 'org.freedesktop.systemd1.Manager').assert_called_with(
            ['test.service'], dbus.Boolean(False), dbus.Boolean(True))

    def test_returns_false_when_failed_to_disable_service(self):
        # Given
        system_bus = MagicMock(spec=dbus.SystemBus)
        system_bus.get_object().get_dbus_method.side_effect = DBusException('Failure')
        systemd = SystemdDbus(system_bus)

        # When
        result = systemd.disable_service('test.service')

        # Then
        self.assertFalse(result)
        system_bus.get_object.assert_called_with('org.freedesktop.systemd1', '/org/freedesktop/systemd1')
        system_bus.get_object().get_dbus_method.assert_called_with(
            'DisableUnitFiles', 'org.freedesktop.systemd1.Manager')

    def test_returns_false_when_failed_to_mask_service(self):
        # Given
        system_bus = MagicMock(spec=dbus.SystemBus)
        system_bus.get_object().get_dbus_method.side_effect = DBusException('Failure')
        systemd = SystemdDbus(system_bus)

        # When
        result = systemd.mask_service('test.service')

        # Then
        self.assertFalse(result)
        system_bus.get_object.assert_called_with('org.freedesktop.systemd1', '/org/freedesktop/systemd1')
        system_bus.get_object().get_dbus_method.assert_called_with(
            'MaskUnitFiles', 'org.freedesktop.systemd1.Manager')

    def test_returns_true_when_service_is_unmasked_successfully(self):
        # Given
        system_bus = MagicMock(spec=dbus.SystemBus)
        systemd = SystemdDbus(system_bus)

        # When
        result = systemd.unmask_service('test')

        # Then
        self.assertTrue(result)
        system_bus.get_object.assert_called_with('org.freedesktop.systemd1', '/org/freedesktop/systemd1')
        system_bus.get_object().get_dbus_method(
            'UnmaskUnitFiles', 'org.freedesktop.systemd1.Manager').assert_called_with(
            ['test.service'], dbus.Boolean(False))

    def test_returns_true_when_service_is_active(self):
        # Given
        system_bus = MagicMock(spec=dbus.SystemBus)
        system_bus.get_object().get_dbus_method().return_value = {'ActiveState': 'active'}
        systemd = SystemdDbus(system_bus)

        # When
        result = systemd.is_active('test')

        # Then
        self.assertTrue(result)
        system_bus.get_object().get_dbus_method.assert_called_with('GetAll', 'org.freedesktop.DBus.Properties')
        system_bus.get_object().get_dbus_method().assert_called_with('org.freedesktop.systemd1.Unit')

    def test_returns_true_when_service_is_failed(self):
        # Given
        system_bus = MagicMock(spec=dbus.SystemBus)
        system_bus.get_object().get_dbus_method().return_value = {'ActiveState': 'failed'}
        systemd = SystemdDbus(system_bus)

        # When
        result = systemd.is_failed('test.service')

        # Then
        self.assertTrue(result)
        system_bus.get_object().get_dbus_method.assert_called_with('GetAll', 'org.freedesktop.DBus.Properties')
        system_bus.get_object().get_dbus_method().assert_called_with('org.freedesktop.systemd1.Unit')

    def test_returns_false_when_tries_to_get_is_active_but_no_properties(self):
        # Given
        system_bus = MagicMock(spec=dbus.SystemBus)
        system_bus.get_object().get_dbus_method().return_value = None
        systemd = SystemdDbus(system_bus)

        # When
        result = systemd.is_active('test')

        # Then
        self.assertFalse(result)
        system_bus.get_object().get_dbus_method.assert_called_with('GetAll', 'org.freedesktop.DBus.Properties')
        system_bus.get_object().get_dbus_method().assert_called_with('org.freedesktop.systemd1.Unit')

    def test_returns_false_when_tries_to_get_is_failed_but_fails_to_get_properties(self):
        # Given
        system_bus = MagicMock(spec=dbus.SystemBus)
        system_bus.get_object().get_dbus_method().side_effect = DBusException('Failure')
        systemd = SystemdDbus(system_bus)

        # When
        result = systemd.is_failed('test.service')

        # Then
        self.assertFalse(result)
        system_bus.get_object().get_dbus_method.assert_called_with('LoadUnit', 'org.freedesktop.systemd1.Manager')
        system_bus.get_object().get_dbus_method().assert_called_with('test.service')

    def test_returns_true_when_service_is_enabled(self):
        # Given
        system_bus = MagicMock(spec=dbus.SystemBus)
        system_bus.get_object().get_dbus_method().return_value = 'enabled'
        systemd = SystemdDbus(system_bus)

        # When
        result = systemd.is_enabled('test')

        # Then
        self.assertTrue(result)
        system_bus.get_object().get_dbus_method.assert_called_with('GetUnitFileState',
                                                                   'org.freedesktop.systemd1.Manager')
        system_bus.get_object().get_dbus_method().assert_called_with('test.service')

    def test_returns_true_when_service_is_statically_enabled(self):
        # Given
        system_bus = MagicMock(spec=dbus.SystemBus)
        system_bus.get_object().get_dbus_method().return_value = 'static'
        systemd = SystemdDbus(system_bus)

        # When
        result = systemd.is_enabled('test')

        # Then
        self.assertTrue(result)
        system_bus.get_object().get_dbus_method.assert_called_with('GetUnitFileState',
                                                                   'org.freedesktop.systemd1.Manager')
        system_bus.get_object().get_dbus_method().assert_called_with('test.service')

    def test_returns_false_when_service_is_disabled(self):
        # Given
        system_bus = MagicMock(spec=dbus.SystemBus)
        system_bus.get_object().get_dbus_method().return_value = 'disabled'
        systemd = SystemdDbus(system_bus)

        # When
        result = systemd.is_enabled('test')

        # Then
        self.assertFalse(result)
        system_bus.get_object().get_dbus_method.assert_called_with('GetUnitFileState',
                                                                   'org.freedesktop.systemd1.Manager')
        system_bus.get_object().get_dbus_method().assert_called_with('test.service')

    def test_returns_true_when_service_is_masked(self):
        # Given
        system_bus = MagicMock(spec=dbus.SystemBus)
        system_bus.get_object().get_dbus_method().return_value = 'masked'
        systemd = SystemdDbus(system_bus)

        # When
        result = systemd.is_masked('test')

        # Then
        self.assertTrue(result)
        system_bus.get_object().get_dbus_method.assert_called_with('GetUnitFileState',
                                                                   'org.freedesktop.systemd1.Manager')
        system_bus.get_object().get_dbus_method().assert_called_with('test.service')

    def test_returns_false_when_service_is_not_masked(self):
        # Given
        system_bus = MagicMock(spec=dbus.SystemBus)
        system_bus.get_object().get_dbus_method().return_value = 'disabled'
        systemd = SystemdDbus(system_bus)

        # When
        result = systemd.is_masked('test')

        # Then
        self.assertFalse(result)
        system_bus.get_object().get_dbus_method.assert_called_with('GetUnitFileState',
                                                                   'org.freedesktop.systemd1.Manager')
        system_bus.get_object().get_dbus_method().assert_called_with('test.service')

    def test_returns_true_when_service_is_installed(self):
        # Given
        system_bus = MagicMock(spec=dbus.SystemBus)
        system_bus.get_object().get_dbus_method().return_value = {'LoadState': 'loaded'}
        systemd = SystemdDbus(system_bus)

        # When
        result = systemd.is_installed('test')

        # Then
        self.assertTrue(result)
        system_bus.get_object().get_dbus_method.assert_called_with('GetAll', 'org.freedesktop.DBus.Properties')
        system_bus.get_object().get_dbus_method().assert_called_with('org.freedesktop.systemd1.Unit')

    def test_returns_false_when_service_is_not_installed(self):
        # Given
        system_bus = MagicMock(spec=dbus.SystemBus)
        system_bus.get_object().get_dbus_method().return_value = {'LoadState': 'not-found'}
        systemd = SystemdDbus(system_bus)

        # When
        result = systemd.is_installed('test')

        # Then
        self.assertFalse(result)
        system_bus.get_object().get_dbus_method.assert_called_with('GetAll', 'org.freedesktop.DBus.Properties')
        system_bus.get_object().get_dbus_method().assert_called_with('org.freedesktop.systemd1.Unit')

    def test_returns_error_code(self):
        # Given
        system_bus = MagicMock(spec=dbus.SystemBus)
        system_bus.get_object().get_dbus_method().return_value = {'ExecMainStatus': '123'}
        systemd = SystemdDbus(system_bus)

        # When
        result = systemd.get_error_code('test')

        # Then
        self.assertEqual(123, result)
        system_bus.get_object().get_dbus_method.assert_called_with('GetAll', 'org.freedesktop.DBus.Properties')
        system_bus.get_object().get_dbus_method().assert_called_with('org.freedesktop.systemd1.Service')

    def test_returns_none_when_tries_to_get_error_code_but_no_properties(self):
        # Given
        system_bus = MagicMock(spec=dbus.SystemBus)
        system_bus.get_object().get_dbus_method().return_value = None
        systemd = SystemdDbus(system_bus)

        # When
        result = systemd.get_error_code('test.service')

        # Then
        self.assertFalse(result)
        system_bus.get_object().get_dbus_method.assert_called_with('GetAll', 'org.freedesktop.DBus.Properties')
        system_bus.get_object().get_dbus_method().assert_called_with('org.freedesktop.systemd1.Service')

    def test_returns_none_when_tries_to_get_error_code_but_fails_to_get_properties(self):
        # Given
        system_bus = MagicMock(spec=dbus.SystemBus)
        system_bus.get_object().get_dbus_method().side_effect = DBusException('Failure')
        systemd = SystemdDbus(system_bus)

        # When
        result = systemd.get_error_code('test')

        # Then
        self.assertFalse(result)
        system_bus.get_object().get_dbus_method.assert_called_with('LoadUnit', 'org.freedesktop.systemd1.Manager')
        system_bus.get_object().get_dbus_method().assert_called_with('test.service')

    def test_returns_unit_file_state(self):
        # Given
        system_bus = MagicMock(spec=dbus.SystemBus)
        system_bus.get_object().get_dbus_method().return_value = 'enabled'
        systemd = SystemdDbus(system_bus)

        # When
        result = systemd.get_service_file_state('test.service')

        # Then
        self.assertEqual('enabled', result)
        system_bus.get_object().get_dbus_method.assert_called_with(
            'GetUnitFileState', 'org.freedesktop.systemd1.Manager')
        system_bus.get_object().get_dbus_method().assert_called_with('test.service')

    def test_returns_none_when_fails_to_get_service_file_state(self):
        # Given
        system_bus = MagicMock(spec=dbus.SystemBus)
        system_bus.get_object().get_dbus_method().side_effect = DBusException('Failure')
        systemd = SystemdDbus(system_bus)

        # When
        result = systemd.get_service_file_state('test')

        # Then
        self.assertIsNone(result)
        system_bus.get_object().get_dbus_method.assert_called_with(
            'GetUnitFileState', 'org.freedesktop.systemd1.Manager')
        system_bus.get_object().get_dbus_method().assert_called_with('test.service')

    def test_returns_service_properties(self):
        # Given
        system_bus = MagicMock(spec=dbus.SystemBus)
        system_bus.get_object().get_dbus_method().return_value = {'ExecMainStatus': '123'}
        systemd = SystemdDbus(system_bus)

        # When
        result = systemd.get_service_properties('test.service')

        # Then
        self.assertEqual({'ExecMainStatus': '123'}, result)
        system_bus.get_object().get_dbus_method.assert_called_with('GetAll', 'org.freedesktop.DBus.Properties')
        system_bus.get_object().get_dbus_method().assert_called_with('org.freedesktop.systemd1.Service')

    def test_returns_service_file_properties(self):
        # Given
        system_bus = MagicMock(spec=dbus.SystemBus)
        system_bus.get_object().get_dbus_method().return_value = {'ActiveState': 'active'}
        systemd = SystemdDbus(system_bus)

        # When
        result = systemd.get_service_file_properties('test')

        # Then
        self.assertEqual({'ActiveState': 'active'}, result)
        system_bus.get_object().get_dbus_method.assert_called_with('GetAll', 'org.freedesktop.DBus.Properties')
        system_bus.get_object().get_dbus_method().assert_called_with('org.freedesktop.systemd1.Unit')

    def test_returns_true_when_systemd_daemon_is_reloaded(self):
        # Given
        system_bus = MagicMock(spec=dbus.SystemBus)
        systemd = SystemdDbus(system_bus)

        # When
        result = systemd.reload_daemon()

        # Then
        self.assertTrue(result)
        system_bus.get_object.assert_called_with('org.freedesktop.systemd1', '/org/freedesktop/systemd1')
        system_bus.get_object().get_dbus_method.assert_called_with('Reload', 'org.freedesktop.systemd1.Manager')
        system_bus.get_object().get_dbus_method().assert_called()

    def test_returns_false_when_failed_to_reload_systemd_daemon(self):
        # Given
        system_bus = MagicMock(spec=dbus.SystemBus)
        system_bus.get_object().get_dbus_method.side_effect = DBusException('Failure')
        systemd = SystemdDbus(system_bus)

        # When
        result = systemd.reload_daemon()

        # Then
        self.assertFalse(result)
        system_bus.get_object.assert_called_with('org.freedesktop.systemd1', '/org/freedesktop/systemd1')
        system_bus.get_object().get_dbus_method.assert_called_with('Reload', 'org.freedesktop.systemd1.Manager')


if __name__ == "__main__":
    unittest.main()
