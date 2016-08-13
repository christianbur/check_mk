register_check_parameters(
    subgroup_applications,
    "snmp_info_v2_parameters",
    _("SNMP Firmware Check"),
    Dictionary(
        help = _("SNMP Firmware Check"),
        elements = [
            ( "standard_firmware",
              ListOf(
                  Tuple(
                    title = ("SNMP Firmware Check"),
                    elements = [
                      TextUnicode(
                          title = _("ModelName starts with"),
                          help = _("ModelName starts with"),
                          allow_empty = False,
                      ),
                      TextUnicode(
                          title = _("Standard firmware for ModelName (search in sysDescr)"),
                          help = _("Standard firmware for ModelName (search in sysDescr"),
                          allow_empty = False,
                      ),
                      DropdownChoice(
                            title = _("Status if standard firmware not found in sysDesc"),
                            default_value = None,
                            choices = [
                                ( "0", _("OK") ),
                                ( "1", _("WARN") ),
                      ]),
                     ]),
                     add_label = _("Add Firmware Check"),
                     movable = False,
                     title = _("check Firmware-String in sysDesc"),
                  )),
        ],
    ),
    None,
    "dict",
    #match_type = "dict",
)
