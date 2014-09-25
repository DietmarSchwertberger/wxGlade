"""\
wxComboBox widget configuration

@copyright: 2014 Carsten Grohmann
@license: MIT (see license.txt) - THIS PROGRAM COMES WITH NO WARRANTY
"""

config = {
    'wxklass': 'wxComboBox',
    'style_defs': {
        'wxCB_SIMPLE': {
            'desc': _('Creates a combobox with a permanently displayed list. '
                      'Windows only.'),
        },
        'wxCB_DROPDOWN': {
            'desc': _('Creates a combobox with a drop-down list.'),
        },
        'wxCB_READONLY': {
            'desc': _('Same as wxCB_DROPDOWN but only the strings specified '
                      'as the combobox choices can be selected, it is '
                      'impossible to select (even from a program) a string '
                      'which is not in the choices list.'),
        },
        'wxCB_SORT': {
            'desc': _('	Sorts the entries in the list alphabetically.'),
        },
        'wxTE_PROCESS_ENTER': {
            'desc': _('The control will generate the event '
                      'wxEVT_COMMAND_TEXT_ENTER (otherwise pressing Enter '
                      'key is either processed internally by the control '
                      'or used for navigation between dialog controls). '
                      'Windows only.'),
        },
    },
    'box_label': _('Style'),
    'style_list': ['wxCB_SIMPLE', 'wxCB_DROPDOWN', 'wxCB_READONLY',
                   'wxCB_SORT', 'wxTE_PROCESS_ENTER	'],
}




