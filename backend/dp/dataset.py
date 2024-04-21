'''
Author       : Outsider
Date         : 2023-12-08 17:36:41
LastEditors  : Outsider
LastEditTime : 2023-12-18 19:41:16
Description  : In User Settings Edit
FilePath     : /thesis/backend/dp/dataset.py
'''
import re
import pandas as pd
import numpy as np
import glob

keep_POSIX_columns = [
    'nprocs',
    'run_time',
    'POSIX_TOTAL_FILES',
    'POSIX_READ_ONLY_FILES',
    'POSIX_WRITE_ONLY_FILES',
    'POSIX_READ_WRITE_FILES',
    'POSIX_UNIQUE_FILES',
    'POSIX_SHARE_FILES',
    'POSIX_BYTES_READ',
    'POSIX_BYTES_WRITTEN',
    'POSIX_SIZE_READ_*',
    'POSIX_SIZE_WRITE_*',
]
# 编译正则表达式字符串
keep_POSIX_regex_columns = [re.compile(regex) for regex in keep_POSIX_columns]
keep_STDIO_columns = []


def Get_dataset(path):
    df = pd.read_csv(path, delimiter=',')

    return df


def get_number_columns(df):
    """
    Since some columns contain string metadata, and others contain values,
    this function returns the columns that contain values.
    """
    return df.columns[np.logical_or(df.dtypes == np.float64,
                                    df.dtypes == np.int64)]


def remove_invalid_feature(df, min_drop_prec=0.5):
    drop_columns = []
    for idx, c in enumerate(df.columns):
        print(idx, c)
        if df.dtypes.iloc[idx] == np.int64 or df.dtypes.iloc[idx] == np.float64:
            print(df[c])
            tol = np.sum(df[c] < 0)
            print(tol)

            if df.shape[1] * min_drop_prec < tol:
                drop_columns.append(c)

    drop_columns = filter_columns('POSIX', drop_columns)

    df = df.drop(columns=drop_columns)

    # Next, drop jobs that have negative values
    jobs_without_zeros = np.sum(df[get_number_columns(df)] < 0, axis=1) == 0

    df = df.loc[jobs_without_zeros]

    return df


def remove_zero_variance_features(df):
    """
    Drop columns with zero variance.
    """
    drop_columns = get_number_columns(df)[df[get_number_columns(df)].var() ==
                                          0]

    drop_columns = filter_columns('POSIX', drop_columns)
    df = df.drop(columns=drop_columns)

    return df


def remove_correlated_features(df, min_correlation=0.99):
    """
    Clusters together highly correlated features into sets. 
    Since some features are more important than others, forces keeping those features out of a set of
    correlated ones.
    """
    keep_features = ['runtime', "POSIX_total_bytes", "POSIX_READS"]
    corr = df.corr()
    feature_sets = []

    # First, populate the feature_sets list with sets of correlated features
    for row, col in zip(*np.where(corr > min_correlation)):
        # check if we should bundle in a previous set
        found_set = False

        for fs in feature_sets:
            if row in fs or col in fs:
                fs.add(row)
                fs.add(col)
                found_set = True
                break

        if not found_set:
            feature_sets.append(set((row, col)))

    # # Log the correlated sets
    # for feature_set in [s for s in feature_sets if len(s) > 1]:
    #     logging.info("Found a set of correlated features: {}".format(list(df.columns[list(feature_set)])))

    # Next, figure out what features per set to keep, and what to discard
    drop_columns = []
    for fs in [fs for fs in feature_sets if len(fs) > 1]:
        column_set = set(df.columns[list(fs)])

        intersection = column_set.intersection(keep_features)
        # if len(intersection) > 1:
        #     logging.warning("Found a set of correlated features that contains multiple features we are forced to keep: {}".format(intersection))

        # In case the intersection has some elements, just remove keep_features
        if len(intersection) > 0:
            column_set = column_set.difference(keep_features)
        # Else, keep the first one
        else:
            column_set = list(column_set)[1:]

        # Remove any features we are forced to keep
        drop_columns += list(column_set)

    # Finally, drop the correlated features, without the string features
    drop_columns = list(set(drop_columns).intersection(get_number_columns(df)))
    drop_columns = filter_columns('POSIX', drop_columns)
    print("Removing correlated set of features: {}".format(drop_columns))
    df = df.drop(columns=drop_columns)

    return df


