#!/usr/bin/env python

"""
Tests for the FixedWidth class.
"""

import unittest
from decimal import Decimal
from copy import deepcopy

from ..fixedwidth import FixedWidth

SAMPLE_CONFIG = {

    "first_name": {
        "required": True,
        "type": "string",
        "start_pos": 1,
        "end_pos": 10,
        "alignment": "left",
        "padding": " "
    },

    "last_name": {
        "required": True,
        "type": "string",
        "start_pos": 11,
        "end_pos": 30,
        "alignment": "left",
        "padding": " "
    },

    "nickname": {
        "required": False,
        "type": "string",
        "start_pos": 31,
        "length": 15,
        "alignment": "left",
        "padding": " "
    },

    "age": {
        "type": "integer",
        "alignment": "right",
        "start_pos": 46,
        "padding": "0",
        "length": 3,
        "required": True
    },

    "meal": {
        "type": "string",
        "start_pos": 49,
        "default": "no preference",
        "padding": " ",
        "end_pos": 68,
        "length": 20,
        "alignment": "left",
        "required": False
    },

    "latitude": {
        "required": True,
        "type": "decimal",
        "start_pos": 69,
        "end_pos": 78,
        "alignment": "right",
        "padding": " "
        },

    "longitude": {
        "required": True,
        "type": "decimal",
        "start_pos": 79,
        "end_pos": 89,
        "alignment": "right",
        "padding": " "
        },

    "elevation": {
        "required": True,
        "type": "integer",
        "start_pos": 90,
        "end_pos": 93,
        "alignment": "right",
        "padding": " "
        },

    "temperature": {
        "required": False,
        "type": "decimal",
        "default": "98.6",
        "start_pos": 94,
        "end_pos": 100,
        "alignment": "right",
        "padding": " "
        },

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
        fw_obj = FixedWidth(fw_config)
        fw_obj.update(
            last_name="Smith", first_name="Michael",
            age=32, meal="vegetarian", latitude=Decimal('40.7128'),
            longitude=Decimal('-74.0059'), elevation=-100,
        )

        fw_string = fw_obj.line

        good = (
            "Michael   Smith                              "
            "032vegetarian             40.7128   -74.0059-100   98.6\r\n"
        )

        self.assertEquals(fw_string, good)

    def test_update(self):
        """
        Test FixedWidth.update()
        """

        fw_config = deepcopy(SAMPLE_CONFIG)
        fw_obj = FixedWidth(fw_config)

        fw_obj.update(
            last_name="Smith", first_name="Michael",
            age=32, meal="vegetarian", latitude=Decimal('40.7128'),
            longitude=Decimal('-74.0059'), elevation=-100,
        )

        #change a value
        fw_obj.update(meal="Paleo")
        self.assertEquals(fw_obj.data["meal"], "Paleo")

        #nothing else should have changed
        self.assertEquals(fw_obj.data["first_name"], "Michael")

    def test_fw_to_dict(self):
        """
        Pass in a line and receive dictionary.
        """

        fw_config = deepcopy(SAMPLE_CONFIG)

        fw_obj = FixedWidth(fw_config)
        fw_obj.line = (
            "Michael   Smith                              "
            "032vegetarian             40.7128   -74.0059-100  98.6"
        )

        values = fw_obj.data
        self.assertEquals(values["first_name"], "Michael")
        self.assertEquals(values["last_name"], "Smith")
        self.assertEquals(values["age"], 32)
        self.assertEquals(values["meal"], "vegetarian")
        self.assertEquals(values["latitude"], Decimal('40.7128'))
        self.assertEquals(values["longitude"], Decimal('-74.0059'))
        self.assertEquals(values["elevation"], -100)
        self.assertEquals(values["temperature"], Decimal('98.6'))

    def test_truncate(self):
        fw_config = deepcopy({
            "field_truncate": {
                "required": True,
                'truncate': True,
                "type": "string",
                "start_pos": 1,
                "length": 8,
                "alignment": "left",
                "padding": " "
            },
            "field_truncate_longer": {
                "required": True,
                'truncate': True,
                "type": "string",
                "start_pos": 9,
                "length": 8,
                "alignment": "left",
                "padding": " "
            },
            "field_truncate_int": {
                "required": True,
                'truncate': True,
                "type": "numeric",
                "start_pos": 17,
                "length": 3,
                "alignment": "left",
                "padding": " "
            },
            "field_truncate_int_longer": {
                "required": True,
                'truncate': True,
                "type": "numeric",
                "start_pos": 20,
                "length": 5,
                "alignment": "left",
                "padding": " "
            }
        })
        fw_obj = FixedWidth(fw_config, line_end='')

        fw_obj.update(
            field_truncate='1234567890',
            field_truncate_longer='1234',
            field_truncate_int=1234,
            field_truncate_int_longer=1234
        )
        self.assertEquals(fw_obj.line, '123456781234    1231234 ')

if __name__ == '__main__':
    unittest.main()
