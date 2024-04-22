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
import time

from packaging import version

from multiprocessing import Pool, cpu_count, Process
from joblib import Parallel, delayed

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


def excat(file):

    file = version_compatible_convert(file)

    report = darshan.DarshanReport(file)

    if 'POSIX' in report.records:
        df_posix = report.records['POSIX'].to_df()
        dfp = df_posix['counters']

        record = dfp.sum(axis=0)
        record = record.drop(['id', 'rank'])

        rec_dict = report.records['POSIX'].to_df()
        nprocs = report.metadata['job']['nprocs']

        derived_metrics = darshanll.accumulate_records(rec_dict, 'POSIX',
                                                       nprocs).derived_metrics

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

        return record

    return None


if __name__ == '__main__':
    # example()
    # excat([
    #     '/home/lwz/thesis/backend/data/darshan.2019-12-01',
    #     '/home/lwz/thesis/backend/data/darshan.2019-12-02',
    #     '/home/lwz/thesis/backend/data/darshan.2019-12-03',
    #     '/home/lwz/thesis/backend/data/darshan.2019-12-04',
    #     '/home/lwz/thesis/backend/data/darshan.2019-12-05',
    # ])

    paths = [
        '/home/lwz/thesis/backend/data/darshan.2019-12-01',
        '/home/lwz/thesis/backend/data/darshan.2019-12-02',
        # '/home/lwz/thesis/backend/data/darshan.2019-12-03',
        # '/home/lwz/thesis/backend/data/darshan.2019-12-04',
        # '/home/lwz/thesis/backend/data/darshan.2019-12-05',
        # '/home/lwz/thesis/backend/data/darshan.2019-12-06',
        # '/home/lwz/thesis/backend/data/darshan.2019-12-07',
        # '/home/lwz/thesis/backend/data/darshan.2019-12-08',
        # '/home/lwz/thesis/backend/data/darshan.2019-12-09',
        # '/home/lwz/thesis/backend/data/darshan.2019-12-10',
    ]

    ranks = 4

    df = pd.DataFrame()

    start = time.time()

    for path in paths:
        files = glob.glob(os.path.join(path, '*.darshan'))
        result = Parallel(n_jobs=4, prefer="threads")(delayed(excat)(file) for file in files)

        print(result)

    df.to_csv('total_posix.csv')

    end = time.time()
    print('time : ', end - start)
