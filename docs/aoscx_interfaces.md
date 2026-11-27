# module: aoscx_interfaces

description: This module configures a list of existing interfaces (physical
ports, LAGs) on AOS-CX devices in a single task. It covers the settings of the
aoscx_interface, aoscx_l2_interface, aoscx_interface_stp,
aoscx_port_access_interface and aoscx_port_access_auth modules commonly used on
access ports, and reuses one REST session for every interface, which is much
faster than one task per interface and per feature. Only the supplied settings
are managed; omitted settings are left unchanged. The interfaces must already
exist. The dot1x and mac_auth settings require a pyaoscx release that ships the
PortAccessAuthConfiguration class, and the port access settings require REST
API version 10.16 (set ansible_aoscx_rest_version to 10.16).

##### ARGUMENTS

```YAML
  interfaces:
    description: >
      List of interfaces to configure. With state delete, every
      supplied setting is reset to its default value, whatever the value
      given.
    required: true
    type: list
    elements: dict
    suboptions:
      name:
        description: Name of the interface, for example 1/1/1 or lag10.
        required: true
        type: str
      description:
        description: Description of the interface (description).
        required: false
        type: str
      enabled:
        description: >
          Administrative state of the interface, true for no shutdown.
        required: false
        type: bool
      mtu:
        description: MTU of the interface (mtu).
        required: false
        type: int
      loop_protect_enable:
        description: Enable loop protection (loop-protect).
        required: false
        type: bool
      app_recognition_enable:
        description: >
          Enable application recognition on the interface
          (app-recognition enable).
        required: false
        type: bool
      vlan_mode:
        description: >
          Layer 2 mode of the interface (vlan access or vlan trunk).
          Setting it also disables routing on the interface (no routing).
          Required by the other VLAN options.
        required: false
        type: str
        choices:
          - access
          - trunk
      vlan_access:
        description: >
          Access VLAN ID. When omitted with vlan_mode access, the
          current access VLAN is left unchanged.
        required: false
        type: int
      vlan_trunks:
        description: >
          Trunk allowed VLAN IDs, vlan_mode must be trunk. The supplied
          list replaces the current trunk VLANs (order does not matter).
        required: false
        type: list
        elements: int
      trunk_allowed_all:
        description: >
          Allow all VLANs on the trunk, vlan_mode must be trunk.
          Mutually exclusive with vlan_trunks.
        required: false
        type: bool
      native_vlan_id:
        description: >
          Native VLAN ID of the trunk, vlan_mode must be trunk. Defaults
          to VLAN 1 on the switch.
        required: false
        type: int
      native_vlan_tag:
        description: >
          Accept only tagged packets on the trunk native VLAN
          (vlan trunk native <id> tag), vlan_mode must be trunk.
        required: false
        type: bool
      stp:
        description: Spanning tree settings of the interface.
        required: false
        type: dict
        suboptions:
          admin_edge:
            description: Administrative edge port (spanning-tree port-type admin-edge).
            required: false
            type: bool
          bpdu_guard:
            description: BPDU guard (spanning-tree bpdu-guard).
            required: false
            type: bool
          bpdu_filter:
            description: BPDU filter (spanning-tree bpdu-filter).
            required: false
            type: bool
          root_guard:
            description: Root guard (spanning-tree root-guard).
            required: false
            type: bool
          loop_guard:
            description: Loop guard (spanning-tree loop-guard).
            required: false
            type: bool
          tcn_guard:
            description: TCN guard (spanning-tree tcn-guard).
            required: false
            type: bool
          link_type:
            description: Link type (spanning-tree link-type).
            required: false
            type: str
            choices:
              - auto
              - point_to_point
              - shared
      port_access:
        description: Port access settings of the interface.
        required: false
        type: dict
        suboptions:
          concurrent_onboarding:
            description: >
              Concurrent onboarding
              (port-access onboarding-method concurrent enable).
            required: false
            type: bool
          client_limit:
            description: >
              Maximum number of authenticated clients
              (aaa authentication port-access client-limit).
            required: false
            type: int
          auth_mode:
            description: Port access authentication mode.
            required: false
            type: str
            choices:
              - client-mode
              - device-mode
              - proxy-mode
              - multi-domain
          allow_bpdu:
            description: >
              Protocol BPDUs allowed before authentication
              (aaa authentication port-access allow-cdp-bpdu and
              allow-lldp-bpdu). Order does not matter.
            required: false
            type: list
            elements: str
            choices:
              - cdp
              - lldp
          allow_flood_traffic:
            description: >
              Allow flood traffic before authentication
              (port-access allow-flood-traffic enable).
            required: false
            type: bool
          client_ip_track:
            description: Client IP tracking (client track ip).
            required: false
            type: dict
            suboptions:
              admin_state:
                description: Tracking state.
                required: false
                type: str
                choices:
                  - enable
                  - disable
                  - auto
              update_interval:
                description: Update interval in seconds.
                required: false
                type: int
              client_limit:
                description: Maximum number of tracked clients.
                required: false
                type: int
          device_fingerprint:
            description: >
              Device fingerprinting
              (client device-fingerprint apply-profile).
            required: false
            type: dict
            suboptions:
              profile_name:
                description: Name of an existing device fingerprint profile.
                required: false
                type: str
              client_limit:
                description: Maximum number of fingerprinted clients.
                required: false
                type: int
      dot1x:
        description: >
          802.1X authenticator settings of the interface
          (aaa authentication port-access dot1x authenticator). With
          state delete the whole 802.1X configuration of the interface
          is removed.
        required: false
        type: dict
        suboptions:
          auth_enable:
            description: Enable the authentication method (enable).
            required: false
            type: bool
          reauth_enable:
            description: Periodic re-authentication (reauth).
            required: false
            type: bool
          reauth_period:
            description: Re-authentication period in seconds.
            required: false
            type: int
          cached_reauth_enable:
            description: Cached re-authentication (cached-reauth).
            required: false
            type: bool
          cached_reauth_period:
            description: Cached re-authentication period in seconds.
            required: false
            type: int
          eapol_timeout:
            description: EAPOL timeout in seconds (802.1X only).
            required: false
            type: int
          max_retries:
            description: Maximum number of authentication retries.
            required: false
            type: int
          max_requests:
            description: Maximum number of EAPOL requests (802.1X only).
            required: false
            type: int
          quiet_period:
            description: Quiet period in seconds.
            required: false
            type: int
          discovery_period:
            description: Discovery period in seconds (802.1X only).
            required: false
            type: int
      mac_auth:
        description: >
          MAC authentication settings of the interface
          (aaa authentication port-access mac-auth), same options as
          dot1x. With state delete the whole MAC authentication
          configuration of the interface is removed.
        required: false
        type: dict
        suboptions:
          auth_enable:
            description: Enable the authentication method (enable).
            required: false
            type: bool
          reauth_enable:
            description: Periodic re-authentication (reauth).
            required: false
            type: bool
          reauth_period:
            description: Re-authentication period in seconds.
            required: false
            type: int
          cached_reauth_enable:
            description: Cached re-authentication (cached-reauth).
            required: false
            type: bool
          cached_reauth_period:
            description: Cached re-authentication period in seconds.
            required: false
            type: int
          eapol_timeout:
            description: EAPOL timeout in seconds (802.1X only).
            required: false
            type: int
          max_retries:
            description: Maximum number of authentication retries.
            required: false
            type: int
          max_requests:
            description: Maximum number of EAPOL requests (802.1X only).
            required: false
            type: int
          quiet_period:
            description: Quiet period in seconds.
            required: false
            type: int
          discovery_period:
            description: Discovery period in seconds (802.1X only).
            required: false
            type: int
  state:
    description: >
      Configure (create or update, same behaviour) the supplied
      settings, or reset them to their default value (delete).
    required: false
    default: create
    choices:
      - create
      - update
      - delete
    type: str
```

