#!/usr/bin/env python
# -*- coding: utf-8 -*-

# (C) Copyright 2019-2022 Hewlett Packard Enterprise Development LP.
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from random import randint

from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_port import (  # NOQA
    Port,
)
from ansible_collections.arubanetworks.aoscx.plugins.module_utils.vrfs.aoscx_vrf import (  # NOQA
    VRF,
)


def number_unit(s):
    for i, c in enumerate(s):
        if not c.isdigit():
            break
    number = s[:i]
    unit = s[i:].lstrip()
    return number, unit


class Interface:
    def create_interface(
        self, aruba_ansible_module, interface_name, type=None
    ):

        if aruba_ansible_module.switch_platform.startswith("6") and (
            type is None
        ):

            return aruba_ansible_module

        if "Interface" not in aruba_ansible_module.running_config.keys():
            aruba_ansible_module.running_config["Interface"] = {}

        encoded_interface_name = interface_name.replace("/", "%2F")
        if (
            encoded_interface_name
            not in aruba_ansible_module.running_config["Interface"].keys()
        ):

            aruba_ansible_module.running_config["Interface"][
                encoded_interface_name
            ] = {"name": interface_name}

        return aruba_ansible_module

    def check_interface_exists(self, aruba_ansible_module, interface_name):

        if "Interface" not in aruba_ansible_module.running_config.keys():
            return False

        encoded_interface_name = interface_name.replace("/", "%2F")
        if (
            encoded_interface_name
            not in aruba_ansible_module.running_config["Interface"].keys()
        ):
            return False

        return True

    def delete_interface(
        self, aruba_ansible_module, interface_name, type=None
    ):

        if aruba_ansible_module.switch_platform.startswith("6") and (
            type is None
        ):
            if self.check_interface_exists(
                aruba_ansible_module, interface_name
            ):
                encoded_interface_name = interface_name.replace("/", "%2F")
                user_config = {
                    "admin": "down",
                }

                aruba_ansible_module.running_config["Interface"][
                    encoded_interface_name
                ] = {
                    "name": interface_name,
                    "user_config": user_config,
                }

            return aruba_ansible_module

        if self.check_interface_exists(aruba_ansible_module, interface_name):
            encoded_interface_name = interface_name.replace("/", "%2F")
            aruba_ansible_module.running_config["Interface"].pop(
                encoded_interface_name
            )

        return aruba_ansible_module

    def update_interface_fields(
        self, aruba_ansible_module, interface_name, interface_fields
    ):

        if self.check_interface_exists(aruba_ansible_module, interface_name):

            encoded_interface_name = interface_name.replace("/", "%2F")

            for key in interface_fields.keys():

                aruba_ansible_module.running_config["Interface"][
                    encoded_interface_name
                ][key] = interface_fields[key]

        return aruba_ansible_module

    def update_interface_acl_details(
        self,
        aruba_ansible_module,
        interface_name,
        acl_name,
        acl_type,
        acl_direction,
        update_type="insert",
    ):
        port = Port()

        acl_type_prefix = ""
        if acl_type == "ipv4":
            acl_type_prefix = "aclv4"
        elif acl_type == "ipv6":
            acl_type_prefix = "aclv6"
        elif acl_type == "mac":
            acl_type_prefix = "aclmac"

        field1 = "{0}_{1}_cfg".format(acl_type_prefix, acl_direction)
        value1 = "{0}/{1}".format(acl_name, acl_type)

        field2 = "{0}_{1}_cfg_version".format(acl_type_prefix, acl_direction)
        value2 = randint(-900719925474099, 900719925474099)

        port_fields = {field1: value1, field2: value2}

        if (update_type == "insert") or (update_type == "update"):
            exisitng_values = port.get_port_field_values(
                aruba_ansible_module, interface_name, [field1]
            )

            if field1 in exisitng_values.keys():
                if exisitng_values[field1] != port_fields[field1]:
                    aruba_ansible_module = port.update_port_fields(
                        aruba_ansible_module, interface_name, port_fields
                    )
            else:
                aruba_ansible_module = port.update_port_fields(
                    aruba_ansible_module, interface_name, port_fields
                )

        elif update_type == "delete":
            aruba_ansible_module = port.delete_port_fields(
                aruba_ansible_module, interface_name, [field1, field2]
            )

        return aruba_ansible_module

    def update_interface_qos_profile(
        self,
        aruba_ansible_module,
        interface_name,
        qos_profile_details,
        update_type="insert",
    ):
        port = Port()
        if (update_type == "insert") or (update_type == "update"):
            if "QoS" not in aruba_ansible_module.running_config.keys():
                aruba_ansible_module.module.fail_json(
                    msg="Qos schedule profile being attached to interface {0} "
                    " is not configured".format(interface_name)
                )
            elif (
                qos_profile_details
                not in aruba_ansible_module.running_config["QoS"].keys()
            ):
                aruba_ansible_module.module.fail_json(
                    msg="Qos schedule profile being attached to interface {0} "
                    "is not configured".format(interface_name)
                )
            else:
                port_fields = {"qos": qos_profile_details}
                aruba_ansible_module = port.update_port_fields(
                    aruba_ansible_module, interface_name, port_fields
                )
                return aruba_ansible_module

    def update_interface_qos_rate(
        self, aruba_ansible_module, interface_name, qos_rate
    ):
        port = Port()
        rate_limits = {}
        if qos_rate is not None:
            for k, v in qos_rate.items():
                number, unit = number_unit(v)
                rate_limits[k] = number
                rate_limits[k + "_units"] = unit

            port_fields = {"rate_limits": rate_limits}
        aruba_ansible_module = port.update_port_fields(
            aruba_ansible_module, interface_name, port_fields
        )
        return aruba_ansible_module

    def update_interface_admin_state(
        self, aruba_ansible_module, interface_name, admin_state
    ):

        port = Port()
        interface = Interface()
        user_config = {
            "admin": admin_state,
        }
        interface_fields = {"user_config": user_config}

        port_fields = {"admin": admin_state}

        aruba_ansible_module = port.update_port_fields(
            aruba_ansible_module, interface_name, port_fields
        )
        aruba_ansible_module = interface.update_interface_fields(
            aruba_ansible_module, interface_name, interface_fields
        )

        return aruba_ansible_module

    def update_interface_description(
        self, aruba_ansible_module, interface_name, description
    ):
        interface = Interface()
        interface_fields = {"description": description}
        aruba_ansible_module = interface.update_interface_fields(
            aruba_ansible_module, interface_name, interface_fields
        )
        return aruba_ansible_module


