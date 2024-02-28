''' ==================
python -O python_file
__debug__ -> False
'''

import glob
import shutil
import sys
import darshan, os
import darshan.backend.cffi_backend as darshanll
import pandas as pd
import colorful as cf  # ref: https://pypi.org/project/colorful/

from packaging import version

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


def excat(path: str):
    files = glob.glob(os.path.join(path, '*.darshan'))

    df = pd.DataFrame()
    df_p = pd.DataFrame()

    for file in files:
        file = version_compatible_convert(file)

        report = darshan.DarshanReport(file)

        if 'STDIO' in report.records:
            df_stdio = report.records['STDIO'].to_df()
            dfs = df_stdio['counters']

            df = df._append(dfs.sum(axis=0), ignore_index=True)

        if 'POSIX' in report.records:
            df_posix = report.records['POSIX'].to_df()
            dfp = df_posix['counters']

            print(dfp)

            df_p = df_p._append(dfp.sum(axis=0), ignore_index=True)

        if 'MPI-IO' in report.records:
            df_mpi = report.records['MPI-IO'].to_df()
            dfm = df_mpi['counters']

    df = df.map(int)
    df.to_csv('stdio.csv')

    df_p = df_p.map(int)
    df_p.to_csv('posix.csv')


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


if __name__ == '__main__':
    # example()
    excat('/home/lwz/thesis/backend/data/darshan.2019-12-01_031501-0')