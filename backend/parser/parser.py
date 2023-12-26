'''
Author       : Outsider
Date         : 2023-12-26 11:25:44
LastEditors  : Outsider
LastEditTime : 2023-12-26 11:30:42
Description  : In User Settings Edit
FilePath     : \thesis\backend\parser\parser.py
'''
import darshan
# open a Darshan log file and read all data 4

filename='data/benchmark_write_parallel_1.darshan'

with darshan.DarshanReport(filename, read_all=True) as report:
    # print the metadata dict for this log
    print("metadata: ", report.metadata)
    # print job runtime and nprocs
    print("run_time: ", report.metadata['job']['run_time'])
    print("nprocs: ", report.metadata['job']['nprocs'])
    # print modules contained in the report
    print(" modules : ", list(report.modules.keys()))
    # export POSIX module records to DataFrame and print
    posix_df = report.records[' POSIX '].to_df()
    display(posix_df)
