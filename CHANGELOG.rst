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

- Fix Checkpoint module that was showing 404 error (https://github.com/aruba/aoscx-ansible-collection/issues/33)
- Fix Facts module for 6xxx platforms (https://github.com/aruba/aoscx-ansible-collection/issues/27)
- Fix Static MAC module
- Fix compatibility issue with Ansible version 2.13 (https://github.com/aruba/aoscx-ansible-collection/issues/39)
- Fix for ACL module, delete ACE
- Support for anti-CSRF tokens for REST API

Minor Changes
-------------

- Added option to set REST version (10.04, 10.08, 10.09)

v4.1.0
======

Release Summary
---------------

Feature OSPF and bug fixes

Major Changes
-------------

- Bug fixes
- Feature not yet supported, Port Security and Speed Duplex
- New feature supported, OSPFv2 and OSPFv3
