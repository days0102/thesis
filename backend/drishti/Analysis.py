import os
import io
import sys
import csv
import time
import json
import shlex
import shutil
import datetime
import argparse
import subprocess

import pandas as pd

import darshan
import darshan.backend.cffi_backend as darshanll

from rich import print, box, rule
from rich.console import Console, Group
from rich.padding import Padding
from rich.text import Text
from rich.syntax import Syntax
from rich.panel import Panel
from rich.terminal_theme import TerminalTheme
from rich.terminal_theme import MONOKAI
from subprocess import call

from packaging import version

# TODO: need to verify the threashold to be between 0 and 1
# TODO: read thresholds from file

class Analysis:
    RECOMMENDATIONS = 0
    HIGH = 1
    WARN = 2
    INFO = 3
    OK = 4

    ROOT = os.path.abspath(os.path.dirname(__file__))

    TARGET_USER = 1
    TARGET_DEVELOPER = 2
    TARGET_SYSTEM = 3


    THRESHOLD_OPERATION_IMBALANCE = 0.1
    THRESHOLD_SMALL_REQUESTS = 0.1
    THRESHOLD_SMALL_REQUESTS_ABSOLUTE = 1000
    THRESHOLD_MISALIGNED_REQUESTS = 0.1
    THRESHOLD_METADATA = 0.1
    THRESHOLD_METADATA_TIME_RANK = 30  # seconds
    THRESHOLD_RANDOM_OPERATIONS = 0.2
    THRESHOLD_RANDOM_OPERATIONS_ABSOLUTE = 1000
    THRESHOLD_STRAGGLERS = 0.15
    THRESHOLD_IMBALANCE = 0.30
    THRESHOLD_INTERFACE_STDIO = 0.1
    THRESHOLD_COLLECTIVE_OPERATIONS = 0.5
    THRESHOLD_COLLECTIVE_OPERATIONS_ABSOLUTE = 1000

    INSIGHTS_STDIO_HIGH_USAGE = 'S01'
    INSIGHTS_POSIX_WRITE_COUNT_INTENSIVE = 'P01'
    INSIGHTS_POSIX_READ_COUNT_INTENSIVE = 'P02'
    INSIGHTS_POSIX_WRITE_SIZE_INTENSIVE = 'P03'
    INSIGHTS_POSIX_READ_SIZE_INTENSIVE = 'P04'
    INSIGHTS_POSIX_HIGH_SMALL_READ_REQUESTS_USAGE = 'P05'
    INSIGHTS_POSIX_HIGH_SMALL_WRITE_REQUESTS_USAGE = 'P06'
    INSIGHTS_POSIX_HIGH_MISALIGNED_MEMORY_USAGE = 'P07'
    INSIGHTS_POSIX_HIGH_MISALIGNED_FILE_USAGE = 'P08'
    INSIGHTS_POSIX_REDUNDANT_READ_USAGE = 'P09'
    INSIGHTS_POSIX_REDUNDANT_WRITE_USAGE = 'P10'
    INSIGHTS_POSIX_HIGH_RANDOM_READ_USAGE = 'P11'
    INSIGHTS_POSIX_HIGH_SEQUENTIAL_READ_USAGE = 'P12'
    INSIGHTS_POSIX_HIGH_RANDOM_WRITE_USAGE = 'P13'
    INSIGHTS_POSIX_HIGH_SEQUENTIAL_WRITE_USAGE = 'P14'
    INSIGHTS_POSIX_HIGH_SMALL_READ_REQUESTS_SHARED_FILE_USAGE = 'P15'
    INSIGHTS_POSIX_HIGH_SMALL_WRITE_REQUESTS_SHARED_FILE_USAGE = 'P16'
    INSIGHTS_POSIX_HIGH_METADATA_TIME = 'P17'
    INSIGHTS_POSIX_SIZE_IMBALANCE = 'P18'
    INSIGHTS_POSIX_TIME_IMBALANCE = 'P19'
    INSIGHTS_POSIX_INDIVIDUAL_WRITE_SIZE_IMBALANCE = 'P21'
    INSIGHTS_POSIX_INDIVIDUAL_READ_SIZE_IMBALANCE = 'P22'
    INSIGHTS_MPI_IO_NO_USAGE = 'M01'
    INSIGHTS_MPI_IO_NO_COLLECTIVE_READ_USAGE = 'M02'
    INSIGHTS_MPI_IO_NO_COLLECTIVE_WRITE_USAGE = 'M03'
    INSIGHTS_MPI_IO_COLLECTIVE_READ_USAGE = 'M04'
    INSIGHTS_MPI_IO_COLLECTIVE_WRITE_USAGE = 'M05'
    INSIGHTS_MPI_IO_BLOCKING_READ_USAGE = 'M06'
    INSIGHTS_MPI_IO_BLOCKING_WRITE_USAGE = 'M07'
    INSIGHTS_MPI_IO_AGGREGATORS_INTRA = 'M08'
    INSIGHTS_MPI_IO_AGGREGATORS_INTER = 'M09'
    INSIGHTS_MPI_IO_AGGREGATORS_OK = 'M10'

    def __init__(self, args):
        if args.export_size:
            self.console = Console(record=True, width=int(args.export_size))
        else:
            self.console = Console(record=True)

        self.csv_report = []

        self.args = args


        self.insights_operation = []
        self.insights_metadata = []
        self.insights_dxt = []

        self.insights_total = dict()

        self.insights_total[self.HIGH] = 0
        self.insights_total[self.WARN] = 0
        self.insights_total[self.RECOMMENDATIONS] = 0 

    def validate_thresholds(self):
        """
        Validate thresholds defined by the user.
        """
        assert (self.THRESHOLD_OPERATION_IMBALANCE >= 0.0
                and self.THRESHOLD_OPERATION_IMBALANCE <= 1.0)
        assert (self.THRESHOLD_SMALL_REQUESTS >= 0.0
                and self.THRESHOLD_SMALL_REQUESTS <= 1.0)
        assert (self.THRESHOLD_MISALIGNED_REQUESTS >= 0.0
                and self.THRESHOLD_MISALIGNED_REQUESTS <= 1.0)
        assert (self.THRESHOLD_METADATA >= 0.0
                and self.THRESHOLD_METADATA <= 1.0)
        assert (self.THRESHOLD_RANDOM_OPERATIONS >= 0.0
                and self.THRESHOLD_RANDOM_OPERATIONS <= 1.0)

        assert (self.THRESHOLD_METADATA_TIME_RANK >= 0.0)

    def clear():
        """
        Clear the screen with the comment call based on the operating system.
        """
        _ = call('clear' if os.name == 'posix' else 'cls')

    def convert_bytes(bytes_number):
        """
        Convert bytes into formatted string.
        """
        tags = ['bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB']

        i = 0
        double_bytes = bytes_number

        while (i < len(tags) and bytes_number >= 1024):
            double_bytes = bytes_number / 1024.0
            i = i + 1
            bytes_number = bytes_number / 1024

        return str(round(double_bytes, 2)) + ' ' + tags[i]

    def is_available(self,name):
        """Check whether `name` is on PATH and marked as executable."""

        return shutil.which(name) is not None

    def message(self,
                code,
                target,
                level,
                issue,
                recommendations=None,
                details=None):
        """
        Display the message on the screen with level, issue, and recommendation.
        """
        icon = ':arrow_forward:'

        if level in (self.HIGH, self.WARN):
            self.insights_total[level] += 1

        if level == self.HIGH:
            color = '[red]'
        elif level == self.WARN:
            color = '[orange1]'
        elif level == self.OK:
            color = '[green]'
        else:
            color = ''

        messages = [
            '{}{}{} {}'.format(color, icon,
                               ' [' + code + ']' if self.args.code else '', issue)
        ]

        if self.args.export_csv:
            self.csv_report.append(code)

        if details:
            for detail in details:
                messages.append('  {}:left_arrow_curving_right: {}'.format(
                    color, detail['message']))

        if recommendations:
            if not self.args.only_issues:
                messages.append(
                    '  [white]:left_arrow_curving_right: [b]Recommendations:[/b]'
                )

                for recommendation in recommendations:
                    messages.append('    :left_arrow_curving_right: {}'.format(
                        recommendation['message']))

                    if self.args.verbose and 'sample' in recommendation:
                        messages.append(
                            Padding(
                                Panel(recommendation['sample'],
                                      title='Solution Example Snippet',
                                      title_align='left',
                                      padding=(1, 2)), (1, 0, 1, 7)))

            self.insights_total[self.RECOMMENDATIONS] += len(recommendations)

        return Group(*messages)


    def check_log_version(self,file, log_version, library_version):
        use_file = file

        if version.parse(log_version) < version.parse('3.4.0'):
            # Check if darshan-convert is installed and available in the PATH
            if not self.is_available('darshan-convert'):
                self.console.print(
                    Panel(Padding(
                        'Darshan file is using an old format and darshan-convert is not available in the PATH.',
                        (1, 1)),
                        title='{}WARNING'.format('[orange1]'),
                        title_align='left'))

                sys.exit(os.EX_DATAERR)

            use_file = os.path.basename(
                file.replace('.darshan', '.converted.darshan'))

            self.console.print(
                Panel(Padding(
                    'Converting .darshan log from {} to 3.4.0: format: saving output file "{}" in the current working directory.'
                    .format(log_version, use_file), (1, 1)),
                    title='{}WARNING'.format('[orange1]'),
                    title_align='left'))

            if not os.path.isfile(use_file):
                ret = os.system('darshan-convert {} {}'.format(file, use_file))

                if ret != 0:
                    print('Unable to convert .darshan file to version {}'.format(
                        library_version))

        return use_file


    def start(self):
        if not os.path.isfile(self.args.darshan):
            print('Unable to open .darshan file.')

            return 'Not .darshan file.'
            # sys.exit(os.EX_NOINPUT)

        # clear()
        self.validate_thresholds()

        insights_start_time = time.time()

        log = darshanll.log_open(self.args.darshan)

        modules = darshanll.log_get_modules(log)

        information = darshanll.log_get_job(log)

        log_version = information['metadata']['lib_ver']
        library_version = darshanll.darshan.backend.cffi_backend.get_lib_version()

        # Make sure log format is of the same version
        filename = self.check_log_version(self.args.darshan, log_version, library_version)

        darshanll.log_close(log)

        darshan.enable_experimental()

        report = darshan.DarshanReport(filename)

        job = report.metadata

        #########################################################################################################################################################################

        # Check usage of STDIO, POSIX, and MPI-IO per file

        if 'STDIO' in report.records:
            df_stdio = report.records['STDIO'].to_df()

            if df_stdio:
                total_write_size_stdio = df_stdio['counters'][
                    'STDIO_BYTES_WRITTEN'].sum()
                total_read_size_stdio = df_stdio['counters'][
                    'STDIO_BYTES_READ'].sum()

                total_size_stdio = total_write_size_stdio + total_read_size_stdio
            else:
                total_size_stdio = 0
        else:
            df_stdio = None

            total_size_stdio = 0

        if 'POSIX' in report.records:
            df_posix = report.records['POSIX'].to_df()

            if df_posix:
                total_write_size_posix = df_posix['counters'][
                    'POSIX_BYTES_WRITTEN'].sum()
                total_read_size_posix = df_posix['counters'][
                    'POSIX_BYTES_READ'].sum()

                total_size_posix = total_write_size_posix + total_read_size_posix
            else:
                total_size_posix = 0
        else:
            df_posix = None

            total_size_posix = 0

        if 'MPI-IO' in report.records:
            df_mpiio = report.records['MPI-IO'].to_df()

            if df_mpiio:
                total_write_size_mpiio = df_mpiio['counters'][
                    'MPIIO_BYTES_WRITTEN'].sum()
                total_read_size_mpiio = df_mpiio['counters'][
                    'MPIIO_BYTES_READ'].sum()

                total_size_mpiio = total_write_size_mpiio + total_read_size_mpiio
            else:
                total_size_mpiio = 0
        else:
            df_mpiio = None

            total_size_mpiio = 0

        # Since POSIX will capture both POSIX-only accesses and those comming from MPI-IO, we can subtract those
        total_size_posix -= total_size_mpiio

        total_size = total_size_stdio + total_size_posix + total_size_mpiio

        assert (total_size_stdio >= 0)
        assert (total_size_posix >= 0)
        assert (total_size_mpiio >= 0)

        files = {}

        # Check interface usage for each file
        file_map = report.name_records

        total_files = len(file_map)

        total_files_stdio = 0
        total_files_posix = 0
        total_files_mpiio = 0

        for id, path in file_map.items():
            if df_stdio:
                uses_stdio = len(
                    df_stdio['counters'][(df_stdio['counters']['id'] == id)]) > 0
            else:
                uses_stdio = 0

            if df_posix:
                uses_posix = len(
                    df_posix['counters'][(df_posix['counters']['id'] == id)]) > 0
            else:
                uses_posix = 0

            if df_mpiio:
                uses_mpiio = len(
                    df_mpiio['counters'][(df_mpiio['counters']['id'] == id)]) > 0
            else:
                uses_mpiio = 0

            total_files_stdio += uses_stdio
            total_files_posix += uses_posix
            total_files_mpiio += uses_mpiio

            files[id] = {
                'path': path,
                'stdio': uses_stdio,
                'posix': uses_posix,
                'mpiio': uses_mpiio
            }

        df_posix_files = df_posix

        if total_size and total_size_stdio / total_size > self.THRESHOLD_INTERFACE_STDIO:
            issue = 'Application is using STDIO, a low-performance interface, for {:.2f}% of its data transfers ({})'.format(
                total_size_stdio / total_size * 100.0,
                self.convert_bytes(total_size_stdio))

            recommendation = [{
                'message':
                'Consider switching to a high-performance I/O interface such as MPI-IO'
            }]

            self.insights_operation.append(
                self.message(self.INSIGHTS_STDIO_HIGH_USAGE, self.TARGET_DEVELOPER, self.HIGH, issue,
                        recommendation))

        if 'MPI-IO' not in modules:
            issue = 'Application is using low-performance interface'

            recommendation = [{
                'message':
                'Consider switching to a high-performance I/O interface such as MPI-IO'
            }]

            self.insights_operation.append(
                self.message(self.INSIGHTS_MPI_IO_NO_USAGE, self.TARGET_DEVELOPER, self.WARN, issue,
                        recommendation))

        #########################################################################################################################################################################

        if 'POSIX' in report.records:
            df = report.records['POSIX'].to_df()

            #print(df)
            #print(df['counters'].columns)
            #print(df['fcounters'].columns)

            #########################################################################################################################################################################

            # Get number of write/read operations
            total_reads = df['counters']['POSIX_READS'].sum()
            total_writes = df['counters']['POSIX_WRITES'].sum()

            # Get total number of I/O operations
            total_operations = total_writes + total_reads

            # To check whether the application is write-intersive or read-intensive we only look at the POSIX level and check if the difference between reads and writes is larger than 10% (for more or less), otherwise we assume a balance
            if total_writes > total_reads and total_operations and abs(
                    total_writes - total_reads
            ) / total_operations > self.THRESHOLD_OPERATION_IMBALANCE:
                issue = 'Application is write operation intensive ({:.2f}% writes vs. {:.2f}% reads)'.format(
                    total_writes / total_operations * 100.0,
                    total_reads / total_operations * 100.0)

                self.insights_metadata.append(
                    self.message(self.INSIGHTS_POSIX_WRITE_COUNT_INTENSIVE, self.TARGET_DEVELOPER,
                           self.INFO, issue, None))

            if total_reads > total_writes and total_operations and abs(
                    total_writes - total_reads
            ) / total_operations > self.THRESHOLD_OPERATION_IMBALANCE:
                issue = 'Application is read operation intensive ({:.2f}% writes vs. {:.2f}% reads)'.format(
                    total_writes / total_operations * 100.0,
                    total_reads / total_operations * 100.0)

                self.insights_metadata.append(
                    self.message(self.INSIGHTS_POSIX_READ_COUNT_INTENSIVE, self.TARGET_DEVELOPER,
                            self.INFO, issue, None))

            total_read_size = df['counters']['POSIX_BYTES_READ'].sum()
            total_written_size = df['counters']['POSIX_BYTES_WRITTEN'].sum()

            total_size = total_written_size + total_read_size

            if total_written_size > total_read_size and abs(
                    total_written_size - total_read_size) / (
                        total_written_size +
                        total_read_size) > self.THRESHOLD_OPERATION_IMBALANCE:
                issue = 'Application is write size intensive ({:.2f}% write vs. {:.2f}% read)'.format(
                    total_written_size / (total_written_size + total_read_size) *
                    100.0, total_read_size /
                    (total_written_size + total_read_size) * 100.0)

                self.insights_metadata.append(
                    self.message(self.INSIGHTS_POSIX_WRITE_SIZE_INTENSIVE, self.TARGET_DEVELOPER,
                            self.INFO, issue, None))

            if total_read_size > total_written_size and abs(
                    total_written_size - total_read_size) / (
                        total_written_size +
                        total_read_size) > self.THRESHOLD_OPERATION_IMBALANCE:
                issue = 'Application is read size intensive ({:.2f}% write vs. {:.2f}% read)'.format(
                    total_written_size / (total_written_size + total_read_size) *
                    100.0, total_read_size /
                    (total_written_size + total_read_size) * 100.0)

                self.insights_metadata.append(
                    self.message(self.INSIGHTS_POSIX_READ_SIZE_INTENSIVE, self.TARGET_DEVELOPER,
                            self.INFO, issue, None))

            #########################################################################################################################################################################

            # Get the number of small I/O operations (less than 1 MB)
            total_reads_small = (df['counters']['POSIX_SIZE_READ_0_100'].sum() +
                                df['counters']['POSIX_SIZE_READ_100_1K'].sum() +
                                df['counters']['POSIX_SIZE_READ_1K_10K'].sum() +
                                df['counters']['POSIX_SIZE_READ_10K_100K'].sum() +
                                df['counters']['POSIX_SIZE_READ_100K_1M'].sum())

            # Get the files responsible for more than half of these accesses
            files = []

            df['counters']['INSIGHTS_POSIX_SMALL_READ'] = (
                df['counters']['POSIX_SIZE_READ_0_100'] +
                df['counters']['POSIX_SIZE_READ_100_1K'] +
                df['counters']['POSIX_SIZE_READ_1K_10K'] +
                df['counters']['POSIX_SIZE_READ_10K_100K'] +
                df['counters']['POSIX_SIZE_READ_100K_1M'])

            df['counters']['INSIGHTS_POSIX_SMALL_WRITE'] = (
                df['counters']['POSIX_SIZE_WRITE_0_100'] +
                df['counters']['POSIX_SIZE_WRITE_100_1K'] +
                df['counters']['POSIX_SIZE_WRITE_1K_10K'] +
                df['counters']['POSIX_SIZE_WRITE_10K_100K'] +
                df['counters']['POSIX_SIZE_WRITE_100K_1M'])

            detected_files = pd.DataFrame(df['counters'].groupby('id')[[
                'INSIGHTS_POSIX_SMALL_READ', 'INSIGHTS_POSIX_SMALL_WRITE'
            ]].sum()).reset_index()
            detected_files.columns = ['id', 'total_reads', 'total_writes']
            detected_files.loc[:, 'id'] = detected_files.loc[:, 'id'].astype(str)

            if total_reads_small and total_reads_small / total_reads > self.THRESHOLD_SMALL_REQUESTS and total_reads_small > self.THRESHOLD_SMALL_REQUESTS_ABSOLUTE:
                issue = 'Application issues a high number ({}) of small read requests (i.e., < 1MB) which represents {:.2f}% of all read requests'.format(
                    total_reads_small, total_reads_small / total_reads * 100.0)

                detail = []
                recommendation = []

                for index, row in detected_files.iterrows():
                    if row['total_reads'] > (total_reads *
                                            self.THRESHOLD_SMALL_REQUESTS / 2):
                        detail.append({
                            'message':
                            '{} ({:.2f}%) small read requests are to "{}"'.format(
                                row['total_reads'],
                                row['total_reads'] / total_reads * 100.0,
                                file_map[int(row['id'])] if self.args.full_path else
                                os.path.basename(file_map[int(row['id'])]))
                        })

                recommendation.append({
                    'message':
                    'Consider buffering read operations into larger more contiguous ones'
                })

                if 'MPI-IO' in modules:
                    recommendation.append({
                        'message':
                        'Since the appplication already uses MPI-IO, consider using collective I/O calls (e.g. MPI_File_read_all() or MPI_File_read_at_all()) to aggregate requests into larger ones',
                        'sample':
                        Syntax.from_path(os.path.join(
                            self.ROOT, 'snippets/mpi-io-collective-read.c'),
                                        line_numbers=True,
                                        background_color='default')
                    })
                else:
                    recommendation.append({
                        'message':
                        'Application does not use MPI-IO for operations, consider use this interface instead to harness collective operations'
                    })

                self.insights_operation.append(
                    self.message(self.INSIGHTS_POSIX_HIGH_SMALL_WRITE_REQUESTS_USAGE,
                            self.TARGET_DEVELOPER, self.HIGH, issue, recommendation, detail))

            # Get the number of small I/O operations (less than the stripe size)
            total_writes_small = (
                df['counters']['POSIX_SIZE_WRITE_0_100'].sum() +
                df['counters']['POSIX_SIZE_WRITE_100_1K'].sum() +
                df['counters']['POSIX_SIZE_WRITE_1K_10K'].sum() +
                df['counters']['POSIX_SIZE_WRITE_10K_100K'].sum() +
                df['counters']['POSIX_SIZE_WRITE_100K_1M'].sum())

            if total_writes_small and total_writes_small / total_writes > self.THRESHOLD_SMALL_REQUESTS and total_writes_small > self.THRESHOLD_SMALL_REQUESTS_ABSOLUTE:
                issue = 'Application issues a high number ({}) of small write requests (i.e., < 1MB) which represents {:.2f}% of all write requests'.format(
                    total_writes_small, total_writes_small / total_writes * 100.0)

                detail = []
                recommendation = []

                for index, row in detected_files.iterrows():
                    if row['total_writes'] > (total_writes *
                                            self.THRESHOLD_SMALL_REQUESTS / 2):
                        detail.append({
                            'message':
                            '{} ({:.2f}%) small write requests are to "{}"'.format(
                                row['total_writes'],
                                row['total_writes'] / total_writes * 100.0,
                                file_map[int(row['id'])] if self.args.full_path else
                                os.path.basename(file_map[int(row['id'])]))
                        })

                recommendation.append({
                    'message':
                    'Consider buffering write operations into larger more contiguous ones'
                })

                if 'MPI-IO' in modules:
                    recommendation.append({
                        'message':
                        'Since the application already uses MPI-IO, consider using collective I/O calls (e.g. MPI_File_write_all() or MPI_File_write_at_all()) to aggregate requests into larger ones',
                        'sample':
                        Syntax.from_path(os.path.join(
                            self.ROOT, 'snippets/mpi-io-collective-write.c'),
                                        line_numbers=True,
                                        background_color='default')
                    })
                else:
                    recommendation.append({
                        'message':
                        'Application does not use MPI-IO for operations, consider use this interface instead to harness collective operations'
                    })

                self.insights_operation.append(
                    self.message(self.INSIGHTS_POSIX_HIGH_SMALL_READ_REQUESTS_USAGE,
                            self.TARGET_DEVELOPER, self.HIGH, issue, recommendation, detail))

            #########################################################################################################################################################################

            # How many requests are misaligned?

            total_mem_not_aligned = df['counters']['POSIX_MEM_NOT_ALIGNED'].sum()
            total_file_not_aligned = df['counters']['POSIX_FILE_NOT_ALIGNED'].sum()

            if total_operations and total_mem_not_aligned / total_operations > self.THRESHOLD_MISALIGNED_REQUESTS:
                issue = 'Application has a high number ({:.2f}%) of misaligned memory requests'.format(
                    total_mem_not_aligned / total_operations * 100.0)

                self.insights_metadata.append(
                    self.message(self.INSIGHTS_POSIX_HIGH_MISALIGNED_MEMORY_USAGE,
                            self.TARGET_DEVELOPER, self.HIGH, issue, None))

            if total_operations and total_file_not_aligned / total_operations > self.THRESHOLD_MISALIGNED_REQUESTS:
                issue = 'Application issues a high number ({:.2f}%) of misaligned file requests'.format(
                    total_file_not_aligned / total_operations * 100.0)

                recommendation = [{
                    'message':
                    'Consider aligning the requests to the file system block boundaries'
                }]

                if 'HF5' in modules:
                    recommendation.append(
                        {
                            'message':
                            'Since the appplication uses HDF5, consider using H5Pset_alignment() in a file access property list',
                            'sample':
                            Syntax.from_path(os.path.join(
                                self.ROOT, 'snippets/hdf5-alignment.c'),
                                            line_numbers=True,
                                            background_color='default')
                        }, {
                            'message':
                            'Any file object greater than or equal in size to threshold bytes will be aligned on an address which is a multiple of alignment'
                        })

                if 'LUSTRE' in modules:
                    recommendation.append({
                        'message':
                        'Consider using a Lustre alignment that matches the file system stripe configuration',
                        'sample':
                        Syntax.from_path(os.path.join(
                            self.ROOT, 'snippets/lustre-striping.bash'),
                                        line_numbers=True,
                                        background_color='default')
                    })

                self.insights_metadata.append(
                    self.message(self.INSIGHTS_POSIX_HIGH_MISALIGNED_FILE_USAGE,
                            self.TARGET_DEVELOPER, self.HIGH, issue, recommendation))

            #########################################################################################################################################################################

            # Redundant read-traffic (based on Phill)
            # POSIX_MAX_BYTE_READ (Highest offset in the file that was read)
            max_read_offset = df['counters']['POSIX_MAX_BYTE_READ'].max()

            if max_read_offset > total_read_size:
                issue = 'Application might have redundant read traffic (more data read than the highest offset)'

                self.insights_metadata.append(
                    self.message(self.INSIGHTS_POSIX_REDUNDANT_READ_USAGE, self.TARGET_DEVELOPER,
                            self.WARN, issue, None))

            max_write_offset = df['counters']['POSIX_MAX_BYTE_WRITTEN'].max()

            if max_write_offset > total_written_size:
                issue = 'Application might have redundant write traffic (more data written than the highest offset)'

                self.insights_metadata.append(
                    self.message(self.INSIGHTS_POSIX_REDUNDANT_WRITE_USAGE, self.TARGET_DEVELOPER,
                            self.WARN, issue, None))

            #########################################################################################################################################################################

            # Check for a lot of random operations

            read_consecutive = df['counters']['POSIX_CONSEC_READS'].sum()
            #print('READ Consecutive: {} ({:.2f}%)'.format(read_consecutive, read_consecutive / total_reads * 100))

            read_sequential = df['counters']['POSIX_SEQ_READS'].sum()
            read_sequential -= read_consecutive
            #print('READ Sequential: {} ({:.2f}%)'.format(read_sequential, read_sequential / total_reads * 100))

            read_random = total_reads - read_consecutive - read_sequential
            #print('READ Random: {} ({:.2f}%)'.format(read_random, read_random / total_reads * 100))

            if total_reads:
                if read_random and read_random / total_reads > self.THRESHOLD_RANDOM_OPERATIONS and read_random > self.THRESHOLD_RANDOM_OPERATIONS_ABSOLUTE:
                    issue = 'Application is issuing a high number ({}) of random read operations ({:.2f}%)'.format(
                        read_random, read_random / total_reads * 100.0)

                    recommendation = [{
                        'message':
                        'Consider changing your data model to have consecutive or sequential reads'
                    }]

                    self.insights_operation.append(
                        self.message(self.INSIGHTS_POSIX_HIGH_RANDOM_READ_USAGE,
                                self.TARGET_DEVELOPER, self.HIGH, issue, recommendation))
                else:
                    issue = 'Application mostly uses consecutive ({:.2f}%) and sequential ({:.2f}%) read requests'.format(
                        read_consecutive / total_reads * 100.0,
                        read_sequential / total_reads * 100.0)

                    self.insights_operation.append(
                        self.message(self.INSIGHTS_POSIX_HIGH_SEQUENTIAL_READ_USAGE,
                                self.TARGET_DEVELOPER, self.OK, issue, None))

            write_consecutive = df['counters']['POSIX_CONSEC_WRITES'].sum()
            #print('WRITE Consecutive: {} ({:.2f}%)'.format(write_consecutive, write_consecutive / total_writes * 100))

            write_sequential = df['counters']['POSIX_SEQ_WRITES'].sum()
            write_sequential -= write_consecutive
            #print('WRITE Sequential: {} ({:.2f}%)'.format(write_sequential, write_sequential / total_writes * 100))

            write_random = total_writes - write_consecutive - write_sequential
            #print('WRITE Random: {} ({:.2f}%)'.format(write_random, write_random / total_writes * 100))

            if total_writes:
                if write_random and write_random / total_writes > self.THRESHOLD_RANDOM_OPERATIONS and write_random > self.THRESHOLD_RANDOM_OPERATIONS_ABSOLUTE:
                    issue = 'Application is issuing a high number ({}) of random write operations ({:.2f}%)'.format(
                        write_random, write_random / total_writes * 100.0)

                    recommendation = [{
                        'message':
                        'Consider changing your data model to have consecutive or sequential writes'
                    }]

                    self.insights_operation.append(
                        self.message(self.INSIGHTS_POSIX_HIGH_RANDOM_WRITE_USAGE,
                                self.TARGET_DEVELOPER, self.HIGH, issue, recommendation))
                else:
                    issue = 'Application mostly uses consecutive ({:.2f}%) and sequential ({:.2f}%) write requests'.format(
                        write_consecutive / total_writes * 100.0,
                        write_sequential / total_writes * 100.0)

                    self.insights_operation.append(
                        self.message(self.INSIGHTS_POSIX_HIGH_SEQUENTIAL_WRITE_USAGE,
                                self.TARGET_DEVELOPER, self.OK, issue, None))

            #########################################################################################################################################################################

            # Shared file with small operations
            # print(df['counters'].loc[(df['counters']['rank'] == -1)])

            shared_files = df['counters'].loc[(df['counters']['rank'] == -1)]

            shared_files = shared_files.assign(id=lambda d: d['id'].astype(str))

            if not shared_files.empty:
                total_shared_reads = shared_files['POSIX_READS'].sum()
                total_shared_reads_small = (
                    shared_files['POSIX_SIZE_READ_0_100'].sum() +
                    shared_files['POSIX_SIZE_READ_100_1K'].sum() +
                    shared_files['POSIX_SIZE_READ_1K_10K'].sum() +
                    shared_files['POSIX_SIZE_READ_10K_100K'].sum() +
                    shared_files['POSIX_SIZE_READ_100K_1M'].sum())

                shared_files['INSIGHTS_POSIX_SMALL_READS'] = (
                    shared_files['POSIX_SIZE_READ_0_100'] +
                    shared_files['POSIX_SIZE_READ_100_1K'] +
                    shared_files['POSIX_SIZE_READ_1K_10K'] +
                    shared_files['POSIX_SIZE_READ_10K_100K'] +
                    shared_files['POSIX_SIZE_READ_100K_1M'])

                if total_shared_reads and total_shared_reads_small / total_shared_reads > self.THRESHOLD_SMALL_REQUESTS and total_shared_reads_small > self.THRESHOLD_SMALL_REQUESTS_ABSOLUTE:
                    issue = 'Application issues a high number ({}) of small read requests to a shared file (i.e., < 1MB) which represents {:.2f}% of all shared file read requests'.format(
                        total_shared_reads_small,
                        total_shared_reads_small / total_shared_reads * 100.0)

                    detail = []

                    for index, row in shared_files.iterrows():
                        if row['INSIGHTS_POSIX_SMALL_READS'] > (
                                total_shared_reads * self.THRESHOLD_SMALL_REQUESTS / 2):
                            detail.append({
                                'message':
                                '{} ({:.2f}%) small read requests are to "{}"'.
                                format(
                                    row['INSIGHTS_POSIX_SMALL_READS'],
                                    row['INSIGHTS_POSIX_SMALL_READS'] /
                                    total_shared_reads * 100.0,
                                    file_map[int(row['id'])] if self.args.full_path else
                                    os.path.basename(file_map[int(row['id'])]))
                            })

                    recommendation = [{
                        'message':
                        'Consider coalesceing read requests into larger more contiguous ones using MPI-IO collective operations',
                        'sample':
                        Syntax.from_path(os.path.join(
                            self.ROOT, 'snippets/mpi-io-collective-read.c'),
                                        line_numbers=True,
                                        background_color='default')
                    }]

                    self.insights_operation.append(
                        self.message(
                            self.INSIGHTS_POSIX_HIGH_SMALL_READ_REQUESTS_SHARED_FILE_USAGE,
                            self.TARGET_DEVELOPER, self.HIGH, issue, recommendation, detail))

                total_shared_writes = shared_files['POSIX_WRITES'].sum()
                total_shared_writes_small = (
                    shared_files['POSIX_SIZE_WRITE_0_100'].sum() +
                    shared_files['POSIX_SIZE_WRITE_100_1K'].sum() +
                    shared_files['POSIX_SIZE_WRITE_1K_10K'].sum() +
                    shared_files['POSIX_SIZE_WRITE_10K_100K'].sum() +
                    shared_files['POSIX_SIZE_WRITE_100K_1M'].sum())

                shared_files['INSIGHTS_POSIX_SMALL_WRITES'] = (
                    shared_files['POSIX_SIZE_WRITE_0_100'] +
                    shared_files['POSIX_SIZE_WRITE_100_1K'] +
                    shared_files['POSIX_SIZE_WRITE_1K_10K'] +
                    shared_files['POSIX_SIZE_WRITE_10K_100K'] +
                    shared_files['POSIX_SIZE_WRITE_100K_1M'])

                if total_shared_writes and total_shared_writes_small / total_shared_writes > self.THRESHOLD_SMALL_REQUESTS and total_shared_writes_small > self.THRESHOLD_SMALL_REQUESTS_ABSOLUTE:
                    issue = 'Application issues a high number ({}) of small write requests to a shared file (i.e., < 1MB) which represents {:.2f}% of all shared file write requests'.format(
                        total_shared_writes_small,
                        total_shared_writes_small / total_shared_writes * 100.0)

                    detail = []

                    for index, row in shared_files.iterrows():
                        if row['INSIGHTS_POSIX_SMALL_WRITES'] > (
                                total_shared_writes * self.THRESHOLD_SMALL_REQUESTS /
                                2):
                            detail.append({
                                'message':
                                '{} ({:.2f}%) small writes requests are to "{}"'.
                                format(
                                    row['INSIGHTS_POSIX_SMALL_WRITES'],
                                    row['INSIGHTS_POSIX_SMALL_WRITES'] /
                                    total_shared_writes * 100.0,
                                    file_map[int(row['id'])] if self.args.full_path else
                                    os.path.basename(file_map[int(row['id'])]))
                            })

                    recommendation = [{
                        'message':
                        'Consider coalescing write requests into larger more contiguous ones using MPI-IO collective operations',
                        'sample':
                        Syntax.from_path(os.path.join(
                            self.ROOT, 'snippets/mpi-io-collective-write.c'),
                                        line_numbers=True,
                                        background_color='default')
                    }]

                    self.insights_operation.append(
                        self.message(
                            self.INSIGHTS_POSIX_HIGH_SMALL_WRITE_REQUESTS_SHARED_FILE_USAGE,
                            self.TARGET_DEVELOPER, self.HIGH, issue, recommendation, detail))

            #########################################################################################################################################################################

            has_long_metadata = df['fcounters'][(
                df['fcounters']['POSIX_F_META_TIME']
                > self.THRESHOLD_METADATA_TIME_RANK)]

            if not has_long_metadata.empty:
                issue = 'There are {} ranks where metadata operations take over {} seconds'.format(
                    len(has_long_metadata), self.THRESHOLD_METADATA_TIME_RANK)

                recommendation = [{
                    'message':
                    'Attempt to combine files, reduce, or cache metadata operations'
                }]

                if 'HF5' in modules:
                    recommendation.append(
                        {
                            'message':
                            'Since your appplication uses HDF5, try enabling collective metadata calls with H5Pset_coll_metadata_write() and H5Pset_all_coll_metadata_ops()',
                            'sample':
                            Syntax.from_path(os.path.join(
                                self.ROOT, 'snippets/hdf5-collective-metadata.c'),
                                            line_numbers=True,
                                            background_color='default')
                        }, {
                            'message':
                            'Since your appplication uses HDF5, try using metadata cache to defer metadata operations',
                            'sample':
                            Syntax.from_path(os.path.join(self.ROOT,
                                                        'snippets/hdf5-cache.c'),
                                            line_numbers=True,
                                            background_color='default')
                        })

                self.insights_metadata.append(
                    self.message(self.INSIGHTS_POSIX_HIGH_METADATA_TIME, self.TARGET_DEVELOPER,
                            self.HIGH, issue, recommendation))

            # We already have a single line for each shared-file access
            # To check for stragglers, we can check the difference between the

            # POSIX_FASTEST_RANK_BYTES
            # POSIX_SLOWEST_RANK_BYTES
            # POSIX_F_VARIANCE_RANK_BYTES

            stragglers_count = 0

            shared_files = shared_files.assign(id=lambda d: d['id'].astype(str))

            # Get the files responsible
            detected_files = []

            for index, row in shared_files.iterrows():
                total_transfer_size = row['POSIX_BYTES_WRITTEN'] + row[
                    'POSIX_BYTES_READ']

                if total_transfer_size and abs(
                        row['POSIX_SLOWEST_RANK_BYTES'] -
                        row['POSIX_FASTEST_RANK_BYTES']
                ) / total_transfer_size > self.THRESHOLD_STRAGGLERS:
                    stragglers_count += 1

                    detected_files.append([
                        row['id'],
                        abs(row['POSIX_SLOWEST_RANK_BYTES'] -
                            row['POSIX_FASTEST_RANK_BYTES']) /
                        total_transfer_size * 100
                    ])

            if stragglers_count:
                issue = 'Detected data transfer imbalance caused by stragglers when accessing {} shared file.'.format(
                    stragglers_count)

                detail = []

                for file in detected_files:
                    detail.append({
                        'message':
                        'Load imbalance of {:.2f}% detected while accessing "{}"'.
                        format(
                            file[1], file_map[int(file[0])] if self.args.full_path else
                            os.path.basename(file_map[int(file[0])]))
                    })

                recommendation = [{
                    'message':
                    'Consider better balancing the data transfer between the application ranks'
                }, {
                    'message':
                    'Consider tuning how your data is distributed in the file system by changing the stripe size and count',
                    'sample':
                    Syntax.from_path(os.path.join(self.ROOT,
                                                'snippets/lustre-striping.bash'),
                                    line_numbers=True,
                                    background_color='default')
                }]

                self.insights_operation.append(
                    self.message(self.INSIGHTS_POSIX_SIZE_IMBALANCE, self.TARGET_USER, self.HIGH,
                            issue, recommendation, detail))

            # POSIX_F_FASTEST_RANK_TIME
            # POSIX_F_SLOWEST_RANK_TIME
            # POSIX_F_VARIANCE_RANK_TIME

            shared_files_times = df['fcounters'].loc[(
                df['fcounters']['rank'] == -1)]

            # Get the files responsible
            detected_files = []

            stragglers_count = 0
            stragglers_imbalance = {}

            shared_files_times = shared_files_times.assign(
                id=lambda d: d['id'].astype(str))

            for index, row in shared_files_times.iterrows():
                total_transfer_time = row['POSIX_F_WRITE_TIME'] + row[
                    'POSIX_F_READ_TIME'] + row['POSIX_F_META_TIME']

                if total_transfer_time and abs(
                        row['POSIX_F_SLOWEST_RANK_TIME'] -
                        row['POSIX_F_FASTEST_RANK_TIME']
                ) / total_transfer_time > self.THRESHOLD_STRAGGLERS:
                    stragglers_count += 1

                    detected_files.append([
                        row['id'],
                        abs(row['POSIX_F_SLOWEST_RANK_TIME'] -
                            row['POSIX_F_FASTEST_RANK_TIME']) /
                        total_transfer_time * 100
                    ])

            if stragglers_count:
                issue = 'Detected time imbalance caused by stragglers when accessing {} shared file.'.format(
                    stragglers_count)

                detail = []

                for file in detected_files:
                    detail.append({
                        'message':
                        'Load imbalance of {:.2f}% detected while accessing "{}"'.
                        format(
                            file[1], file_map[int(file[0])] if self.args.full_path else
                            os.path.basename(file_map[int(file[0])]))
                    })

                recommendation = [
                    {
                        'message':
                        'Consider better distributing the data in the parallel file system'  # needs to review what suggestion to give
                    },
                    {
                        'message':
                        'Consider tuning how your data is distributed in the file system by changing the stripe size and count',
                        'sample':
                        Syntax.from_path(os.path.join(
                            self.ROOT, 'snippets/lustre-striping.bash'),
                                        line_numbers=True,
                                        background_color='default')
                    }
                ]

                self.insights_operation.append(
                    self.message(self.INSIGHTS_POSIX_TIME_IMBALANCE, self.TARGET_USER, self.HIGH,
                            issue, recommendation, detail))

            aggregated = df['counters'].loc[(df['counters']['rank'] != -1)][[
                'rank', 'id', 'POSIX_BYTES_WRITTEN', 'POSIX_BYTES_READ'
            ]].groupby('id', as_index=False).agg({
                'rank':
                'nunique',
                'POSIX_BYTES_WRITTEN': ['sum', 'min', 'max'],
                'POSIX_BYTES_READ': ['sum', 'min', 'max']
            })

            aggregated.columns = list(map('_'.join, aggregated.columns.values))

            aggregated = aggregated.assign(id=lambda d: d['id_'].astype(str))

            # Get the files responsible
            imbalance_count = 0

            detected_files = []

            for index, row in aggregated.iterrows():
                if row['POSIX_BYTES_WRITTEN_max'] and abs(
                        row['POSIX_BYTES_WRITTEN_max'] -
                        row['POSIX_BYTES_WRITTEN_min']
                ) / row['POSIX_BYTES_WRITTEN_max'] > self.THRESHOLD_IMBALANCE:
                    imbalance_count += 1

                    detected_files.append([
                        row['id'],
                        abs(row['POSIX_BYTES_WRITTEN_max'] -
                            row['POSIX_BYTES_WRITTEN_min']) /
                        row['POSIX_BYTES_WRITTEN_max'] * 100
                    ])

            if imbalance_count:
                issue = 'Detected write imbalance when accessing {} individual files'.format(
                    imbalance_count)

                detail = []

                for file in detected_files:
                    detail.append({
                        'message':
                        'Load imbalance of {:.2f}% detected while accessing "{}"'.
                        format(
                            file[1], file_map[int(file[0])] if self.args.full_path else
                            os.path.basename(file_map[int(file[0])]))
                    })

                recommendation = [{
                    'message':
                    'Consider better balancing the data transfer between the application ranks'
                }, {
                    'message':
                    'Consider tuning the stripe size and count to better distribute the data',
                    'sample':
                    Syntax.from_path(os.path.join(self.ROOT,
                                                'snippets/lustre-striping.bash'),
                                    line_numbers=True,
                                    background_color='default')
                }, {
                    'message':
                    'If the application uses netCDF and HDF5 double-check the need to set NO_FILL values',
                    'sample':
                    Syntax.from_path(os.path.join(
                        self.ROOT, 'snippets/pnetcdf-hdf5-no-fill.c'),
                                    line_numbers=True,
                                    background_color='default')
                }, {
                    'message':
                    'If rank 0 is the only one opening the file, consider using MPI-IO collectives'
                }]

                self.insights_operation.append(
                    self.message(self.INSIGHTS_POSIX_INDIVIDUAL_WRITE_SIZE_IMBALANCE,
                            self.TARGET_DEVELOPER, self.HIGH, issue, recommendation, detail))

            imbalance_count = 0

            detected_files = []

            for index, row in aggregated.iterrows():
                if row['POSIX_BYTES_READ_max'] and abs(
                        row['POSIX_BYTES_READ_max'] - row['POSIX_BYTES_READ_min']
                ) / row['POSIX_BYTES_READ_max'] > self.THRESHOLD_IMBALANCE:
                    imbalance_count += 1

                    detected_files.append([
                        row['id'],
                        abs(row['POSIX_BYTES_READ_max'] -
                            row['POSIX_BYTES_READ_min']) /
                        row['POSIX_BYTES_READ_max'] * 100
                    ])

            if imbalance_count:
                issue = 'Detected read imbalance when accessing {} individual files.'.format(
                    imbalance_count)

                detail = []

                for file in detected_files:
                    detail.append({
                        'message':
                        'Load imbalance of {:.2f}% detected while accessing "{}"'.
                        format(
                            file[1], file_map[int(file[0])] if self.args.full_path else
                            os.path.basename(file_map[int(file[0])]))
                    })

                recommendation = [{
                    'message':
                    'Consider better balancing the data transfer between the application ranks'
                }, {
                    'message':
                    'Consider tuning the stripe size and count to better distribute the data',
                    'sample':
                    Syntax.from_path(os.path.join(self.ROOT,
                                                'snippets/lustre-striping.bash'),
                                    line_numbers=True,
                                    background_color='default')
                }, {
                    'message':
                    'If the application uses netCDF and HDF5 double-check the need to set NO_FILL values',
                    'sample':
                    Syntax.from_path(os.path.join(
                        self.ROOT, 'snippets/pnetcdf-hdf5-no-fill.c'),
                                    line_numbers=True,
                                    background_color='default')
                }, {
                    'message':
                    'If rank 0 is the only one opening the file, consider using MPI-IO collectives'
                }]

                self.insights_operation.append(
                    self.message(self.INSIGHTS_POSIX_INDIVIDUAL_READ_SIZE_IMBALANCE,
                            self.TARGET_DEVELOPER, self.HIGH, issue, recommendation, detail))

        #########################################################################################################################################################################

        if 'MPI-IO' in report.records:
            # Check if application uses MPI-IO and collective operations
            df_mpiio = report.records['MPI-IO'].to_df()

            df_mpiio['counters'] = df_mpiio['counters'].assign(
                id=lambda d: d['id'].astype(str))

            #print(df_mpiio)

            # Get the files responsible
            detected_files = []

            df_mpiio_collective_reads = df_mpiio[
                'counters']  #.loc[(df_mpiio['counters']['MPIIO_COLL_READS'] > 0)]

            total_mpiio_read_operations = df_mpiio['counters'][
                'MPIIO_INDEP_READS'].sum(
                ) + df_mpiio['counters']['MPIIO_COLL_READS'].sum()

            if df_mpiio['counters']['MPIIO_COLL_READS'].sum() == 0:
                if total_mpiio_read_operations and total_mpiio_read_operations > self.THRESHOLD_COLLECTIVE_OPERATIONS_ABSOLUTE:
                    issue = 'Application uses MPI-IO but it does not use collective read operations, instead it issues {} ({:.2f}%) independent read calls'.format(
                        df_mpiio['counters']['MPIIO_INDEP_READS'].sum(),
                        df_mpiio['counters']['MPIIO_INDEP_READS'].sum() /
                        (total_mpiio_read_operations) * 100)

                    detail = []

                    files = pd.DataFrame(
                        df_mpiio_collective_reads.groupby(
                            'id').sum()).reset_index()

                    for index, row in df_mpiio_collective_reads.iterrows():
                        if (row['MPIIO_INDEP_READS'] + row['MPIIO_INDEP_WRITES']
                            ) and row['MPIIO_INDEP_READS'] / (
                                row['MPIIO_INDEP_READS'] +
                                row['MPIIO_INDEP_WRITES']
                            ) > self.THRESHOLD_COLLECTIVE_OPERATIONS and (
                                row['MPIIO_INDEP_READS'] +
                                row['MPIIO_INDEP_WRITES']
                            ) > self.THRESHOLD_COLLECTIVE_OPERATIONS_ABSOLUTE:
                            detail.append({
                                'message':
                                '{} ({}%) of independent reads to "{}"'.format(
                                    row['MPIIO_INDEP_READS'],
                                    row['MPIIO_INDEP_READS'] /
                                    (row['MPIIO_INDEP_READS'] +
                                    row['MPIIO_INDEP_WRITES']) * 100,
                                    file_map[int(row['id'])] if self.args.full_path else
                                    os.path.basename(file_map[int(row['id'])]))
                            })

                    recommendation = [{
                        'message':
                        'Use collective read operations (e.g. MPI_File_read_all() or MPI_File_read_at_all()) and set one aggregator per compute node',
                        'sample':
                        Syntax.from_path(os.path.join(
                            self.ROOT, 'snippets/mpi-io-collective-read.c'),
                                        line_numbers=True,
                                        background_color='default')
                    }]

                    self.insights_operation.append(
                        self.message(self.INSIGHTS_MPI_IO_NO_COLLECTIVE_READ_USAGE,
                                self.TARGET_DEVELOPER, self.HIGH, issue, recommendation,
                                detail))
            else:
                issue = 'Application uses MPI-IO and read data using {} ({:.2f}%) collective operations'.format(
                    df_mpiio['counters']['MPIIO_COLL_READS'].sum(),
                    df_mpiio['counters']['MPIIO_COLL_READS'].sum() /
                    (df_mpiio['counters']['MPIIO_INDEP_READS'].sum() +
                    df_mpiio['counters']['MPIIO_COLL_READS'].sum()) * 100)

                self.insights_operation.append(
                    self.message(self.INSIGHTS_MPI_IO_COLLECTIVE_READ_USAGE,
                            self.TARGET_DEVELOPER, self.OK, issue))

            df_mpiio_collective_writes = df_mpiio[
                'counters']  #.loc[(df_mpiio['counters']['MPIIO_COLL_WRITES'] > 0)]

            total_mpiio_write_operations = df_mpiio['counters'][
                'MPIIO_INDEP_WRITES'].sum(
                ) + df_mpiio['counters']['MPIIO_COLL_WRITES'].sum()

            if df_mpiio['counters']['MPIIO_COLL_WRITES'].sum() == 0:
                if total_mpiio_write_operations and total_mpiio_write_operations > self.THRESHOLD_COLLECTIVE_OPERATIONS_ABSOLUTE:
                    issue = 'Application uses MPI-IO but it does not use collective write operations, instead it issues {} ({:.2f}%) independent write calls'.format(
                        df_mpiio['counters']['MPIIO_INDEP_WRITES'].sum(),
                        df_mpiio['counters']['MPIIO_INDEP_WRITES'].sum() /
                        (total_mpiio_write_operations) * 100)

                    detail = []

                    files = pd.DataFrame(
                        df_mpiio_collective_writes.groupby(
                            'id').sum()).reset_index()

                    for index, row in df_mpiio_collective_writes.iterrows():
                        if (row['MPIIO_INDEP_READS'] + row['MPIIO_INDEP_WRITES']
                            ) and row['MPIIO_INDEP_WRITES'] / (
                                row['MPIIO_INDEP_READS'] +
                                row['MPIIO_INDEP_WRITES']
                            ) > self.THRESHOLD_COLLECTIVE_OPERATIONS and (
                                row['MPIIO_INDEP_READS'] +
                                row['MPIIO_INDEP_WRITES']
                            ) > self.THRESHOLD_COLLECTIVE_OPERATIONS_ABSOLUTE:
                            detail.append({
                                'message':
                                '{} ({}%) independent writes to "{}"'.format(
                                    row['MPIIO_INDEP_WRITES'],
                                    row['MPIIO_INDEP_WRITES'] /
                                    (row['MPIIO_INDEP_READS'] +
                                    row['MPIIO_INDEP_WRITES']) * 100,
                                    file_map[int(row['id'])] if self.args.full_path else
                                    os.path.basename(file_map[int(row['id'])]))
                            })

                    recommendation = [{
                        'message':
                        'Use collective write operations (e.g. MPI_File_write_all() or MPI_File_write_at_all()) and set one aggregator per compute node',
                        'sample':
                        Syntax.from_path(os.path.join(
                            self.ROOT, 'snippets/mpi-io-collective-write.c'),
                                        line_numbers=True,
                                        background_color='default')
                    }]

                    self.self.insights_operation.append(
                        self.self.message(self.self.INSIGHTS_MPI_IO_NO_COLLECTIVE_WRITE_USAGE,
                                self.self.TARGET_DEVELOPER, self.self.HIGH, issue, recommendation,
                                detail))
            else:
                issue = 'Application uses MPI-IO and write data using {} ({:.2f}%) collective operations'.format(
                    df_mpiio['counters']['MPIIO_COLL_WRITES'].sum(),
                    df_mpiio['counters']['MPIIO_COLL_WRITES'].sum() /
                    (df_mpiio['counters']['MPIIO_INDEP_WRITES'].sum() +
                    df_mpiio['counters']['MPIIO_COLL_WRITES'].sum()) * 100)

                self.insights_operation.append(
                    self.message(self.INSIGHTS_MPI_IO_COLLECTIVE_WRITE_USAGE,
                            self.TARGET_DEVELOPER, self.OK, issue))

            #########################################################################################################################################################################

            # Look for usage of non-block operations

            # Look for HDF5 file extension

            has_hdf5_extension = False

            for index, row in df_mpiio['counters'].iterrows():
                if file_map[int(row['id'])].endswith('.h5') or file_map[int(
                        row['id'])].endswith('.hdf5'):
                    has_hdf5_extension = True

            if df_mpiio['counters']['MPIIO_NB_READS'].sum() == 0:
                issue = 'Application could benefit from non-blocking (asynchronous) reads'

                recommendation = []

                if 'H5F' in modules or has_hdf5_extension:
                    recommendation.append({
                        'message':
                        'Since you use HDF5, consider using the ASYNC I/O VOL connector (https://github.com/hpc-io/vol-async)',
                        'sample':
                        Syntax.from_path(os.path.join(
                            self.ROOT, 'snippets/hdf5-vol-async-read.c'),
                                        line_numbers=True,
                                        background_color='default')
                    })

                if 'MPI-IO' in modules:
                    recommendation.append({
                        'message':
                        'Since you use MPI-IO, consider non-blocking/asynchronous I/O operations',  # (e.g., MPI_File_iread(), MPI_File_read_all_begin/end(), or MPI_File_read_at_all_begin/end())',
                        'sample':
                        Syntax.from_path(os.path.join(self.ROOT,
                                                    'snippets/mpi-io-iread.c'),
                                        line_numbers=True,
                                        background_color='default')
                    })

                self.insights_operation.append(
                    self.message(self.INSIGHTS_MPI_IO_BLOCKING_READ_USAGE, self.TARGET_DEVELOPER,
                            self.WARN, issue, recommendation))

            if df_mpiio['counters']['MPIIO_NB_WRITES'].sum() == 0:
                issue = 'Application could benefit from non-blocking (asynchronous) writes'

                recommendation = []

                if 'H5F' in modules or has_hdf5_extension:
                    recommendation.append({
                        'message':
                        'Since you use HDF5, consider using the ASYNC I/O VOL connector (https://github.com/hpc-io/vol-async)',
                        'sample':
                        Syntax.from_path(os.path.join(
                            self.ROOT, 'snippets/hdf5-vol-async-write.c'),
                                        line_numbers=True,
                                        background_color='default')
                    })

                if 'MPI-IO' in modules:
                    recommendation.append({
                        'message':
                        'Since you use MPI-IO, consider non-blocking/asynchronous I/O operations',  # (e.g., MPI_File_iwrite(), MPI_File_write_all_begin/end(), or MPI_File_write_at_all_begin/end())',
                        'sample':
                        Syntax.from_path(os.path.join(self.ROOT,
                                                    'snippets/mpi-io-iwrite.c'),
                                        line_numbers=True,
                                        background_color='default')
                    })

                self.insights_operation.append(
                    self.message(self.INSIGHTS_MPI_IO_BLOCKING_WRITE_USAGE, self.TARGET_DEVELOPER,
                            self.WARN, issue, recommendation))

        #########################################################################################################################################################################

        # Nodes and MPI-IO aggregators
        # If the application uses collective reads or collective writes, look for the number of aggregators
        hints = ''

        if 'h' in job['job']['metadata']:
            hints = job['job']['metadata']['h']

            if hints:
                hints = hints.split(';')

        # print('Hints: ', hints)

        #########################################################################################################################################################################

        NUMBER_OF_COMPUTE_NODES = 0

        if 'MPI-IO' in modules:
            cb_nodes = None

            for hint in hints:
                (key, value) = hint.split('=')

                if key == 'cb_nodes':
                    cb_nodes = value

            # Try to get the number of compute nodes from SLURM, if not found, set as information
            command = 'sacct --job {} --format=JobID,JobIDRaw,NNodes,NCPUs --parsable2 --delimiter ","'.format(
                job['job']['jobid'])

            arguments = shlex.split(command)

            try:
                result = subprocess.run(arguments,
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE)

                if result.returncode == 0:
                    # We have successfully fetched the information from SLURM
                    db = csv.DictReader(io.StringIO(result.stdout.decode('utf-8')))

                    try:
                        first = next(db)

                        if 'NNodes' in first:
                            NUMBER_OF_COMPUTE_NODES = first['NNodes']

                            # Do we have one MPI-IO aggregator per node?
                            if cb_nodes > NUMBER_OF_COMPUTE_NODES:
                                issue = 'Application is using inter-node aggregators (which require network communication)'

                                recommendation = [{
                                    'message':
                                    'Set the MPI hints for the number of aggregators as one per compute node (e.g., cb_nodes={})'
                                    .format(NUMBER_OF_COMPUTE_NODES),
                                    'sample':
                                    Syntax.from_path(os.path.join(
                                        self.ROOT, 'snippets/mpi-io-hints.bash'),
                                                    line_numbers=True,
                                                    background_color='default')
                                }]

                                self.insights_operation.append(
                                    self.message(self.INSIGHTS_MPI_IO_AGGREGATORS_INTER,
                                            self.TARGET_USER, self.HIGH, issue,
                                            recommendation))

                            if cb_nodes < NUMBER_OF_COMPUTE_NODES:
                                issue = 'Application is using intra-node aggregators'

                                self.insights_operation.append(
                                    self.message(self.INSIGHTS_MPI_IO_AGGREGATORS_INTRA,
                                            self.TARGET_USER, self.OK, issue))

                            if cb_nodes == NUMBER_OF_COMPUTE_NODES:
                                issue = 'Application is using one aggregator per compute node'

                                self.insights_operation.append(
                                    self.message(self.INSIGHTS_MPI_IO_AGGREGATORS_OK,
                                            self.TARGET_USER, self.OK, issue))

                    except StopIteration:
                        pass
            except FileNotFoundError:
                pass

        #########################################################################################################################################################################

        codes = []
        if self.args.json:
            f = open(self.args.json)
            data = json.load(f)

            for key, values in data.items():
                for value in values:
                    code = value['code']
                    codes.append(code)

                    level = value['level']
                    issue = value['issue']
                    recommendation = []
                    for rec in value['recommendations']:
                        new_message = {'message': rec}
                        recommendation.append(new_message)

                    self.insights_dxt.append(
                        self.message(code, self.TARGET_DEVELOPER, level, issue,
                                recommendation))

        #########################################################################################################################################################################

        insights_end_time = time.time()

        # Version 3.4.1 of py-darshan changed the contents on what is reported in 'job'
        if 'start_time' in job['job']:
            job_start = datetime.datetime.fromtimestamp(job['job']['start_time'],
                                                        datetime.timezone.utc)
            job_end = datetime.datetime.fromtimestamp(job['job']['end_time'],
                                                    datetime.timezone.utc)
        else:
            job_start = datetime.datetime.fromtimestamp(
                job['job']['start_time_sec'], datetime.timezone.utc)
            job_end = datetime.datetime.fromtimestamp(job['job']['end_time_sec'],
                                                    datetime.timezone.utc)

        self.console.print()

        self.console.print(
            Panel(
                '\n'.join([
                    ' [b]JOB[/b]:            [white]{}[/white]'.format(
                        job['job']['jobid']),
                    ' [b]EXECUTABLE[/b]:     [white]{}[/white]'.format(
                        job['exe'].split()[0]),
                    ' [b]DARSHAN[/b]:        [white]{}[/white]'.format(
                        os.path.basename(self.args.darshan)),
                    ' [b]EXECUTION TIME[/b]: [white]{} to {} ({:.2f} hours)[/white]'
                    .format(job_start, job_end,
                            (job_end - job_start).total_seconds() / 3600),
                    ' [b]FILES[/b]:          [white]{} files ({} use STDIO, {} use POSIX, {} use MPI-IO)[/white]'
                    .format(
                        total_files,
                        total_files_stdio,
                        total_files_posix -
                        total_files_mpiio,  # Since MPI-IO files will always use POSIX, we can decrement to get a unique count
                        total_files_mpiio),
                    ' [b]COMPUTE NODES[/b]   [white]{}[/white]'.format(
                        NUMBER_OF_COMPUTE_NODES),
                    ' [b]PROCESSES[/b]       [white]{}[/white]'.format(
                        job['job']['nprocs']),
                    ' [b]HINTS[/b]:          [white]{}[/white]'.format(
                        ' '.join(hints))
                ]),
                title='[b][slate_blue3]DRISHTI[/slate_blue3] v.0.3[/b]',
                title_align='left',
                subtitle=
                '[red][b]{} critical issues[/b][/red], [orange1][b]{} warnings[/b][/orange1], and [white][b]{} recommendations[/b][/white]'
                .format(
                    self.insights_total[self.HIGH],
                    self.insights_total[self.WARN],
                    self.insights_total[self.RECOMMENDATIONS],
                ),
                subtitle_align='left',
                padding=1))

        self.console.print()

        if self.insights_metadata:
            self.console.print(
                Panel(Padding(Group(*self.insights_metadata), (1, 1)),
                    title='METADATA',
                    title_align='left'))

        if self.insights_operation:
            self.console.print(
                Panel(Padding(Group(*self.insights_operation), (1, 1)),
                    title='OPERATIONS',
                    title_align='left'))

        if self.insights_dxt:
            self.console.print(
                Panel(Padding(Group(*self.insights_dxt), (1, 1)),
                    title='DXT',
                    title_align='left'))

        self.console.print(
            Panel(
                ' {} | [white]LBNL[/white] | [white]Drishti report generated at {} in[/white] {:.3f} seconds'
                .format(datetime.datetime.now().year, datetime.datetime.now(),
                        insights_end_time - insights_start_time),
                box=box.SIMPLE))

        if self.args.export_theme_light:
            export_theme = TerminalTheme(
                (255, 255, 255),
                (0, 0, 0),
                [
                    (26, 26, 26),
                    (244, 0, 95),
                    (152, 224, 36),
                    (253, 151, 31),
                    (157, 101, 255),
                    (244, 0, 95),
                    (88, 209, 235),
                    (120, 120, 120),
                    (98, 94, 76),
                ],
                [
                    (244, 0, 95),
                    (152, 224, 36),
                    (224, 213, 97),
                    (157, 101, 255),
                    (244, 0, 95),
                    (88, 209, 235),
                    (246, 246, 239),
                ],
            )
        else:
            export_theme = MONOKAI

        if self.args.export_html:
            self.console.save_html('{}.html'.format(self.args.darshan),
                            theme=export_theme,
                            clear=False)

        if self.args.export_svg:
            self.console.save_svg('{}.svg'.format(self.args.darshan),
                            title='Drishti',
                            theme=export_theme,
                            clear=False)

        if self.args.export_csv:
            issues = [
                'JOB', self.INSIGHTS_STDIO_HIGH_USAGE,
                self.INSIGHTS_POSIX_WRITE_COUNT_INTENSIVE,
                self.INSIGHTS_POSIX_READ_COUNT_INTENSIVE,
                self.INSIGHTS_POSIX_WRITE_SIZE_INTENSIVE,
                self.INSIGHTS_POSIX_READ_SIZE_INTENSIVE,
                self.INSIGHTS_POSIX_HIGH_SMALL_READ_REQUESTS_USAGE,
                self.INSIGHTS_POSIX_HIGH_SMALL_WRITE_REQUESTS_USAGE,
                self.INSIGHTS_POSIX_HIGH_MISALIGNED_MEMORY_USAGE,
                self.INSIGHTS_POSIX_HIGH_MISALIGNED_FILE_USAGE,
                self.INSIGHTS_POSIX_REDUNDANT_READ_USAGE,
                self.INSIGHTS_POSIX_REDUNDANT_WRITE_USAGE,
                self.INSIGHTS_POSIX_HIGH_RANDOM_READ_USAGE,
                self.INSIGHTS_POSIX_HIGH_SEQUENTIAL_READ_USAGE,
                self.INSIGHTS_POSIX_HIGH_RANDOM_WRITE_USAGE,
                self.INSIGHTS_POSIX_HIGH_SEQUENTIAL_WRITE_USAGE,
                self.INSIGHTS_POSIX_HIGH_SMALL_READ_REQUESTS_SHARED_FILE_USAGE,
                self.INSIGHTS_POSIX_HIGH_SMALL_WRITE_REQUESTS_SHARED_FILE_USAGE,
                self.INSIGHTS_POSIX_HIGH_METADATA_TIME, self.INSIGHTS_POSIX_SIZE_IMBALANCE,
                self.INSIGHTS_POSIX_TIME_IMBALANCE,
                self.INSIGHTS_POSIX_INDIVIDUAL_WRITE_SIZE_IMBALANCE,
                self.INSIGHTS_POSIX_INDIVIDUAL_READ_SIZE_IMBALANCE,
                self.INSIGHTS_MPI_IO_NO_USAGE, self.INSIGHTS_MPI_IO_NO_COLLECTIVE_READ_USAGE,
                self.INSIGHTS_MPI_IO_NO_COLLECTIVE_WRITE_USAGE,
                self.INSIGHTS_MPI_IO_COLLECTIVE_READ_USAGE,
                self.INSIGHTS_MPI_IO_COLLECTIVE_WRITE_USAGE,
                self.INSIGHTS_MPI_IO_BLOCKING_READ_USAGE,
                self.INSIGHTS_MPI_IO_BLOCKING_WRITE_USAGE,
                self.INSIGHTS_MPI_IO_AGGREGATORS_INTRA,
                self.INSIGHTS_MPI_IO_AGGREGATORS_INTER, self.INSIGHTS_MPI_IO_AGGREGATORS_OK
            ]
            if codes:
                issues.extend(codes)

            detected_issues = dict.fromkeys(issues, False)
            detected_issues['JOB'] = job['job']['jobid']

            for report in self.csv_report:
                detected_issues[report] = True

            filename = '{}-summary.csv'.format(self.args.darshan.replace(
                '.darshan', ''))

            with open(filename, 'w') as f:
                w = csv.writer(f)
                w.writerow(detected_issues.keys())
                w.writerow(detected_issues.values())
        
        if self.args.delete_convert:
            os.remove(filename)
        
        return self.console.export_html()