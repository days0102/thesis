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

from ml import cluster

app = Flask(__name__)

df = None
tree = None
cluster_map = None


def update_golobal():
    global df, tree, cluster_map
    df, tree, cluster_map = cluster.build_hierarchy()


@app.route('/api')
def hello_world():
    return jsonify('Hello World!')


@app.route('/api/analysis', methods=['POST'])
def drishti():
    width = request.get_json().get("width")
    file = request.get_json().get("path")

    print(file)
    path = os.path.join(current_directory, 'data', file)
    if file.startswith('data'):
        path = os.path.join(current_directory, file)
    args = Argument(path)
    args.export_size = width
    analysis = Analysis(args)
    return jsonify(analysis.start())


@app.route('/api/getdirent')
def get_dirent():
    return GetDirent('data')


@app.route('/api/hierarchy')
def get_hierarchy():
    global tree, df, cluster_map
    if tree is None:
        df, tree, cluster_map = cluster.build_hierarchy()
    return jsonify(tree)


@app.route('/api/cluster/<cluster_id>/users', methods=['GET'])
def get_users(cluster_id):
    global df, tree, cluster_map
    if df is None or cluster_map is None:
        update_golobal()
    cluster_id = int(cluster_id) if cluster_id.isdigit() else cluster_id
    df_users = cluster.get_cluster_jobs(df, cluster_id, cluster_map)['uid']

    return df_users.value_counts().to_json(orient='columns')


@app.route('/api/cluster/<cluster_id>/apps', methods=['GET'])
def get_apps(cluster_id):
    global df, tree, cluster_map
    if df is None or cluster_map is None:
        update_golobal()
    cluster_id = int(cluster_id) if cluster_id.isdigit() else cluster_id
    df_apps = cluster.get_cluster_jobs(df, cluster_id,
                                       cluster_map)['short_name']
    return df_apps.value_counts().to_json(orient='columns')


@app.route('/api/cluster/<cluster_id>/percentage', methods=['GET'])
def get_percentage_coordinates(cluster_id):
    global df, tree, cluster_map
    if df is None or cluster_map is None:
        update_golobal()
    cluster_id = int(cluster_id) if cluster_id.isdigit() else cluster_id
    df_perc = cluster.get_cluster_jobs(df, cluster_id, cluster_map)

    # Select the right columns
    float_columns = [
        "POSIX_READS_PERC", "POSIX_READ_ONLY_FILES_PERC",
        "POSIX_READ_WRITE_FILES_PERC", "POSIX_WRITE_ONLY_FILES_PERC",
        "POSIX_UNIQUE_FILES_PERC"
    ]
    string_columns = ["uid", "exe", "short_name"]
    columns = float_columns + string_columns

    df_perc = df_perc[columns]

    # Fix rounding errors
    df_perc[float_columns].clip(lower=0, upper=1, inplace=True)

    # Replace names of columns with more intutitive ones
    pprint = {
        "POSIX_READS_PERC": "Read ratio (by access)",
        "POSIX_read_only_files_perc": "Read-only files (by file #)",
        "POSIX_read_write_files_perc": "Read-write files (by file #)",
        "POSIX_write_only_files_perc": "Write-only files (by file #)",
        "POSIX_unique_files_perc": "Unique files (by file #)",
        "uid": "uid",
        "exe": "exe",
        "short_name": "short_name"
    }

    df_perc = df_perc.rename(columns=pprint)

    return df_perc.to_json(orient='split', double_precision=3)


@app.route('/api/cluster/<cluster_id>/logarithmic', methods=['GET'])
def get_log_coordinates(cluster_id):
    global df, tree, cluster_map
    if df is None or cluster_map is None:
        update_golobal()
    columns = [
        "POSIX_RAW_agg_perf_by_slowest", "POSIX_RAW_TOTAL_BYTES",
        "RAW_run_time", "POSIX_RAW_TOTAL_ACCESSES", "RAW_nprocs",
        "POSIX_RAW_TOTAL_FILES", "uid", "exe", "short_name"
    ]

    cluster_id = int(cluster_id) if cluster_id.isdigit() else cluster_id
    df_log = cluster.get_cluster_jobs(df, cluster_id, cluster_map)[columns]

    # Replace names of columns with more intutitive ones
    pprint = {
        "POSIX_RAW_agg_perf_by_slowest": "I/O throughput [MiB/s]",
        "POSIX_RAW_TOTAL_BYTES": "I/O volume [GiB]",
        "RAW_run_time": "Runtime [s]",
        "POSIX_RAW_TOTAL_ACCESSES": "R/W accesses (in 1000s)",
        "RAW_nprocs": "App size (nprocs)",
        "POSIX_RAW_TOTAL_FILES": "Files (count)",
        "uid": "uid",
        "exe": "exe",
        "short_name": "short_name"
    }

    df_log = df_log.rename(columns=pprint)
    print(df_log)

    return df_log.to_json(orient='split', double_precision=3)

@app.route('/api/cluster/<cluster_id>/reads')
def get_cluster_reads(cluster_id):
    global df, tree, cluster_map
    if df is None or cluster_map is None:
        update_golobal()

    features = [
        "POSIX_SIZE_READ_0_100_PERC", "POSIX_SIZE_READ_100_1K_PERC",
        "POSIX_SIZE_READ_1K_10K_PERC", "POSIX_SIZE_READ_10K_100K_PERC",
        "POSIX_SIZE_READ_100K_1M_PERC", "POSIX_SIZE_READ_1M_4M_PERC",
        "POSIX_SIZE_READ_4M_10M_PERC", "POSIX_SIZE_READ_10M_100M_PERC",
        "POSIX_SIZE_READ_100M_1G_PERC", "POSIX_SIZE_READ_1G_PLUS_PERC"
    ]

    cluster_id = int(cluster_id) if cluster_id.isdigit() else cluster_id
    df_reads = cluster.get_cluster_jobs(df, cluster_id, cluster_map)[features]


    return df_reads.to_json(orient='values', double_precision=3)


@app.route('/api/cluster/<cluster_id>/writes')
def get_cluster_writes(cluster_id):
    global df, tree, cluster_map
    if df is None or cluster_map is None:
        update_golobal()

    features = [
        "POSIX_SIZE_WRITE_0_100_PERC", "POSIX_SIZE_WRITE_100_1K_PERC",
        "POSIX_SIZE_WRITE_1K_10K_PERC", "POSIX_SIZE_WRITE_10K_100K_PERC",
        "POSIX_SIZE_WRITE_100K_1M_PERC", "POSIX_SIZE_WRITE_1M_4M_PERC",
        "POSIX_SIZE_WRITE_4M_10M_PERC", "POSIX_SIZE_WRITE_10M_100M_PERC",
        "POSIX_SIZE_WRITE_100M_1G_PERC", "POSIX_SIZE_WRITE_1G_PLUS_PERC"
    ]

    cluster_id = int(cluster_id) if cluster_id.isdigit() else cluster_id
    df_writes = cluster.get_cluster_jobs(df, cluster_id, cluster_map)[features]

    return df_writes.to_json(orient='values', double_precision=3)


if __name__ == '__main__':

    app.run(host="0.0.0.0", port=5005, debug=True)
