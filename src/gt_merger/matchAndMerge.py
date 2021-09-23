"""
/*
 * Copyright (C) 2019-2021 University of South Florida
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
 """
from datetime import datetime
import os
from pathlib import Path

import numpy as np
import pandas as pd

# Import dependencies
from matplotlib import pyplot as plt
from collections import defaultdict

from src.gt_merger import constants
from src.gt_merger.args import get_parser
from src.gt_merger.preprocess import preprocess_gt_data, preprocess_oba_data, is_valid_oba_dataframe, \
    is_valid_gt_dataframe


# -------------------------------------------

def main():
    # Verify if the OBA input file exists
    if not os.path.isfile(command_line_args.obaFile):
        print("OBA data file not found:", command_line_args.obaFile)
        exit()

    # Verify if GT input file exists
    if not os.path.isfile(command_line_args.gtFile):
        print("Ground truth data file not found:", command_line_args.gtFile)
        exit()

    # Verify if the data folder exists
    if not os.path.isdir(command_line_args.outputDir):
        print("Data folder not found, trying to create it in the current working directory:",
              command_line_args.outputDir)
        try:
            os.makedirs(command_line_args.outputDir, exist_ok=True)
        except OSError:
            print("There was an error while creating the data folder:", command_line_args.outputDir)
            exit()

    # Create sub-folders for output an logs
    path_logs = os.path.join(command_line_args.outputDir, constants.FOLDER_LOGS)
    if not os.path.isdir(path_logs):
        try:
            os.mkdir(path_logs)
        except OSError:
            print("There was an error while creating the sub folder for logs:", path_logs)
            exit()

    path_output = os.path.join(command_line_args.outputDir, constants.FOLDER_MERGED_DATA)
    if not os.path.isdir(path_output):
        try:
            os.mkdir(path_output)
        except OSError:
            print("There was an error while creating the sub-folder for output files:", path_logs)
            exit()

    # Create path OS independent for excel file
    excel_path = Path(command_line_args.gtFile)
    # Load ground truth data to a dataframe
    gt_data = pd.read_excel(excel_path)
    # Validate gt dataframe
    if not is_valid_gt_dataframe(gt_data):
        print("Ground truth data frame is empty or does not have the required columns.")
        exit()

    # Preprocess ground truth data
    gt_data, data_gt_dropped = preprocess_gt_data(gt_data)
    print("Ground truth data preprocessed.")
    # Save data to be dropped to a csv file
    dropped_file_path = os.path.join(command_line_args.outputDir, constants.FOLDER_LOGS,
                                     constants.GT_DROPPED_DATA_FILE_NAME)
    data_gt_dropped.to_csv(path_or_buf=dropped_file_path, index=False)

    # Create path OS independent for csv file
    csv_path = Path(command_line_args.obaFile)
    # Load OBA data
    oba_data = pd.read_csv(csv_path)
    # Validate oba dataframe
    if not is_valid_oba_dataframe(oba_data):
        print("OBA data frame is empty or does not have the required columns.")
        exit()

    # Preprocess OBA data
    oba_data, data_csv_dropped = preprocess_oba_data(oba_data, command_line_args.minActivityDuration,
                                                     command_line_args.minTripLength)
    print("OBA data preprocessed.")

    # Data preprocessing is over
    # Save oba dropped data to a csv file
    dropped_file_path = os.path.join(command_line_args.outputDir, constants.FOLDER_LOGS,
                                     constants.OBA_DROPPED_DATA_FILE_NAME)
    data_csv_dropped.to_csv(path_or_buf=dropped_file_path, index=False)

    # merge dataframes
    merged_data_frame, num_matches_df = merge(gt_data, oba_data, command_line_args.tolerance)

    # Calculate difference
    merged_data_frame.loc[:, 'Time_Difference'] = merged_data_frame.apply(
        lambda x: (x['ClosestTime'] - x['Activity Start Date and Time* (UTC)']) / np.timedelta64(1, 's'), 1)

    df_time_diff = merged_data_frame.loc[:, ['Time_Difference']]
    df_time_diff = df_time_diff.dropna()
    print(df_time_diff.shape)
    # boxplot = df_time_diff.boxplot(column=['Time_Difference'])
    # path_figure = os.path.join(command_line_args.outputDir, constants.FOLDER_MERGED_DATA, "boxplot.png")
    # plt.savefig(path_figure, format='png')
    # plt.show()

    now = datetime.now()  # current date and time
    date_time = now.strftime("%y%m%d_%H%M")
    # Save merged data to csv
    merged_file_path = os.path.join(command_line_args.outputDir, constants.FOLDER_MERGED_DATA,
                                    constants.MERGED_DATA_FILE_NAME + "_" + date_time + "_" +
                                    str(command_line_args.tolerance) + ".csv")
    num_matches_file_path = os.path.join(command_line_args.outputDir, constants.FOLDER_MERGED_DATA,
                                    "num_matches" + "_" + date_time + "_" +
                                    str(command_line_args.tolerance) + ".csv")
    merged_data_frame.to_csv(path_or_buf=merged_file_path, index=False)
    num_matches_df.to_csv(path_or_buf=num_matches_file_path, index=False)


