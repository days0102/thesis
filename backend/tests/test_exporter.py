'''
Author       : Outsider
Date         : 2023-11-29 19:35:04
LastEditors  : Outsider
LastEditTime : 2023-11-30 09:03:06
Description  : In User Settings Edit
FilePath     : /thesis/backend/tests/test_exporter.py
'''
import unittest
import json
import sys
import os
from flask import jsonify

# 将 app 的目录添加到模块搜索路径
current_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.dirname(current_directory)
module_directory = os.path.join(parent_directory, 'drishti')
sys.path.append(module_directory)

from exporter import exporter
from args import Args


class ExporterTestCase(unittest.TestCase):  # 测试用例

    def setUp(self):  # 测试固件
        pass

    def tearDown(self):  # 测试固件
        pass

    def test_exporter(self):  # 第 1 个测试
        path = os.path.join(parent_directory, 'data',
                            'benchmark_write_parallel_1.darshan')
        args = Args(path)
        exporter(args)
        # self.assertEqual(result.data, jsonify('Hello World!').data)


if __name__ == "__main__":
    unittest.main()