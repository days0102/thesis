'''
Author       : Outsider
Date         : 2023-12-08 11:50:52
LastEditors  : Outsider
LastEditTime : 2023-12-09 17:09:33
Description  : In User Settings Edit
FilePath     : /thesis/backend/drishti/FileApi.py
'''

import os, json


def build_directory_structure(folder_path):
    """
    构建目录结构
    """
    structure = {}
    structure['label'] = folder_path
    structure['children'] = []
    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)
        if os.path.isdir(item_path):
            structure['children'].append(build_directory_structure(item_path))
        else:
            structure['children'].append({'label': item})
    return structure


def GetDirent(path):
    return json.dumps(build_directory_structure(path)['children'])


if __name__ == "__main__":
    structure = build_directory_structure('data')
    print(structure)