def remove_unimporant_features(df, modual):
    """
    Remove features marked as unimportant.
    """
    STDIO_unimportant_labels = [
        "STDIO_SEEKS", "STDIO_FASTEST_RANK", "STDIO_FASTEST_RANK_BYTES",
        "STDIO_SLOWEST_RANK", "STDIO_SLOWEST_RANK_BYTES",
        "STDIO_F_OPEN_START_TIMESTAMP", "STDIO_F_CLOSE_START_TIMESTAMP",
        "STDIO_F_WRITE_START_TIMESTAMP", "STDIO_F_READ_START_TIMESTAMP",
        "STDIO_F_OPEN_END_TIMESTAMP", "STDIO_F_CLOSE_END_TIMESTAMP",
        "STDIO_F_WRITE_END_TIMESTAMP", "STDIO_F_READ_END_TIMESTAMP",
        "STDIO_F_FASTEST_RANK_TIME", "STDIO_F_SLOWEST_RANK_TIME",
        "STDIO_F_VARIANCE_RANK_TIME", "STDIO_F_VARIANCE_RANK_BYTES"
    ]
    MPIIO_unimportant_labels = [
        "MPIIO_FASTEST_RANK",
        "MPIIO_FASTEST_RANK_BYTES",
        "MPIIO_F_CLOSE_END_TIMESTAMP",
        "MPIIO_F_FASTEST_RANK_TIME",
        "MPIIO_F_MAX_READ_TIME",
        "MPIIO_F_MAX_WRITE_TIME",
        "MPIIO_F_OPEN_START_TIMESTAMP",
        "MPIIO_F_OPEN_END_TIMESTAMP",
        "MPIIO_F_READ_END_TIMESTAMP",
        "MPIIO_F_CLOSE_START_TIMESTAMP",
        "MPIIO_F_READ_START_TIMESTAMP",
        "MPIIO_F_SLOWEST_RANK_TIME",
        "MPIIO_F_VARIANCE_RANK_BYTES",
        "MPIIO_F_VARIANCE_RANK_TIME",
        "MPIIO_F_WRITE_END_TIMESTAMP",
        "MPIIO_F_WRITE_START_TIMESTAMP",
        "MPIIO_HINTS",
        "MPIIO_MAX_READ_TIME_SIZE",
        "MPIIO_MAX_WRITE_TIME_SIZE",
        "MPIIO_MODE",
    ]

    drop_labels = []
    if modual == 'STDIO':
        drop_labels = STDIO_unimportant_labels
    if modual == 'MPIIO':
        drop_labels = MPIIO_unimportant_labels

    for label in drop_labels:
        try:
            df = df.drop(columns=label)
        except:
            print("Cannot drop nonexistant column {}".format(label))

    return df


def remove_columns_containing(df, text):
    """
    Remove all columns that do contain the text argument within their name. 
    """
    if not isinstance(text, list):
        text = [text]

    drop_columns = set()
    for c in df.columns:
        for t in text:
            if t in c:
                drop_columns.add(c)

    print("Removing columns that contain {}: {}".format(text, drop_columns))

    return df.drop(columns=list(drop_columns))


