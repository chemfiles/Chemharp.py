# -*- coding=utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals
import unittest
import os

from chemfiles import logging
from chemfiles.logging import LogLevel


class TestLogging(unittest.TestCase):
    def test_level(self):
        self.assertEqual(logging.log_level(), LogLevel.WARNING)
        logging.set_log_level(LogLevel.DEBUG)
        self.assertEqual(logging.log_level(), LogLevel.DEBUG)
        logging.set_log_level(LogLevel.ERROR)

    def test_redirect(self):
        logging.log_to_file("test.log")
        self.assertTrue(os.path.isfile("test.log"))
        logging.log_to_stderr()

        os.unlink("test.log")


if __name__ == '__main__':
    unittest.main()
