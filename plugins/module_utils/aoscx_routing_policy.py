# -*- coding: utf-8 -*-

# (C) Copyright 2024 Hewlett Packard Enterprise Development LP.
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
Shared helpers to reference routing policy objects (route maps, prefix
lists, BGP community and AS-path filters) from other resources.

The switch accepts a reference written as an URI string, and returns it
either as an URI string or as a {name: uri} dictionary. References are
therefore compared by name.
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible.module_utils.six.moves.urllib.parse import unquote

COLLECTIONS = {
    "route map": "system/route_maps",
    "prefix list": "system/prefix_lists",
    "community list": "system/bgp_community_filters",
    "AS-path list": "system/bgp_aspath_filters",
    "keychain": "system/keychains",
}


def reference_name(reference):
    """Name of a referenced resource, given as {name: uri} or as an uri."""
    if not reference:
        return None
    if isinstance(reference, dict):
        return next(iter(reference))
    if isinstance(reference, str):
        return unquote(reference.rstrip("/").rsplit("/", 1)[-1])
    # pyaoscx object
    return getattr(reference, "name", None) or getattr(
        reference, "ip_or_ifname_or_group_name", None
    )


def reference_uri(session, kind, name):
    """URI used to reference the object of the given kind and name."""
    return "{0}{1}/{2}".format(
        session.resource_prefix, COLLECTIONS[kind], name
    )


def check_reference(ansible_module, session, kind, name):
    """
    Fail if the referenced object does not exist. Skipped in check mode, as
    the object may be created by a previous task of the playbook.
    """
    if ansible_module.check_mode:
        return
    if "/" in name or name in (".", ".."):
        ansible_module.fail_json(
            msg="Invalid {0} name: {1}".format(kind, name)
        )
    path = "{0}/{1}".format(COLLECTIONS[kind], name)
    response = session.request("GET", path, params={"attributes": "name"})
    if response.status_code == 404:
        ansible_module.fail_json(
            msg="Could not find {0} {1}".format(kind, name)
        )
    if response.status_code != 200:
        ansible_module.fail_json(
            msg="Could not read {0} {1}: {2}".format(kind, name, response.text)
        )
