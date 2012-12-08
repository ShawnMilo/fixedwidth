#!/usr/bin/env python

import unittest
from copy import deepcopy

from ..fixedwidth import FixedWidth

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

    'nickname': {
        'required': False,
        'type': 'string',
        'start_pos': 31,
        'length': 15,
        'alignment': 'left',
        'padding': ' '
    },

    'age': {
        'type': 'integer',
        'alignment': 'right',
        'start_pos': 46,
        'padding': '0',
        'length': 3,
        'required': True
    },

    'meal': {
        'type': 'string',
        'start_pos': 49,
        'default': 'no preference',
        'padding': ' ',
        'end_pos': 68,
        'length': 20,
        'alignment': 'left',
        'required': False
    }

}


class TestFixedWidth(unittest.TestCase):

    """
    Test of the FixedWidth class.
    """

    def test_basic(self):

        """
        Test a simple, valid example.
        """

        fw_config = deepcopy(SAMPLE_CONFIG)

        FW = FixedWidth(fw_config)

        new_values = {'last_name': 'Smith', 'first_name': 'Michael', 'age': 32, 'meal': 'vegetarian'}
        FW.update(**new_values)

        fw_string = FW.line

        self.assertEquals(
            fw_string, 'Michael   Smith                              032vegetarian          \r\n')

    def test_update(self):
        """
        Test FixedWidth.update()
        """

        fw_config = deepcopy(SAMPLE_CONFIG)

        new_values = {'last_name': 'Smith', 'first_name': 'Michael', 'age': 32, 'meal': 'vegetarian'}

        FW = FixedWidth(fw_config)

        FW.update(**new_values)

        #change a value
        FW.update(meal = 'Paleo')
        self.assertEquals(FW.data['meal'], 'Paleo')

        #nothing else should have changed
        self.assertEquals(FW.data['first_name'], 'Michael')

    def test_fw_to_dict(self):

        """
        Pass in a line and receive dictionary.
        """

        fw_config = deepcopy(SAMPLE_CONFIG)

        FW = FixedWidth(fw_config)
        FW.line = 'Michael   Smith                              032vegetarian          '

        values = FW.data
        self.assertEquals(values['first_name'], 'Michael')
        self.assertEquals(values['last_name'], 'Smith')
        self.assertEquals(values['age'], 32)
        self.assertEquals(values['meal'], 'vegetarian')
