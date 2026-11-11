=========================
Ansible 0.1 Release Notes
=========================

.. contents:: Topics

v0.1.0
======

Release Summary
---------------

First release of the ``opengear.ng`` collection, providing Ansible modules
for managing Opengear devices.

Tested against Opengear device firmware 25.11.9.

Highlights of this release:

* **Configuration management** - ``config_export`` exports the device
  configuration, ``config_diff`` previews how a provided configuration
  differs from the running one, ``config_import`` merges a configuration
  into the device, and ``config_restore`` restores a previously exported
  configuration.
* **Security** - ``local_password_policy`` manages the expiry and
  complexity policy for local user passwords.
* **Firmware** - ``system_firmware_upgrade`` manages firmware upgrades.
* **Serial ports** - ``ports_config``, ``ports_status``, ``ports_control``,
  ``ports_sessions`` and ``ports_auto_discover`` configure ports, report
  live status, send control actions, manage active sessions and manage
  port auto-discovery.
* **PDUs** - ``pdu_config``, ``pdu_status`` and ``pdu_control`` configure
  connected PDUs, report PDU and outlet status, and send outlet power
  actions.
* **Networking** - ``conns``, ``physifs``, ``static_routes`` and
  ``failover`` manage network connections, physical interfaces, static
  routes and failover behaviour.
* **Users and access** - ``users``, ``groups``, ``auth``,
  ``users_authorized_keys`` and ``system_authorized_keys`` manage users,
  groups, authentication and SSH authorized keys.
* **Services and system** - ``services_config``, ``services_syslog``,
  ``services_snmp_alert_managers``, ``system_config``, ``system_time``,
  ``system_reboot`` and ``system_factory_reset`` manage services and
  general system settings, and reboot or factory reset a device.
* **Facts** - ``facts`` gathers facts from devices.

The ``ports``, ``pdu``, ``services`` and ``system`` areas are split into
smaller, focused modules based on behaviour (for example configuration,
status and control) rather than a single module per area.

New Plugins
-----------

Httpapi
~~~~~~~

- http_api - HttpApi Plugin for Opengear devices

New Modules
-----------

- auth - Manages auth configuration for Opengear devices
- config_diff - Diff device configuration on Opengear devices
- config_export - Export device configuration from Opengear devices
- config_import - Import configuration on Opengear devices
- config_restore - Restore device configuration on Opengear devices
- conns - Manages network connection configuration for Opengear devices
- facts - Gathers facts from Opengear devices
- failover - Manages configuration of failover behavior on Opengear devices
- groups - Manages configuration of groups on Opengear devices
- local_password_policy - Manages the local password policy on Opengear devices
- pdu_config - Manages configuration for PDUs connected to Opengear devices
- pdu_control - Sends power actions to PDU outlets on Opengear devices
- pdu_status - Gathers live status for PDUs and their outlets
- physifs - Manages configuration of physical interfaces on Opengear devices
- ports_auto_discover - Manages Port Auto\-Discovery on Opengear devices
- ports_config - Manages configuration of serial ports on Opengear devices
- ports_control - Sends control actions to serial ports on Opengear devices
- ports_sessions - Manage and inspect active pmshell sessions on serial ports
- ports_status - Gathers live status data for serial ports
- services_config - Manages configuration of singleton services on Opengear devices
- services_snmp_alert_managers - Manages SNMP Alert Manager configuration on Opengear devices
- services_syslog - Manages remote syslog server configuration on Opengear devices
- static_routes - Manages configuration of static routes on Opengear devices
- system_authorized_keys - Manages system\-level SSH authorized keys on Opengear devices
- system_config - Manages general system settings on Opengear devices
- system_factory_reset - Erases the configuration of an Opengear appliance
- system_firmware_upgrade - Manages firmware upgrades on Opengear devices
- system_reboot - Reboots an Opengear appliance
- system_time - Manages the system clock and timezone on Opengear devices
- users - Manages configuration of users on Opengear devices
- users_authorized_keys - Manages configuration of user authorized keys on Opengear devices
