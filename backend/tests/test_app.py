'''
Author       : Outsider
Date         : 2023-11-28 20:11:12
LastEditors  : Outsider
LastEditTime : 2023-11-28 20:48:34
Description  : In User Settings Edit
FilePath     : \thesis\backend\tests\test_app.py
'''
import unittest
import json
import sys
import os
from flask import jsonify

# 将 app 的目录添加到模块搜索路径
current_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.dirname(current_directory)
sys.path.append(parent_directory)

from app import hello_world
from app import app


class HelloWorldTestCase(unittest.TestCase):  # 测试用例
    def setUp(self):  # 测试固件
        pass

    def tearDown(self):  # 测试固件
        pass

    def test_helloworld(self):  # 第 1 个测试
        with app.app_context():
            # 在应用上下文中执行需要应用上下文的代码
            # 例如：调用 Flask 路由函数
            result = app.test_client().get('/api')
            self.assertEqual(result.status_code, 200)
            self.assertEqual(result.data, jsonify('Hello World!').data)


if __name__ == '__main__':
    unittest.main()