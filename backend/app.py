'''
Author       : Outsider
Date         : 2023-11-27 10:43:54
LastEditors  : Outsider
LastEditTime : 2023-11-27 20:40:23
Description  : In User Settings Edit
FilePath     : \thesis\backend\app.py
'''
from flask import Flask, jsonify

app = Flask(__name__)


@app.route('/api')
def hello_world():
    return jsonify('Hello World!')


if __name__ == '__main__':

    app.run(host="0.0.0.0", port=5000, debug=True)