def convert_POSIX_features_to_percentages(df, remove_dual=True):
    """
    Certain features like POSIX_SEQ_READS make more sense when normalized by a more general feature such as POSIX_READS
    For all features that measure either the number of a certain type of access, or the number of bytes, we normalize by
    the total number POSIX accesses and total number of POSIX bytes accessed.
    If remove_dual is true, removes one of the dual features such read and write percentage, unique and shared, etc.
    """
    df = df.copy()

    if np.any(np.isnan(df[get_number_columns(df)])):
        print("Found NaN values before normalizing dataframe.")

    total_accesses = df.POSIX_WRITES + df.POSIX_READS
    total_bytes = df.POSIX_BYTES_READ + df.POSIX_BYTES_WRITTEN

    df['POSIX_TOTAL_ACCESSES'] = total_accesses
    df['POSIX_TOTAL_BYTES'] = total_bytes

    try:
        df['POSIX_BYTES_READ_PERC'] = df.POSIX_BYTES_READ / total_bytes
        df['POSIX_BYTES_WRITTEN_PERC'] = df.POSIX_BYTES_WRITTEN / total_bytes
        df = df.drop(columns=[
            "POSIX_BYTES_READ",
            "POSIX_BYTES_WRITTEN",
        ])
    except:
        print(
            "Failed to normalize one of the features in [POSIX_BYTES_READ, POSIX_BYTES_WRITTEN]"
        )

    try:
        df['POSIX_UNIQUE_FILES_PERC'] = df.POSIX_UNIQUE_FILES / df.POSIX_TOTAL_FILES
        df['POSIX_SHARE_FILES_PERC'] = df.POSIX_SHARE_FILES / df.POSIX_TOTAL_FILES
        df['POSIX_READ_ONLY_FILES_PERC'] = df.POSIX_READ_ONLY_FILES / df.POSIX_TOTAL_FILES
        df['POSIX_READ_WRITE_FILES_PERC'] = df.POSIX_READ_WRITE_FILES / df.POSIX_TOTAL_FILES
        df['POSIX_WRITE_ONLY_FILES_PERC'] = df.POSIX_WRITE_ONLY_FILES / df.POSIX_TOTAL_FILES
        df = df.drop(columns=[
            'POSIX_UNIQUE_FILES', 'POSIX_SHARE_FILES', 'POSIX_READ_ONLY_FILES',
            'POSIX_READ_WRITE_FILES', 'POSIX_WRITE_ONLY_FILES'
        ])
    except:
        print("Failed to normalize one of the *_files features")

    try:
        df['POSIX_READS_PERC'] = df.POSIX_READS / total_accesses
        df['POSIX_WRITES_PERC'] = df.POSIX_WRITES / total_accesses
        df['POSIX_RW_SWITCHES_PERC'] = df.POSIX_RW_SWITCHES / total_accesses
        df['POSIX_SEQ_READS_PERC'] = df.POSIX_SEQ_READS / total_accesses
        df['POSIX_SEQ_WRITES_PERC'] = df.POSIX_SEQ_WRITES / total_accesses
        df['POSIX_CONSEC_READS_PERC'] = df.POSIX_CONSEC_READS / total_accesses
        df['POSIX_CONSEC_WRITES_PERC'] = df.POSIX_CONSEC_WRITES / total_accesses
        df['POSIX_FILE_NOT_ALIGNED_PERC'] = df.POSIX_FILE_NOT_ALIGNED / total_accesses
        df['POSIX_MEM_NOT_ALIGNED_PERC'] = df.POSIX_MEM_NOT_ALIGNED / total_accesses
        df = df.drop(columns=[
            "POSIX_READS", "POSIX_WRITES", "POSIX_RW_SWITCHES",
            "POSIX_SEQ_WRITES", "POSIX_SEQ_READS", "POSIX_CONSEC_READS",
            "POSIX_CONSEC_WRITES", "POSIX_FILE_NOT_ALIGNED",
            "POSIX_MEM_NOT_ALIGNED"
        ])
    except:
        print(
            "Failed to normalize one of the features in [POSIX_READS, POSIX_WRITES, POSIX_SEQ_WRITES, POSIX_SEQ_READS, POSIX_CONSEC_READS, POSIX_CONSEC_WRITES, POSIX_FILE_NOT_ALIGNED_PERC, POSIX_MEM_NOT_ALIGNED_PERC]"
        )

    try:
        if np.any(df.POSIX_SIZE_READ_0_100 + df.POSIX_SIZE_READ_100_1K +
                  df.POSIX_SIZE_READ_1K_10K + df.POSIX_SIZE_READ_10K_100K +
                  df.POSIX_SIZE_READ_100K_1M + df.POSIX_SIZE_READ_1M_4M +
                  df.POSIX_SIZE_READ_4M_10M + df.POSIX_SIZE_READ_10M_100M +
                  df.POSIX_SIZE_READ_100M_1G + df.POSIX_SIZE_READ_1G_PLUS +
                  df.POSIX_SIZE_WRITE_0_100 + df.POSIX_SIZE_WRITE_100_1K +
                  df.POSIX_SIZE_WRITE_1K_10K + df.POSIX_SIZE_WRITE_10K_100K +
                  df.POSIX_SIZE_WRITE_100K_1M + df.POSIX_SIZE_WRITE_1M_4M +
                  df.POSIX_SIZE_WRITE_4M_10M + df.POSIX_SIZE_WRITE_10M_100M +
                  df.POSIX_SIZE_WRITE_100M_1G +
                  df.POSIX_SIZE_WRITE_1G_PLUS != total_accesses):
            print(
                "POSIX_SIZE_WRITE* + POSIX_SIZE_READ* columns do not add up to POSIX_total_accesses"
            )

        df['POSIX_SIZE_READ_0_100_PERC'] = df.POSIX_SIZE_READ_0_100 / total_accesses
        df['POSIX_SIZE_READ_100_1K_PERC'] = df.POSIX_SIZE_READ_100_1K / total_accesses
        df['POSIX_SIZE_READ_1K_10K_PERC'] = df.POSIX_SIZE_READ_1K_10K / total_accesses
        df['POSIX_SIZE_READ_10K_100K_PERC'] = df.POSIX_SIZE_READ_10K_100K / total_accesses
        df['POSIX_SIZE_READ_100K_1M_PERC'] = df.POSIX_SIZE_READ_100K_1M / total_accesses
        df['POSIX_SIZE_READ_1M_4M_PERC'] = df.POSIX_SIZE_READ_1M_4M / total_accesses
        df['POSIX_SIZE_READ_4M_10M_PERC'] = df.POSIX_SIZE_READ_4M_10M / total_accesses
        df['POSIX_SIZE_READ_10M_100M_PERC'] = df.POSIX_SIZE_READ_10M_100M / total_accesses
        df['POSIX_SIZE_READ_100M_1G_PERC'] = df.POSIX_SIZE_READ_100M_1G / total_accesses
        df['POSIX_SIZE_READ_1G_PLUS_PERC'] = df.POSIX_SIZE_READ_1G_PLUS / total_accesses

        df['POSIX_SIZE_WRITE_0_100_PERC'] = df.POSIX_SIZE_WRITE_0_100 / total_accesses
        df['POSIX_SIZE_WRITE_100_1K_PERC'] = df.POSIX_SIZE_WRITE_100_1K / total_accesses
        df['POSIX_SIZE_WRITE_1K_10K_PERC'] = df.POSIX_SIZE_WRITE_1K_10K / total_accesses
        df['POSIX_SIZE_WRITE_10K_100K_PERC'] = df.POSIX_SIZE_WRITE_10K_100K / total_accesses
        df['POSIX_SIZE_WRITE_100K_1M_PERC'] = df.POSIX_SIZE_WRITE_100K_1M / total_accesses
        df['POSIX_SIZE_WRITE_1M_4M_PERC'] = df.POSIX_SIZE_WRITE_1M_4M / total_accesses
        df['POSIX_SIZE_WRITE_4M_10M_PERC'] = df.POSIX_SIZE_WRITE_4M_10M / total_accesses
        df['POSIX_SIZE_WRITE_10M_100M_PERC'] = df.POSIX_SIZE_WRITE_10M_100M / total_accesses
        df['POSIX_SIZE_WRITE_100M_1G_PERC'] = df.POSIX_SIZE_WRITE_100M_1G / total_accesses
        df['POSIX_SIZE_WRITE_1G_PLUS_PERC'] = df.POSIX_SIZE_WRITE_1G_PLUS / total_accesses

        drop_columns = [
            "POSIX_SIZE_READ_0_100", "POSIX_SIZE_READ_100_1K",
            "POSIX_SIZE_READ_1K_10K", "POSIX_SIZE_READ_10K_100K",
            "POSIX_SIZE_READ_100K_1M", "POSIX_SIZE_READ_1M_4M",
            "POSIX_SIZE_READ_4M_10M", "POSIX_SIZE_READ_10M_100M",
            "POSIX_SIZE_READ_100M_1G", "POSIX_SIZE_READ_1G_PLUS",
            "POSIX_SIZE_WRITE_0_100", "POSIX_SIZE_WRITE_100_1K",
            "POSIX_SIZE_WRITE_1K_10K", "POSIX_SIZE_WRITE_10K_100K",
            "POSIX_SIZE_WRITE_100K_1M", "POSIX_SIZE_WRITE_1M_4M",
            "POSIX_SIZE_WRITE_4M_10M", "POSIX_SIZE_WRITE_10M_100M",
            "POSIX_SIZE_WRITE_100M_1G", "POSIX_SIZE_WRITE_1G_PLUS"
        ]

        df = df.drop(columns=drop_columns)
    except:
        print("Failed to normalize POSIX_SIZE_*")

    try:
        df['POSIX_ACCESS1_COUNT_PERC'] = df.POSIX_ACCESS1_COUNT / total_accesses
        df['POSIX_ACCESS2_COUNT_PERC'] = df.POSIX_ACCESS2_COUNT / total_accesses
        df['POSIX_ACCESS3_COUNT_PERC'] = df.POSIX_ACCESS3_COUNT / total_accesses
        df['POSIX_ACCESS4_COUNT_PERC'] = df.POSIX_ACCESS4_COUNT / total_accesses

        print("Normalized access values:")
        print("Access 1 %: max={}, mean={}, median={}".format(
            np.max(df.POSIX_ACCESS1_COUNT_PERC),
            np.mean(df.POSIX_ACCESS1_COUNT_PERC),
            np.median(df.POSIX_ACCESS1_COUNT_PERC)))
        print("Access 2 %: max={}, mean={}, median={}".format(
            np.max(df.POSIX_ACCESS2_COUNT_PERC),
            np.mean(df.POSIX_ACCESS2_COUNT_PERC),
            np.median(df.POSIX_ACCESS2_COUNT_PERC)))
        print("Access 3 %: max={}, mean={}, median={}".format(
            np.max(df.POSIX_ACCESS3_COUNT_PERC),
            np.mean(df.POSIX_ACCESS3_COUNT_PERC),
            np.median(df.POSIX_ACCESS3_COUNT_PERC)))
        print("Access 4 %: max={}, mean={}, median={}".format(
            np.max(df.POSIX_ACCESS4_COUNT_PERC),
            np.mean(df.POSIX_ACCESS4_COUNT_PERC),
            np.median(df.POSIX_ACCESS4_COUNT_PERC)))

        df = df.drop(columns=[
            'POSIX_ACCESS1_COUNT', 'POSIX_ACCESS2_COUNT',
            'POSIX_ACCESS3_COUNT', 'POSIX_ACCESS4_COUNT'
        ])
    except:
        print("Failed to normalize POSIX_ACCESS[1-4]_COUNT")

    # In case of division by zero, we'll get NaN. We convert those to zeros.
    df = df.fillna(0)

    if remove_dual:
        df = df.drop(columns=[
            'POSIX_BYTES_WRITTEN_PERC', 'POSIX_shared_bytes_perc',
            'POSIX_read_write_bytes_perc', 'POSIX_read_write_files_perc',
            'POSIX_WRITES_PERC', 'POSIX_shared_files_perc'
        ])

    return df


