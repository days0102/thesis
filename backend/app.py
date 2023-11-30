'''
Author       : Outsider
Date         : 2023-11-27 10:43:54
LastEditors  : Outsider
LastEditTime : 2023-11-30 10:44:28
Description  : In User Settings Edit
FilePath     : /thesis/backend/app.py
'''
from flask import Flask, jsonify, request
import os, sys

# 将 app 的目录添加到模块搜索路径
current_directory = os.path.dirname(os.path.abspath(__file__))
module_directory = os.path.join(current_directory, 'drishti')
sys.path.append(module_directory)
from exporter import exporter
from args import Args

app = Flask(__name__)


@app.route('/api')
def hello_world():
    return jsonify('Hello World!')


@app.route('/api/analysis', methods=['POST'])
def drishti():
    req = request.get_json().get("log")
    
    path = os.path.join(current_directory, 'data',
                        'benchmark_write_parallel_1.darshan')
    args = Args(path)
    return exporter(args)


if __name__ == '__main__':

    app.run(host="0.0.0.0", port=5000, debug=True)
