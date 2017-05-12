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
        "required": False,
        "type": "decimal",
        "default": "52.23",
        "start_pos": 69,
        "end_pos": 78,
        "alignment": "right",
        "padding": " "
        },

    "longitude": {
        "required": False,
        "default": Decimal('4.38'),
        "type": "decimal",
        "start_pos": 79,
        "end_pos": 89,
        "alignment": "right",
        "padding": " "
        },

    "elevation": {
        "required": False,
        "type": "integer",
        "default": 7,
        "start_pos": 90,
        "end_pos": 93,
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
            "032vegetarian             40.7128   -74.0059-100\r\n"
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
            longitude=Decimal('-74.0059'), elevation=-100,
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
            "032vegetarian             40.7128   -74.0059-100"
        )

        values = fw_obj.data
        self.assertEqual(values["first_name"], "Michael")
        self.assertEqual(values["last_name"], "Smith")
        self.assertEqual(values["age"], 32)
        self.assertEqual(values["meal"], "vegetarian")
        self.assertEqual(values["latitude"], Decimal('40.7128'))
        self.assertEqual(values["longitude"], Decimal('-74.0059'))
        self.assertEqual(values["elevation"], -100)

    def test_default_conversion_decimal(self):
        """
        Test that default value is converted when it doesn't match the type
        """
        config = {
            "defaulttypemismatchstr": {
                "required": False,
                "type": "decimal",
                "default": "52.23",
                "start_pos": 1,
                "length": 8,
                "alignment": "right",
                "padding": " "
                },
            }
        good_line = "{:8}\r\n".format(52.23)
        fw_obj = FixedWidth(config)

        #defaulttypemismatch value not set so will use default value
        self.assertEqual(good_line, fw_obj.line)
        self.assertIsInstance(fw_obj.data["defaulttypemismatchstr"], Decimal)


    def test_default_conversion_fails(self):
        """
        Test that value error is raised when default mismatch and conversion fails
        """
        field_name = "defaulttypemismatchbad"
        field_type = "decimal"

        config = {
            field_name: {
                "required": False,
                "type": field_type,
                "default": "bad",
                "start_pos": 1,
                "length": 8,
                "alignment": "right",
                "padding": " ",
            },
        }

        self.assertRaisesRegex(ValueError, "^Unable to convert.*$", FixedWidth, config)

    def test_default_conversion_integer(self):
        """
        Test that default integer value is converted when it doesn't match the type
        """
        field_name = "defaulttypemismatch"
        field_type = "integer"

        config = {
            field_name: {
                "required": False,
                "type": field_type,
                "default": "52",
                "start_pos": 1,
                "length": 8,
                "alignment": "right",
                "padding": " ",
            },
        }
        good_line = "{:8}\r\n".format(52)
        fw_obj = FixedWidth(config)

        #field not set so will use default value
        self.assertEqual(good_line, fw_obj.line)
        self.assertIsInstance(fw_obj.data["defaulttypemismatch"], int)

    def test_decimal_float_conversion(self):
        """
        Test that value error is raised when default mismatch, type is decimal and
        the type of the default is a float.

        Note:
            Floats aren't supported for Decimal types since they aren't as
            exact as Decimal for serialization/deserialization of fixed width documents.
        """
        field_name = "defaultstrmismatch"
        field_type = "string"

        config = {
            field_name: {
                "required": False,
                "type": field_type,
                "default": 52.23,
                "start_pos": 1,
                "length": 8,
                "alignment": "right",
                "padding": " ",
            },
        }

        self.assertRaisesRegex(ValueError, "^Default value for %s "\
                "is not a valid %s$" % (field_name, field_type), FixedWidth, config)

    def test_str_int_conversion(self):
        """
        Test that value error is raised when default mismatch, type is not string.
        """
        field_name = "defaultstrmismatch"
        field_type = "string"

        config = {
            field_name: {
                "required": False,
                "type": field_type,
                "default": 52.23,
                "start_pos": 1,
                "length": 8,
                "alignment": "right",
                "padding": " ",
            },
        }

        self.assertRaisesRegex(ValueError, "^Default value for %s "\
                "is not a valid %s$" % (field_name, field_type), FixedWidth, config)
