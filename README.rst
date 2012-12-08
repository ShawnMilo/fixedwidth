Easy two-way conversion between Python dictionaries and fixed-width files.

Requires a 'config' dictonary. See unit tests for full example.

Small example::

    SAMPLE_CONFIG = {

        'first_name': {
            'required': True,
            'type': 'string',
            'start_pos': 1,
            'end_pos': 10,
            'alignment': 'left',
            'padding': ' '
        },

        'last_name': {
            'required': True,
            'type': 'string',
            'start_pos': 11,
            'end_pos': 30,
            'alignment': 'left',
            'padding': ' '
        },

    }

Notes:

#.  A field must have a start_pos and either an end_pos or a length.
    If both an end_pos and a length are provided, they must not conflict.

#.  A field may not have a default value if it is required.

#.  Supported types are string, integer, and decimal.

#.  Alignment and padding are required.