class L2_Interface:
    def create_l2_interface(self, aruba_ansible_module, interface_name):
        if self.check_if_l2_interface_possible(
            aruba_ansible_module, interface_name
        ):
            interface = Interface()
            port = Port()
            aruba_ansible_module = interface.create_interface(
                aruba_ansible_module, interface_name
            )
            aruba_ansible_module = port.create_port(
                aruba_ansible_module, interface_name
            )
            encoded_interface_name = interface_name.replace("/", "%2F")
            interfaces = [encoded_interface_name]
            port_fields = {"interfaces": interfaces, "routing": False}
            aruba_ansible_module = port.update_port_fields(
                aruba_ansible_module, interface_name, port_fields
            )
        else:
            aruba_ansible_module.module.fail_json(
                msg="Interface {0} is currently an L3 interface. Delete "
                "interface then configure as L2.".format(interface_name)
            )

        return aruba_ansible_module

    def delete_l2_interface(self, aruba_ansible_module, interface_name):
        interface = Interface()
        port = Port()
        aruba_ansible_module = interface.delete_interface(
            aruba_ansible_module, interface_name
        )
        aruba_ansible_module = port.delete_port(
            aruba_ansible_module, interface_name
        )
        return aruba_ansible_module

    def check_if_l2_interface_possible(
        self, aruba_ansible_module, interface_name
    ):
        port = Port()
        if port.check_port_exists(aruba_ansible_module, interface_name):
            result = port.get_port_field_values(
                aruba_ansible_module, interface_name, ["vrf"]
            )
            if "vrf" in result.keys():
                if result["vrf"] != "":
                    return False
                else:
                    return True
            else:
                return True
        else:
            return True

    def update_interface_vlan_details(
        self,
        aruba_ansible_module,
        interface_name,
        vlan_details,
        update_type="insert",
    ):
        port = Port()
        interface = L2_Interface()

        if not interface.check_if_l2_interface_possible(
            aruba_ansible_module, interface_name
        ):
            aruba_ansible_module.module.fail_json(
                msg="Interface {0} is currently an L3 interface. Delete "
                "interface then configure as L2.".format(interface_name)
            )
        if not port.check_port_exists(aruba_ansible_module, interface_name):
            aruba_ansible_module.module.fail_json(
                msg="Interface {0} is not configured".format(interface_name)
            )

        if (update_type == "insert") or (update_type == "insert"):
            aruba_ansible_module = port.update_port_fields(
                aruba_ansible_module, interface_name, vlan_details
            )
        elif update_type == "delete":
            vlan_fields = []
            aruba_ansible_module = port.delete_port_fields(
                aruba_ansible_module, interface_name, vlan_fields
            )

        return aruba_ansible_module

    def update_interface_acl_details(
        self,
        aruba_ansible_module,
        interface_name,
        acl_name,
        acl_type,
        acl_direction,
    ):
        interface = Interface()
        aruba_ansible_module = interface.update_interface_acl_details(
            aruba_ansible_module,
            interface_name,
            acl_name,
            acl_type,
            acl_direction,
            update_type="insert",
        )
        return aruba_ansible_module

    def update_interface_qos_profile(
        self,
        aruba_ansible_module,
        interface_name,
        qos_profile_details,
        update_type="insert",
    ):
        interface = Interface()
        aruba_ansible_module = interface.update_interface_qos_profile(
            aruba_ansible_module,
            interface_name,
            qos_profile_details,
            update_type,
        )
        return aruba_ansible_module

    def update_interface_qos_rate(
        self, aruba_ansible_module, interface_name, qos_rate
    ):
        interface = Interface()
        aruba_ansible_module = interface.update_interface_qos_rate(
            aruba_ansible_module, interface_name, qos_rate
        )
        return aruba_ansible_module


