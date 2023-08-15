=================================
Arubanetworks.Aoscx Release Notes
=================================

.. contents:: Topics


v4.3.0
======

Release Summary
---------------

New features (LAG and DNS), enhancements (VLAN) and bugfixes

Major Changes
-------------

- Add enhancements for VLAN module by Alexis La Goutte (https://github.com/aruba/aoscx-ansible-collection/pull/60)
- Add new modules for LAG (aoscx_lag_interface) and DNS (aoscx_dns)
- Include fixes for issues found internally.

Minor Changes
-------------

- Fix Facts Ansible module. The ``gather_subset`` choices ``management_interface`` , ``platform_name``, ``host_name``, ``product_info``, ``software_images`` are working again. (https://github.com/aruba/aoscx-ansible-collection/issues/76)
- Fix aoscx_command module (https://github.com/aruba/aoscx-ansible-collection/issues/70)
- Fix sanity tests errors.
- The ``gather_subsets`` choice ``config`` is not available yet and it will be available in a future release.

v4.2.1
======

Release Summary
---------------

Documentation and bug fixes release

Major Changes
-------------

- Fix errors in documentation.
- Fix module aoscx_facts (failing on 6000 and 6100, also with other platforms when stressing the device).
- Remove legacy code not using the pyaoscx library.

Minor Changes
-------------

- Fix sanity errors for Ansible 2.12.

v4.2.0
======

Release Summary
---------------

New features (port security, PoE, MAC, static MAC and speed/duplex) and bugfixes

Major Changes
-------------

- Add new modules for PoE (aoscx_poe), MAC (aoscx_mac) and Static MAC (aoscx_static_mac)
- Add port security support (aoscx_l2_interface).
- Add speed and duplex support (aoscx_interface).
- Fix module aoscx_upload firmware using HTTP.
- Fix module aoscx_upload_firmware for local path (https://github.com/aruba/aoscx-ansible-collection/issues/28).
- Include fixes for issues found internally.

Minor Changes
-------------

- Fix Interface MTU support (https://github.com/aruba/aoscx-ansible-collection/issues/38).
- Fix idempotency in ACL module.

v4.1.1
======

Release Summary
---------------

Bug fixes release

Major Changes
-------------

- Fix Checkpoint module that was showing 404 error (https://github.com/aruba/aoscx-ansible-collection/issues/33).
- Fix Facts module for 6xxx platforms (https://github.com/aruba/aoscx-ansible-collection/issues/27).
- Fix Github action Ansible-test (https://github.com/aruba/aoscx-ansible-collection/issues/40).
- Fix Static MAC module.
- Fix compatibility issue with Ansible version 2.13 (https://github.com/aruba/aoscx-ansible-collection/issues/39).
- Fix for ACL module, delete ACE.
- Support for anti-CSRF tokens for REST API.
- Update versions in Ansible-test (https://github.com/aruba/aoscx-ansible-collection/issues/35).

Minor Changes
-------------

- Added option to set REST version (10.04, 10.08, 10.09).
- Fix default string value (https://github.com/aruba/aoscx-ansible-collection/issues/42).

v4.1.0
======

Release Summary
---------------

Feature OSPF and bug fixes.

Major Changes
-------------

- Bug fixes.
- Feature not yet supported, Port Security and Speed Duplex.
- New feature supported, OSPFv2 and OSPFv3.
