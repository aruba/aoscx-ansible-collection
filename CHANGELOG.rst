=================================
Arubanetworks.Aoscx Release Notes
=================================

.. contents:: Topics


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
