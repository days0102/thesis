''' ==================
python -O python_file
__debug__ -> False
'''

import glob
import shutil
import sys
import darshan, os
import darshan.backend.cffi_backend as darshanll
from darshan.lib.accum import log_file_count_summary_table, log_module_overview_table
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
        # print(report.metadata['job']['nprocs'])
        # print(report.metadata['job']['run_time'])
        # print(report.metadata['exe'])
        file_map = report.name_records

        # print(report.records['POSIX'][0])
        # rec_dict = report.records['POSIX'].to_df()
        # nprocs = report.metadata['job']['nprocs']

        # derived_metrics = darshanll.accumulate_records(rec_dict, 'POSIX',
        #                                                nprocs).derived_metrics
        # summary_record = darshanll.accumulate_records(rec_dict, 'POSIX',
        #                                               nprocs).summary_record
        '''
        struct darshan_derived_metrics {
            /* total bytes moved (read and write) */
            int64_t total_bytes;

            /* combined meta and rw time spent in unique files by slowest rank */
            double unique_io_total_time_by_slowest;
            /* rw time spent in unique files by slowest rank */
            double unique_rw_only_time_by_slowest;
            /* meta time spent in unique files by slowest rank */
            double unique_md_only_time_by_slowest;
            /* which rank was the slowest for unique files */
            int unique_io_slowest_rank;

            /* combined meta and rw time speint by slowest rank on shared file */
            /* Note that (unlike the unique file counters above) we cannot
            * discriminate md and rw time separately within shared files.
            */
            double shared_io_total_time_by_slowest;

            /* overall throughput, accounting for the slowest path through both
            * shared files and unique files
            */
            double agg_perf_by_slowest;
            /* overall elapsed io time, accounting for the slowest path through both
            * shared files and unique files
            */
            double agg_time_by_slowest;

            /* array of derived metrics broken down by different categories */
            struct darshan_file_category_counters
                category_counters[DARSHAN_FILE_CATEGORY_MAX];
        };
        enum darshan_file_category {
            DARSHAN_ALL_FILES = 0,
            DARSHAN_RO_FILES,
            DARSHAN_WO_FILES,
            DARSHAN_RW_FILES,
            DARSHAN_UNIQ_FILES,
            DARSHAN_SHARED_FILES,
            DARSHAN_PART_SHARED_FILES,
            DARSHAN_FILE_CATEGORY_MAX
        };
        struct darshan_file_category_counters {
            int64_t count;                   /* number of files in this category */
            int64_t total_read_volume_bytes; /* total read traffic volume */
            int64_t total_write_volume_bytes;/* total write traffic volume */
            int64_t max_read_volume_bytes;   /* maximum read traffic volume to 1 file */
            int64_t max_write_volume_bytes;  /* maximum write traffic volume to 1 file */
            int64_t total_max_offset_bytes;  /* summation of max_offsets */
            int64_t max_offset_bytes;        /* largest max_offset */
            int64_t nprocs;                  /* how many procs accessed (-1 for "all") */
        };
        '''
        # print(derived_metrics.category_counters[0].count)  # DARSHAN_ALL_FILES
        # print(derived_metrics.category_counters[0].total_read_volume_bytes
        #       )  # DARSHAN_ALL_FILES
        # print(derived_metrics.category_counters[0].max_write_volume_bytes
        #       )  # DARSHAN_ALL_FILES
        # print(derived_metrics.category_counters[1].max_read_volume_bytes)
        # print(derived_metrics.category_counters[2])
        # print(derived_metrics.category_counters[3])

        # actual_df = log_file_count_summary_table(derived_metrics=derived_metrics,
        #                                      mod_name='POSIX').df
        # print(actual_df)

        if 'STDIO' in report.records:
            df_stdio = report.records['STDIO'].to_df()
            dfs = df_stdio['counters']

            record = dfs.sum(axis=0)
            record = record.drop(['id', 'rank'])
            rec_dict = report.records['STDIO'].to_df()
            nprocs = report.metadata['job']['nprocs']

            derived_metrics = darshanll.accumulate_records(
                rec_dict, 'STDIO', nprocs).derived_metrics
            record = pd.concat([
                pd.Series({
                    'uid':
                    report.metadata['job']['uid'],
                    'nprocs':
                    report.metadata['job']['nprocs'],
                    'run_time':
                    report.metadata['job']['run_time'],
                    'exe':
                    report.metadata['exe'],
                    'STDIO_agg_perf_by_slowest':
                    derived_metrics.agg_perf_by_slowest,
                    'STDIO_TOTAL_FILES':
                    derived_metrics.category_counters[0].count,
                    # 'STDIO_TOTAL_FILES_READ_BYTES':
                    # derived_metrics.category_counters[0].
                    # total_read_volume_bytes,
                    # 'STDIO_TOTAL_FILES_WRITE_BYTES':
                    # derived_metrics.category_counters[0].
                    # total_write_volume_bytes,
                    'STDIO_READ_ONLY_FILES':
                    derived_metrics.category_counters[1].count,
                    'STDIO_WRITE_ONLY_FILES':
                    derived_metrics.category_counters[2].count,
                    'STDIO_READ_WRITE_FILES':
                    derived_metrics.category_counters[3].count,
                    'STDIO_UNIQUE_FILES':
                    derived_metrics.category_counters[4].count,
                    'STDIO_SHARE_FILES':
                    derived_metrics.category_counters[5].count,
                }),
                record
            ])

            df = df._append(record, ignore_index=True)

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

    # df = df.map(int)
    df.to_csv('stdio.csv')

    # df_p = df_p.map(int)
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