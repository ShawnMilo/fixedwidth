#!/usr/bin/env python

"""
Tests for the FixedWidth class.
"""

import unittest
from copy import deepcopy
from decimal import Decimal

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
            age=32, meal="vegetarian"
        )

        fw_string = fw_obj.line

        good = (
            "Michael   Smith                              "
            "032vegetarian          \r\n"
        )

        self.assertEquals(fw_string, good)

    def test_decimal(self):
        """
        Test a simple, valid example.
        """

        fw_config = deepcopy(SAMPLE_CONFIG)

        fw_config["cost"] = {
            "type": "decimal",
            "start_pos": 69,
            "default": Decimal("1.02093982"),
            "padding": "0",
            "end_pos": 78,
            "length": 10,
            "alignment": "right",
            "required": False,
            "precision": 4
        }

        fw_config["cost_mainframe"] = {
            "type": "decimal",
            "start_pos": 79,
            "default": Decimal("1.02093982"),
            "padding": "0",
            "end_pos": 88,
            "length": 10,
            "alignment": "right",
            "required": False,
            "precision": 4,
            "separator": None
        }

        fw_obj = FixedWidth(fw_config)
        fw_obj.update(
            last_name="Smith", first_name="Michael",
            age=32, meal="vegetarian"
        )

        fw_string = fw_obj.line

        good = (
            "Michael   Smith                              "
            "032vegetarian          00001.02090000010209\r\n"
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
            age=32, meal="vegetarian"
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
            "032vegetarian          "
        )

        values = fw_obj.data
        self.assertEquals(values["first_name"], "Michael")
        self.assertEquals(values["last_name"], "Smith")
        self.assertEquals(values["age"], 32)
        self.assertEquals(values["meal"], "vegetarian")

if __name__ == '__main__':
    unittest.main()