def merge(gt_data, oba_data, tolerance):
    """
    Merge gt_data dataframe and oba_data dataframe using the nearest value between columns 'gt_data.ClosestTime' and
    'oba_data.Activity Start Date and Time* (UTC)'. Before merging, the data is grouped by 'GT_Collector' on gt_data and
    each row on gt_data will be paired with one or none of the rows on oba_data grouped by userId.
    :param tolerance: maximum allowed difference (seconds) between 'gt_data.ClosestTime' and
    'oba_data.Activity Start Date and Time* (UTC)'.
    :param gt_data: dataframe with preprocessed data from ground truth XLSX data file
    :param oba_data: dataframe with preprocessed data from OBA firebase export CSV data file
    :return: dataframe with the merged data.
    """
    list_collectors = gt_data['GT_Collector'].unique()
    list_oba_users = oba_data['User ID'].unique()
    merged_df = pd.DataFrame()
    matches_df = pd.DataFrame(list_collectors, columns=['GT_Collector'])
    list_total_trips = []
    list_matches = []
    matches_dict = defaultdict(list)
    for collector in list_collectors:
        print("Merging data for collector ", collector)
        # Create dataframe for a collector on list_collectors
        gt_data_collector = gt_data[gt_data["GT_Collector"] == collector]
        # Make sure dataframe is sorted by 'ClosesTime'
        gt_data_collector.sort_values('ClosestTime', inplace=True)
        # Add total trips per collector
        list_total_trips.append(len(gt_data_collector))
        i = 0
        list_matches_by_phone = []
        for oba_user in list_oba_users:
            # Create a dataframe with the oba_user activities only
            oba_data_user = oba_data[oba_data["User ID"] == oba_user]
            # Make sure dataframes is sorted by 'Activity Start Date and Time* (UTC)'
            oba_data_user.sort_values('Activity Start Date and Time* (UTC)', inplace=True)

            temp_merge = pd.merge_asof(gt_data_collector, oba_data_user, left_on="ClosestTime",
                                       right_on="Activity Start Date and Time* (UTC)",
                                       direction="nearest",
                                       tolerance=pd.Timedelta(str(tolerance) + "ms"), left_by='GT_Mode',
                                       right_by='Google Activity')
            merged_df = pd.concat([merged_df, temp_merge], ignore_index=True)
            # Print number of matches
            print("\t Oba user", oba_user[-4:], "\tMatches: ", (temp_merge["User ID"] == oba_user).sum(), " out of ",
                  (temp_merge["GT_Collector"] == collector).sum())
            #matches_df[(matches_df["GT_Collector"] == collector)][oba_user] = (temp_merge["User ID"] == oba_user).sum()
            list_matches_by_phone.append((temp_merge["User ID"] == oba_user).sum())
            matches_dict[oba_user[-4:]].append((temp_merge["User ID"] == oba_user).sum())
            i += 1
        list_matches.append(list_matches_by_phone)
    matches_df['total_trips'] = list_total_trips
    numbers_df = pd.DataFrame.from_dict(matches_dict)
    matches_df = pd.concat([matches_df, numbers_df], axis=1)
    print("matches", matches_df.head())
    print("List of matches", list_matches)
    return merged_df, matches_df


if __name__ == '__main__':
    command_line_args = get_parser()
    main()