def log_scale_dataset(df, add_small_value=1, set_NaNs_to=-10):
    """
    Takes the log10 of a DF + a small value (to prevent -infs), 
    and replaces NaN values with a predetermined value.
    Adds the new columns to the dataset, and renames the original ones.
    """
    number_columns = get_number_columns(df)
    columns = [x for x in number_columns if "perc" not in x.lower()]
    print("Applying log10() to the columns {}".format(columns))

    for c in columns:
        if c == 'uid':
            pass
        elif c == 'run_time' or c == 'nprocs':
            df["LOG10_" +
               c] = np.log10(df[c] + add_small_value).fillna(value=set_NaNs_to)
            df.rename(columns={c: "RAW_" + c}, inplace=True)
        else:
            df[c.replace("POSIX",
                         "POSIX_LOG10")] = np.log10(df[c] +
                                                    add_small_value).fillna(
                                                        value=set_NaNs_to)
            df.rename(columns={c: c.replace("POSIX", "POSIX_RAW")},
                      inplace=True)

    return df


def filter_columns(modual, arrary):
    filtered = []
    if modual == 'POSIX':
        # 过滤掉与正则表达式列表 A 中任何一个匹配的字符串
        filtered = [
            string for string in arrary if not any(
                regex.search(string) for regex in keep_POSIX_regex_columns)
        ]
        print(filtered)

    return filtered


