#!/usr/bin/python

inventory_displayhints.update({

    ".networking.switch_ipRoute:"                              : { "title" : _("Switch Routes (ipRoute)"), "render" : render_inv_dicttable,
                                                                "keyorder" : [ "ipRouteDest", "ipRouteMask_cidr", "ipRouteMask", "ipRouteIfIndex",
								"ipRouteProto", "ipRouteNextHop", "ipRouteType"] },
    ".networking.switch_ipRoute:*.ipRouteDest"                 : { "title" : _("ipRouteDest") },
    ".networking.switch_ipRoute:*.ipRouteMask_cidr"            : { "title" : _("ipRouteMask_cidr") },
    ".networking.switch_ipRoute:*.ipRouteMask"                 : { "title" : _("ipRouteMask") },
    ".networking.switch_ipRoute:*.ipRouteIfIndex"              : { "title" : _("ipRouteIfIndex") },
    ".networking.switch_ipRoute:*.ipRouteProto"                : { "title" : _("ipRouteProto") },
    ".networking.switch_ipRoute:*.ipRouteNextHop"              : { "title" : _("ipRouteNextHop") },
    ".networking.switch_ipRoute:*.ipRouteType"                 : { "title" : _("ipRouteType") },


    ".networking.switch_ipCidrRoute:"                            : { "title" : _("Switch Routes (ipCidrRoute)"), "render" : render_inv_dicttable,
                                                                "keyorder" : [ "ipCidrRouteDest", "ipCidrRouteMask_cidr", "ipCidrRouteMask", "ipCidrRouteIfIndex",
                                                                "ipCidrRouteProto", "ipCidrRouteNextHop", "ipCidrRouteType"] },
    ".networking.switch_ipCidrRoute:*.ipCidrRouteDest"           : { "title" : _("ipCidrRouteDest") },
    ".networking.switch_ipCidrRoute:*.ipCidrRouteMask_cidr"      : { "title" : _("ipCidrRouteMask_cidr") },
    ".networking.switch_ipCidrRoute:*.ipCidrRouteMask"           : { "title" : _("ipCidrRouteMask") },
    ".networking.switch_ipCidrRoute:*.ipCidrRouteIfIndex"        : { "title" : _("ipCidrRouteIfIndex") },
    ".networking.switch_ipCidrRoute:*.ipCidrRouteProto"          : { "title" : _("ipCidrRouteProto") },
    ".networking.switch_ipCidrRoute:*.ipCidrRouteNextHop"        : { "title" : _("ipCidrRouteNextHop") },
    ".networking.switch_ipCidrRoute:*.ipCidrRouteType"           : { "title" : _("ipCidrRouteType") },

   ".networking.switch_addresses:"                           : { "title" : _("Switch IP-Addresses"), "render" : render_inv_dicttable,
                                                           "keyorder" : [ "index", "description", "alias", "address" ], },
    ".networking.switch_addresses:*.index"                     : { "title" : _("if_Index") },
    ".networking.switch_addresses:*.description"               : { "title" : _("If_Description")},
    ".networking.switch_addresses:*.alias"                     : { "title" : _("If_Alias") },
    ".networking.switch_addresses:*.address"                   : { "title" : _("IP-Address") },


    ".networking.switch_interfaces:"                          : { "title" : _("Switch Interfaces"), "render" : render_inv_dicttable,
                                                                "keyorder" : [ "index", "description", "alias", "oper_status", "speed", "dulpex_status", 
								"neighbor", "vlan", "vlan_voice", "vlan_trunk", "trunk" ], },
    ".networking.switch_interfaces:*.index"                   : { "title" : _("If_Index") },
    ".networking.switch_interfaces:*.description"             : { "title" : _("If_Description") },
    ".networking.switch_interfaces:*.alias"                   : { "title" : _("If_Alias") },
    ".networking.switch_interfaces:*.oper_status"             : { "title" : _("Oper_Status") },
    ".networking.switch_interfaces:*.speed"                   : { "title" : _("Speed"), "paint" : "nic_speed", },
    ".networking.switch_interfaces:*.dulpex_status"           : { "title" : _("Duplex Status") },
    ".networking.switch_interfaces:*.neighbor"                : { "title" : _("Neighbor (CDP/LLDP)")  },
    ".networking.switch_interfaces:*.vlan"                    : { "title" : _("VLAN") },
    ".networking.switch_interfaces:*.vlan_voice"              : { "title" : _("Voice VLAN") },
    ".networking.switch_interfaces:*.vlan_trunk"              : { "title" : _("Trunk VLAN") },
    ".networking.switch_interfaces:*.trunk"                   : { "title" : _("Trunk/Access") },


   ".networking.switch_mac:"                           : { "title" : _("Switch MAC-Adressen"), "render" : render_inv_dicttable,
                                                           "keyorder" : [ "index", "description", "trunk","vlan", "mac" ], },
    ".networking.switch_mac:*.index"                     : { "title" : _("if_Index") },
    ".networking.switch_mac:*.description"               : { "title" : _("If_Description")},
    ".networking.switch_mac:*.trunk"                     : { "title" : _("Trunk/Access") },
    ".networking.switch_mac:*.vlan"               	 : { "title" : _("Vlan")},
    ".networking.switch_mac:*.mac"                       : { "title" : _("MAC-Address/Vendor") },



   ".networking.switch_mac_count:"                      : { "title" : _("Switch MAC-Adressen Count"), "render" : render_inv_dicttable,
                                                           "keyorder" : [ "vendor", "counter" ], },
    ".networking.switch_mac_count:*.vendor"             : { "title" : _("MAc-Address Vendor") },
    ".networking.switch_mac_count:*.counter"            : { "title" : _("Counter")},
})


declare_invtable_view("invswitch_interface",   ".networking.switch_interfaces:",   _("Switch Interface"),    	     _("Switch Interfaces"))
declare_invtable_view("invswitch_addresses",   ".networking.switch_addresses:",    _("Switch Ip-Addresses"), 	     _("Switch IP-Addresses"))
declare_invtable_view("invswitch_ipRoute",     ".networking.switch_ipRoute:",      _("Switch Routes (ipRoute)"),     _("Switch Routes (ipRoute)"))
declare_invtable_view("invswitch_ipCidrRoute", ".networking.switch_ipCidrRoute:",  _("Switch Routes (ipCidrRoute)"), _("Switch Routes (ipCidrRoute)"))
declare_invtable_view("invswitch_mac",         ".networking.switch_mac:",          _("Switch MAC-Adressen"),         _("Switch Mac-Adressen"))
declare_invtable_view("invswitch_mac_count",  ".networking.switch_mac_count:",     _("Switch MAC-Adressen Count"),   _("Switch Mac-Adressen Count"))