class L3_Interface:
    def create_l3_interface(self, aruba_ansible_module, interface_name):
        if self.check_if_l3_interface_possible(
            aruba_ansible_module, interface_name
        ):
            interface = Interface()
            port = Port()
            aruba_ansible_module = interface.create_interface(
                aruba_ansible_module, interface_name, type="l3"
            )
            aruba_ansible_module = port.create_port(
                aruba_ansible_module, interface_name
            )
            encoded_interface_name = interface_name.replace("/", "%2F")
            interfaces = [encoded_interface_name]
            port_fields = {"interfaces": interfaces, "routing": True}
            aruba_ansible_module = port.update_port_fields(
                aruba_ansible_module, interface_name, port_fields
            )
        else:
            aruba_ansible_module.module.fail_json(
                msg="Interface {0} is currently an L2 interface. Delete "
                "interface then configure as L3.".format(interface_name)
            )

        return aruba_ansible_module

    def delete_l3_interface(self, aruba_ansible_module, interface_name):
        interface = Interface()
        port = Port()
        aruba_ansible_module = interface.delete_interface(
            aruba_ansible_module, interface_name
        )
        aruba_ansible_module = port.delete_port(
            aruba_ansible_module, interface_name
        )
        return aruba_ansible_module

    def check_if_l3_interface_possible(
        self, aruba_ansible_module, interface_name
    ):
        port = Port()
        if port.check_port_exists(aruba_ansible_module, interface_name):
            result = port.get_port_field_values(
                aruba_ansible_module,
                interface_name,
                ["vrf", "routing", "vlan_tag"],
            )

            if "vlan_tag" in result.keys():
                if result["vlan_tag"] != "":
                    return False

            if "vrf" in result.keys():
                return True
            if "routing" in result.keys():
                if result["routing"] is False:
                    return False
            else:
                return True
        else:
            return True

    def update_interface_vrf_details_from_l3(
        self,
        aruba_ansible_module,
        vrf_name,
        interface_name,
        update_type="insert",
    ):
        port = Port()
        vrf = VRF()
        if not port.check_port_exists(aruba_ansible_module, interface_name):
            aruba_ansible_module.module.fail_json(
                msg="Interface {0} is not configured".format(interface_name)
            )

        result = port.get_port_field_values(
            aruba_ansible_module, interface_name, ["vrf"]
        )
        if "vrf" in result.keys():
            if result["vrf"] != "" and result["vrf"] != vrf_name:
                aruba_ansible_module.module.fail_json(
                    msg=(
                        "Interface {0} is attached to VRF {1}. Delete "
                        "interfaceand recreate with VRF {2}".format(
                            interface_name, result["vrf"], vrf_name
                        )
                    )
                )

        if not vrf.check_vrf_exists(aruba_ansible_module, vrf_name):
            if vrf_name != "default":
                aruba_ansible_module.module.fail_json(
                    msg="VRF {0} does not exist".format(vrf_name)
                )
            aruba_ansible_module = vrf.create_vrf(
                aruba_ansible_module, vrf_name
            )

        port_field = {"vrf": vrf_name}

        aruba_ansible_module = port.update_port_fields(
            aruba_ansible_module, interface_name, port_field
        )

        return aruba_ansible_module

    def update_interface_vrf_details_from_vrf(
        self,
        aruba_ansible_module,
        vrf_name,
        interface_name,
        update_type="insert",
    ):
        port = Port()
        vrf = VRF()
        if not port.check_port_exists(aruba_ansible_module, interface_name):
            aruba_ansible_module.module.fail_json(
                msg="Interface {0} is not configured".format(interface_name)
            )

        result = port.get_port_field_values(
            aruba_ansible_module, interface_name, ["vrf"]
        )
        if "vrf" in result.keys():
            if result["vrf"] != "" and result["vrf"] != vrf_name:
                aruba_ansible_module.module.fail_json(
                    msg=(
                        "Interface {0} is attached to VRF {1}. Delete "
                        "interface and recreate with VRF {2}".format(
                            interface_name, result["vrf"], vrf_name
                        )
                    )
                )

        if not vrf.check_vrf_exists(aruba_ansible_module, vrf_name):
            if vrf_name != "default":
                aruba_ansible_module.module.fail_json(
                    msg="VRF {0} does not exist".format(vrf_name)
                )
            aruba_ansible_module = vrf.create_vrf(
                aruba_ansible_module, vrf_name
            )

        port_field = {"vrf": vrf_name}

        aruba_ansible_module = port.update_port_fields(
            aruba_ansible_module, interface_name, port_field
        )
        try:
            aruba_ansible_module = port.delete_port_fields(
                aruba_ansible_module, interface_name, ["ip4_address"]
            )
            aruba_ansible_module = port.delete_port_fields(
                aruba_ansible_module, interface_name, ["ip6_address"]
            )
        except Exception:
            pass

        return aruba_ansible_module

    def update_interface_acl_details(
        self,
        aruba_ansible_module,
        interface_name,
        acl_name,
        acl_type,
        acl_direction,
    ):
        interface = Interface()
        aruba_ansible_module = interface.update_interface_acl_details(
            aruba_ansible_module,
            interface_name,
            acl_name,
            acl_type,
            acl_direction,
            update_type="insert",
        )
        return aruba_ansible_module

    def update_interface_qos_profile(
        self,
        aruba_ansible_module,
        interface_name,
        qos_profile_details,
        update_type="insert",
    ):
        interface = Interface()
        aruba_ansible_module = interface.update_interface_qos_profile(
            aruba_ansible_module,
            interface_name,
            qos_profile_details,
            update_type,
        )
        return aruba_ansible_module

    def update_interface_qos_rate(
        self, aruba_ansible_module, interface_name, qos_rate
    ):
        interface = Interface()
        aruba_ansible_module = interface.update_interface_qos_rate(
            aruba_ansible_module, interface_name, qos_rate
        )
        return aruba_ansible_module

    def update_interface_ipv4_address(
        self, aruba_ansible_module, interface_name, ipv4
    ):
        port = Port()
        port_fields = {}
        if ipv4 == [""]:
            aruba_ansible_module = port.delete_port_fields(
                aruba_ansible_module, interface_name, ["ip4_address"]
            )
            return aruba_ansible_module

        port_fields["ip4_address"] = ipv4[0]
        if len(ipv4) > 2:
            port_fields["ip4_address_secondary"] = []
            for item in ipv4[1:]:
                port_fields["ip4_address_secondary"].append(item)
        elif len(ipv4) == 2:
            port_fields["ip4_address_secondary"] = ipv4[1]
        aruba_ansible_module = port.update_port_fields(
            aruba_ansible_module, interface_name, port_fields
        )

        return aruba_ansible_module

    def update_interface_ipv6_address(
        self, aruba_ansible_module, interface_name, ipv6
    ):
        port = Port()
        port_fields = {}
        ip6_addresses = {}

        if ipv6 == [""]:
            aruba_ansible_module = port.delete_port_fields(
                aruba_ansible_module, interface_name, ["ip6_addresses"]
            )
            return aruba_ansible_module

        for item in ipv6:
            ip6_addresses[item] = {
                "node_address": True,
                "preferred_lifetime": 604800,
                "ra_prefix": True,
                "type": "global-unicast",
                "valid_lifetime": 2592000,
            }

        port_fields["ip6_addresses"] = ip6_addresses

        aruba_ansible_module = port.update_port_fields(
            aruba_ansible_module, interface_name, port_fields
        )

        return aruba_ansible_module

    def update_interface_ip_helper_address(
        self, aruba_ansible_module, vrf_name, interface_name, ip_helper_address
    ):

        vrf = VRF()
        if vrf_name is not None:
            vrf_name = "default"

        if not vrf.check_vrf_exists(aruba_ansible_module, vrf_name):

            if vrf_name == "default":
                aruba_ansible_module = vrf.create_vrf(
                    aruba_ansible_module, vrf_name
                )
            else:
                aruba_ansible_module.module.fail_json(
                    msg="VRF {0} is not configured".format(vrf_name)
                )

        if "DHCP_Relay" not in aruba_ansible_module.running_config.keys():

            aruba_ansible_module.running_config["DHCP_Relay"] = {}

        encoded_interface_name = interface_name.replace("/", "%2F")

        index = "{0}/{1}".format(vrf_name, encoded_interface_name)

        if (
            index
            not in aruba_ansible_module.running_config["DHCP_Relay"].keys()
        ):
            aruba_ansible_module.running_config["DHCP_Relay"][index] = {}

        if (
            "ipv4_ucast_server"
            not in aruba_ansible_module.running_config["DHCP_Relay"][
                index
            ].keys()
        ):
            aruba_ansible_module.running_config["DHCP_Relay"][index][
                "ipv4_ucast_server"
            ] = []

        aruba_ansible_module.running_config["DHCP_Relay"][index][
            "port"
        ] = encoded_interface_name

        aruba_ansible_module.running_config["DHCP_Relay"][index][
            "vrf"
        ] = vrf_name

        for item in ip_helper_address:
            aruba_ansible_module.running_config["DHCP_Relay"][index][
                "ipv4_ucast_server"
            ].append(item)
            aruba_ansible_module.running_config["DHCP_Relay"][index][
                "ipv4_ucast_server"
            ].sort()

        return aruba_ansible_module
