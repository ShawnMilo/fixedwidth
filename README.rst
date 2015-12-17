Easy two-way conversion between Python dictionaries and fixed-width files.
The FixedWidth class has been used in production without modification for 
several years.

This module has also proven useful for "debugging" a fixed-width spec --
an invalid configuration reports an error that may not be obvious from
reading the spec document.

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

#.  If 'decimal' type is used, there are two other optional parameters,
    'precision' and 'separator'. 
        
        a. 'precision' is a integer that specifies how many places the decimal needs 
        to be rounded to. 
        
        b. 'separator' can be a string or None. If None, the resultant value will
        not have a separator, the value will be offset by the number of precision
        decimals for example::
            
            CONFIG = {
                "money": {
                    "type": "decimal",
                    "start_pos": 1,
                    "padding": "0",
                    "end_pos": 10,
                    "alignment": "right",
                    "required": True,
                    "precision": 4,
                    "separator": None,
                }
            }
            
            fw = FixedWidth(CONFIG,**{'money':Decimal('1.0245678')})
            
            print fw.line
            '0000010245\r\n'

            
            
        
