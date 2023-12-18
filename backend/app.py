'''
Author       : Outsider
Date         : 2023-11-27 10:43:54
LastEditors  : Outsider
LastEditTime : 2023-12-09 19:46:10
Description  : In User Settings Edit
FilePath     : /thesis/backend/app.py
'''
from flask import Flask, jsonify, request
import os, sys

# 将 app 的目录添加到模块搜索路径
current_directory = os.path.dirname(os.path.abspath(__file__))
module_directory = os.path.join(current_directory, 'drishti')
sys.path.append(module_directory)
module_directory = os.path.join(current_directory, 'dp')
sys.path.append(module_directory)
from Analysis import Analysis
from Args import Argument
from FileApi import GetDirent

app = Flask(__name__)


@app.route('/api')
def hello_world():
    return jsonify('Hello World!')


@app.route('/api/analysis', methods=['POST'])
def drishti():
    width = request.get_json().get("width")
    file = request.get_json().get("path")

    path = os.path.join(current_directory, 'data', file)
    args = Argument(path)
    args.export_size = width
    analysis = Analysis(args)
    return jsonify(analysis.start())


@app.route('/api/getdirent')
def get_dirent():
    return GetDirent('data')


if __name__ == '__main__':

    app.run(host="0.0.0.0", port=5000, debug=True)
