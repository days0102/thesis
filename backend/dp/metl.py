''' ==================
python -O python_file
__debug__ -> False
'''

import glob
import shutil
import sys, os
import darshan
import darshan.backend.cffi_backend as darshanll
from darshan.lib.accum import log_file_count_summary_table, log_module_overview_table
import pandas as pd
import colorful as cf  # ref: https://pypi.org/project/colorful/

from packaging import version

from multiprocessing import Pool, cpu_count, Process

pd.set_option('display.max_columns', None)

library_version = darshanll.get_lib_version()
if __debug__:
    print(cf.bold_blue('library_version:{0}'.format(library_version)))


def version_compatible_convert(file: str) -> str:
    convert_file = file

    if not os.path.isfile(file):
        pass

    log = darshanll.log_open(file)
    report = darshanll.log_get_job(log)
    log_version = report['metadata']['lib_ver']

    if __debug__:
        print(cf.bold_blue("{} log_version:{}".format(file, log_version)))

    if version.parse(log_version) < version.parse(library_version):
        # Check if darshan-convert is installed and available in the env PATH
        if shutil.which('darshan-convert') is None:
            print(
                cf.bold_red(
                    'Darshan file is using an old format and darshan-convert is not available in the PATH.'
                ))
            return convert_file

        # convert
        convert_file = os.path.basename(
            file.replace('.darshan', '.converted.darshan'))

        ret = os.system('darshan-convert {} {}'.format(file, convert_file))

        if ret != 0:
            print('Unable to convert .darshan file to version {}'.format(
                library_version))

    return convert_file


def excat(paths: str):
    files = []
    for path in paths:
        files.extend(glob.glob(os.path.join(path, '*.darshan')))

    df = pd.DataFrame()
    df_p = pd.DataFrame()
    df_m = pd.DataFrame()

    for file in files:
        file = version_compatible_convert(file)

        if 'POSIX' in report.records:
            df_posix = report.records['POSIX'].to_df()
            dfp = df_posix['counters']

            record = dfp.sum(axis=0)
            record = record.drop(['id', 'rank'])

            rec_dict = report.records['POSIX'].to_df()
            nprocs = report.metadata['job']['nprocs']

            derived_metrics = darshanll.accumulate_records(
                rec_dict, 'POSIX', nprocs).derived_metrics

            record = pd.concat([
                pd.Series({
                    'uid':
                    report.metadata['job']['uid'],
                    'nprocs':
                    nprocs,
                    'run_time':
                    report.metadata['job']['run_time'],
                    'exe':
                    report.metadata['exe'],
                    'POSIX_agg_perf_by_slowest':
                    derived_metrics.agg_perf_by_slowest,
                    'POSIX_TOTAL_FILES':
                    derived_metrics.category_counters[0].count,
                    # 'POSIX_TOTAL_FILES_READ_BYTES':
                    # derived_metrics.category_counters[0].
                    # total_read_volume_bytes,
                    # 'POSIX_TOTAL_FILES_WRITE_BYTES':
                    # derived_metrics.category_counters[0].
                    # total_write_volume_bytes,
                    'POSIX_READ_ONLY_FILES':
                    derived_metrics.category_counters[1].count,
                    'POSIX_WRITE_ONLY_FILES':
                    derived_metrics.category_counters[2].count,
                    'POSIX_READ_WRITE_FILES':
                    derived_metrics.category_counters[3].count,
                    'POSIX_UNIQUE_FILES':
                    derived_metrics.category_counters[4].count,
                    'POSIX_SHARE_FILES':
                    derived_metrics.category_counters[5].count,
                }),
                record
            ])

            df_p = df_p._append(record, ignore_index=True)

        if 'MPI-IO' in report.records:
            df_mpi = report.records['MPI-IO'].to_df()
            dfm = df_mpi['counters']

            record = dfm.sum(axis=0)
            record = record.drop(['id', 'rank'])

            rec_dict = report.records['MPI-IO'].to_df()
            nprocs = report.metadata['job']['nprocs']

            derived_metrics = darshanll.accumulate_records(
                rec_dict, 'MPI-IO', nprocs).derived_metrics

            record = pd.concat([
                pd.Series({
                    'uid':
                    report.metadata['job']['uid'],
                    'nprocs':
                    nprocs,
                    'run_time':
                    report.metadata['job']['run_time'],
                    'exe':
                    report.metadata['exe'],
                    'MPIIO_agg_perf_by_slowest':
                    derived_metrics.agg_perf_by_slowest,
                    'MPIIO_TOTAL_FILES':
                    derived_metrics.category_counters[0].count,
                    # 'POSIX_TOTAL_FILES_READ_BYTES':
                    # derived_metrics.category_counters[0].
                    # total_read_volume_bytes,
                    # 'POSIX_TOTAL_FILES_WRITE_BYTES':
                    # derived_metrics.category_counters[0].
                    # total_write_volume_bytes,
                    'MPIIO_READ_ONLY_FILES':
                    derived_metrics.category_counters[1].count,
                    'MPIIO_WRITE_ONLY_FILES':
                    derived_metrics.category_counters[2].count,
                    'MPIIO_READ_WRITE_FILES':
                    derived_metrics.category_counters[3].count,
                    'MPIIO_UNIQUE_FILES':
                    derived_metrics.category_counters[4].count,
                    'MPIIO_SHARE_FILES':
                    derived_metrics.category_counters[5].count,
                }),
                record
            ])

            df_m = df_m._append(record, ignore_index=True)

    # df = df.map(int)
    # df.to_csv('stdio.csv')

    df_p = df_p.map(int)
    df_p.to_csv('posix.csv')

    df_m.to_csv('mpiio.csv')


def example():
    file = '/home/lwz/thesis/backend/data/darshan.2019-12-01_031501-0/bwjenkin_ior_id10652215_11-30-17307-6832157030733066328_1.darshan'

    file = version_compatible_convert(file)

    report = darshan.DarshanReport(file)

    df = pd.DataFrame()

    if 'STDIO' in report.records:
        df_stdio = report.records['STDIO'].to_df()
        print(df_stdio['counters']['STDIO_READS'].sum())
        print(df_stdio['counters']['STDIO_BYTES_READ'].sum())
        dfs = df_stdio['counters']

        total = {}
        print(dfs.sum(axis=0))
        df = df._append(dfs.sum(axis=0), ignore_index=True)
    print(df)

def func(str):
    print(str)


if __name__ == '__main__':
    # example()
    # excat([
    #     '/home/lwz/thesis/backend/data/darshan.2019-12-01',
    #     '/home/lwz/thesis/backend/data/darshan.2019-12-02',
    #     '/home/lwz/thesis/backend/data/darshan.2019-12-03',
    #     '/home/lwz/thesis/backend/data/darshan.2019-12-04',
    #     '/home/lwz/thesis/backend/data/darshan.2019-12-05',
    # ])

    ranks = 4

    pool = Pool(processes=ranks)

    for i in pool.imap_unordered(func, ['a','b','c','r']):
        print(i)