def extract_app_name(text):

    match = re.match(r'^\./(.+?)(?:\s|$)', text)
    if match:
        return match.group(1).split('/')[-1]

    match = re.match(r'^/(.+?)(?:\s|$)', text)
    if match:
        return match.group(1).split('/')[-1]

    match = re.search(r"\/?([^\/\s]+\.x)", text)
    if match:
        return match.group(1)

    return text


def rename_apps(df):
    df['short_name'] = df['exe'].apply(extract_app_name)
    print(df)
    return df


def sanitize(df):

    df = remove_invalid_feature(df, 0.5)
    df = remove_zero_variance_features(df)
    # df = remove_correlated_features(df[get_number_columns(df)])
    df = remove_columns_containing(df, 'STRIDE')
    df = remove_columns_containing(df, 'FASTEST')
    df = remove_columns_containing(df, 'SLOWEST')

    df = convert_POSIX_features_to_percentages(df, remove_dual=False)
    df = log_scale_dataset(df)

    df = rename_apps(df)

    # Finally, let's cut down the size of the dataset in order to simplify clustering
    IO_jobs = df.POSIX_RAW_TOTAL_BYTES > 0

    df = df[IO_jobs]

    run_job = df.RAW_run_time > 0

    df = df[run_job]

    df.to_csv('total_posix_sanitize.csv')


if __name__ == "__main__":
    # df = Get_dataset("data/anon.csv")
    df = Get_dataset("posix.csv")
    print(df.columns)
    print(df)
    sanitize(df)
