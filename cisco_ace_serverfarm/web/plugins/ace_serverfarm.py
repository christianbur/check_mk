register_check_parameters(
    subgroup_networking,
    "cisco_ace_serverfarm",
    _("ACE_F5 Serverfarm"),
    Dictionary(
        elements = [
            ( "ace_serverfarm_wato",
              ListOf(
                  Tuple(
                    title = ("ACE_F5 Serverfarm"),
                    elements = [
                      TextUnicode(
                          title = _("Name of ACE_F5-Serverfarm"),
                          help = _("The configured value must match a serverfarm reported by the monitored "
                                   "device."),
                          allow_empty = False,
                      ),
                      DropdownChoice(
                            title = _("Worst state if serverfarm is crit"),
                            default_value = None,
                            choices = [
                                ( None, _("original return state") ),
                                ( "0", _("OK") ),
                                ( "1", _("WARN") ),
                                ( "3", _("UNKNOWN") ),
                      ]),
                      DropdownChoice(
                            title = _("Worst state if serverfarm is warning"),
                            default_value = None,
                            choices = [
                                ( None, _("orginal return state") ),
                                ( "0", _("OK") ),
                                ( "3", _("UNKNOWN") ),
                      ]),
                      Checkbox(
                            title = _("Show only short status of other nodes (only ACE)"),
                            label = _(""),
                      ),
                     ]),
                     add_label = _("Add Serverfarm"),
                     movable = False,
                     title = _("ACE_F5 Serverfarm specific configuration"),
                  )),
                        ("default_crit",    DropdownChoice(
                            title = _("DEFAULT: Worst state if serverfarm is crit"),
                            default_value = None,
                            choices = [
                                ( None, _("original return state") ),
                                ( "0", _("OK") ),
                                ( "1", _("WARN") ),
                                ( "3", _("UNKNOWN") )
                        ])),
                        ("default_warn",  DropdownChoice(
                            title = _("DEFAULT: Worst state if serverfarm is warning"),
                            default_value = None,
                            choices = [
                                ( None, _("orginal return state") ),
                                ( "0", _("OK") ),
                                ( "3", _("UNKNOWN") )
                        ])),
        ],
    ),
    TextAscii( title = _("ACE_F5 Serverfarm")),
    "first"
)