##### EXAMPLES

```YAML
- name: Configure the access ports 1/1/1 to 1/1/48 in a single task
  aoscx_interfaces:
    interfaces: "{{ access_ports }}"
  vars:
    access_ports: >-
      {%- set ports = [] -%}
      {%- for n in range(1, 49) -%}
      {%-   set _ = ports.append(dict(access_port, name='1/1/' ~ n)) -%}
      {%- endfor -%}
      {{ ports }}
    access_port:
      description: colorless_port
      enabled: true
      vlan_mode: access
      vlan_access: 1
      stp:
        admin_edge: true
        bpdu_guard: true
      port_access:
        client_limit: 2
        allow_bpdu: [cdp, lldp]
      dot1x:
        auth_enable: true
        reauth_enable: true
        reauth_period: 86400
      mac_auth:
        auth_enable: true

- name: Configure a trunk uplink and an access port
  aoscx_interfaces:
    interfaces:
      - name: 1/1/49
        description: uplink
        vlan_mode: trunk
        native_vlan_id: 1
        vlan_trunks: [10, 20, 30]
      - name: 1/1/1
        vlan_mode: access
        vlan_access: 10

- name: Remove the 802.1X configuration and the description of two ports
  aoscx_interfaces:
    interfaces:
      - {name: 1/1/1, description: x, dot1x: {}}
      - {name: 1/1/2, description: x, dot1x: {}}
    state: delete
```
