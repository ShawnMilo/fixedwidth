#!/usr/bin/env python

"""
Tests for the FixedWidth class.
"""
import unittest
from decimal import Decimal, ROUND_UP
from copy import deepcopy

import datetime

try:
    from fixedwidth import FixedWidth
except ImportError:
    from fixedwidth.fixedwidth import FixedWidth

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

    "date": {
        "required": False,
        "type": "date",
        "default": datetime.datetime.strptime('20170101', '%Y%m%d'),
        "start_pos": 101,
        "end_pos": 108,
        "alignment": "right",
        "padding": " ",
        "format": '%Y%m%d',
        },

    "decimal_precision": {
        "required": False,
        "type": "decimal",
        "default": 1,
        "start_pos": 109,
        "length": 5,
        "precision": 3,
        "alignment": "right",
        "rounding": ROUND_UP,
        "padding": " "
        },
    "none_date": {
        "required": False,
        "type": "date",
        "default": None,
        "start_pos": 114,
        "end_pos": 121,
        "alignment": "right",
        "padding": " ",
        "format": '%Y%m%d',
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
            longitude=Decimal('-74.0059'), elevation=-100, decimal_precision=Decimal('1.0001'),
        )

        fw_string = fw_obj.line

        good = (
            "Michael   Smith                              "
            "032vegetarian             40.7128   -74.0059-100   98.6201701011.001        \r\n"
        )

        self.assertEqual(fw_string, good)

    def test_update(self):
        """
        Test FixedWidth.update()
        """

        fw_config = deepcopy(SAMPLE_CONFIG)
        fw_obj = FixedWidth(fw_config)

        fw_obj.update(
            last_name="Smith", first_name="Michael",
            age=32, meal="vegetarian", latitude=Decimal('40.7128'),
            longitude=Decimal('-74.0059'), elevation=-100, decimal_precision=1,
        )

        #change a value
        fw_obj.update(meal="Paleo")
        self.assertEqual(fw_obj.data["meal"], "Paleo")

        #nothing else should have changed
        self.assertEqual(fw_obj.data["first_name"], "Michael")

    def test_fw_to_dict(self):
        """
        Pass in a line and receive dictionary.
        """

        fw_config = deepcopy(SAMPLE_CONFIG)

        fw_obj = FixedWidth(fw_config)
        fw_obj.line = (
            "Michael   Smith                              "
            "032vegetarian             40.7128   -74.0059-100   98.6201701011.000        \r\n"
        )

        values = fw_obj.data
        self.assertEqual(values["first_name"], "Michael")
        self.assertEqual(values["last_name"], "Smith")
        self.assertEqual(values["age"], 32)
        self.assertEqual(values["meal"], "vegetarian")
        self.assertEqual(values["latitude"], Decimal('40.7128'))
        self.assertEqual(values["longitude"], Decimal('-74.0059'))
        self.assertEqual(values["elevation"], -100)
        self.assertEqual(values["temperature"], Decimal('98.6'))
        self.assertEqual(values["decimal_precision"], Decimal('1.000'))
        self.assertEqual(values["date"], datetime.datetime.strptime('20170101', '%Y%m%d'))
        self.assertEqual(values["none_date"], None)

    def test_required_is_none(self):
        """
        Pass in a None value and raise exception.
        """
        fw_config = deepcopy(SAMPLE_CONFIG)
        fw_obj = FixedWidth(fw_config)
        fw_obj.update(
            last_name="Smith", first_name="Michael",
            age=32, meal="vegetarian", latitude=Decimal('40.7128'),
            longitude=Decimal('-74.0059'), elevation=None,
        )
        self.assertRaises(Exception, fw_obj.validate)

    def test_optional_is_none(self):
        """
        Pass in a None value and raise exception.
        """
        fw_config = deepcopy(SAMPLE_CONFIG)
        fw_obj = FixedWidth(fw_config)
        fw_obj.update(
            last_name="Smith", first_name="Michael",
            age=32, meal="vegetarian", latitude=Decimal('40.7128'),
            longitude=Decimal('-74.0059'), elevation=-100, decimal_precision=None,
        )

        good = (
            "Michael   Smith                              "
            "032vegetarian             40.7128   -74.0059-100   98.6201701011.000        \r\n"
        )

        self.assertEqual(fw_obj.line, good)

    def test_fw_contains_empty_value(self):
        """
        Pass in a line with empty value and test that default gets set.
        """

        fw_config = deepcopy(SAMPLE_CONFIG)

        fw_obj = FixedWidth(fw_config)
        fw_obj.line = (
            "Michael   Smith                              "
            "032vegetarian             40.7128   -74.0059-100   98.620170101              \r\n"
        )


        self.assertEqual(fw_obj.data["decimal_precision"], Decimal(1))

if __name__ == '__main__':
    unittest.main()
