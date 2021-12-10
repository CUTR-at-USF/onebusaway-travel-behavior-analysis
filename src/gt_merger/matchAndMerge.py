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
import os
# Import dependencies
from collections import defaultdict
from pathlib import Path

import haversine as hs
import numpy as np
import pandas as pd
from haversine import Unit

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

    # Verify if there is a list of devices
    if command_line_args.deviceList:
        # Verify if the list of devices file exists
        if os.path.isfile(command_line_args.deviceList):
            with open(command_line_args.deviceList) as f:
                list_of_devices = f.readline().split(",")
                list_of_devices = [s.strip() for s in list_of_devices]
        else:
            print("File with white list of devices not found:", command_line_args.deviceList)
            exit()
    else:
        list_of_devices = []

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
    gt_data, data_gt_dropped = preprocess_gt_data(gt_data, command_line_args.removeStillMode)

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

    # If a devices white list was provided, list the devices
    if list_of_devices:
        oba_data = oba_data[oba_data["User ID"].isin(list_of_devices)]

    # Preprocess OBA data
    oba_data, data_csv_dropped = preprocess_oba_data(oba_data, command_line_args.minActivityDuration,
                                                     command_line_args.minTripLength, command_line_args.removeStillMode)
    print("OBA data preprocessed.")
    print(oba_data.info())
    print(gt_data.info())

    # Data preprocessing IS OVER
    # Save oba dropped data to a csv file
    dropped_file_path = os.path.join(command_line_args.outputDir, constants.FOLDER_LOGS,
                                     constants.OBA_DROPPED_DATA_FILE_NAME)
    data_csv_dropped.to_csv(path_or_buf=dropped_file_path, index=False)

    if command_line_args.iterateOverTol:
        first_tol = 30000
        save_to_path = os.path.join(constants.FOLDER_MERGED_DATA, "batch")
    else:
        save_to_path = os.path.join(constants.FOLDER_MERGED_DATA)
        first_tol = constants.TOLERANCE

    for tol in range(first_tol, command_line_args.tolerance + 1, constants.CALCULATE_EVERY_N_SECS):
        print("TOLERANCE:", str(tol))
        # merge dataframes one to one or one to many according to the commandline parameter
        if command_line_args.mergeOneToOne:
            merged_data_frame, num_matches_df = merge(gt_data, oba_data, tol)
        else:
            merged_data_frame, num_matches_df, unmatched_oba_trips_df = merge_to_many(gt_data, oba_data, tol)
            # Save unmatched oba records to csv
            unmatched_file_path = os.path.join(command_line_args.outputDir, save_to_path,
                                               "oba_records_without_match_on_GT.csv")
            unmatched_oba_trips_df.to_csv(path_or_buf=unmatched_file_path, index=False)

        # Calculate difference
        merged_data_frame['Time_Difference'] = merged_data_frame.apply(
            lambda x: (x['Activity Start Date and Time* (UTC)'] - x['GT_DateTimeOrigUTC_Backup']) / np.timedelta64(1, 's')
            if pd.notna(x['Activity Start Date and Time* (UTC)']) else "", 1)

        # Calculate distance between GT and OBA starting points
        merged_data_frame['Distance_Difference'] = merged_data_frame.apply(
            lambda row: hs.haversine((row['GT_LatOrig'], row['GT_LonOrig']),
                                     (row['Origin latitude (*best)'], row['Origin longitude (*best)']),
                                     unit=Unit.METERS), axis=1)

        # Add Manual Assignment Column before reorganize
        merged_data_frame["Manual Assignment"] = ''
        # Reorder merged dataframe columns
        new_column_orders = constants.GT_NEW_COLUMNS_ORDER + constants.OBA_NEW_COLUMNS_ORDER
        merged_data_frame = merged_data_frame[new_column_orders]
        # Save merged data to csv
        merged_file_path = os.path.join(command_line_args.outputDir, save_to_path,
                                        constants.MERGED_DATA_FILE_NAME + "_" + str(tol) + ".csv")
        num_matches_file_path = os.path.join(command_line_args.outputDir, save_to_path,
                                             "num_matches" + "_" + str(tol) + ".csv")
        merged_data_frame.to_csv(path_or_buf=merged_file_path, index=False)
        num_matches_df.to_csv(path_or_buf=num_matches_file_path, index=False)


def merge(gt_data, oba_data, tolerance):
    """
    Merge gt_data dataframe and oba_data dataframe using the nearest value between columns 'gt_data.GT_DateTimeOrigUTC' and
    'oba_data.Activity Start Date and Time* (UTC)'. Before merging, the data is grouped by 'GT_Collector' on gt_data and
    each row on gt_data will be paired with one or none of the rows on oba_data grouped by userId.
    :param tolerance: maximum allowed difference (seconds) between 'gt_data.GT_DateTimeOrigUTC' and
    'oba_data.Activity Start Date and Time* (UTC)'.
    :param gt_data: dataframe with preprocessed data from ground truth XLSX data file
    :param oba_data: dataframe with preprocessed data from OBA firebase export CSV data file
    :return: dataframe with the merged data and a dataframe with summary of matches by collector/oba_user(phone).
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
        gt_data_collector.sort_values('GT_DateTimeOrigUTC', inplace=True)
        # Add total trips per collector
        list_total_trips.append(len(gt_data_collector))
        i = 0
        list_matches_by_phone = []
        for oba_user in list_oba_users:
            # Create a dataframe with the oba_user activities only
            oba_data_user = oba_data[oba_data["User ID"] == oba_user]
            # Make sure dataframes is sorted by 'Activity Start Date and Time* (UTC)'
            oba_data_user.sort_values('Activity Start Date and Time* (UTC)', inplace=True)

            temp_merge = pd.merge_asof(gt_data_collector, oba_data_user, left_on="GT_DateTimeOrigUTC",
                                       right_on="Activity Start Date and Time* (UTC)",
                                       direction="forward",
                                       tolerance=pd.Timedelta(str(tolerance) + "ms"), left_by='GT_Mode',
                                       right_by='Google Activity')
            merged_df = pd.concat([merged_df, temp_merge], ignore_index=True)
            # Print number of matches
            print("\t Oba user", oba_user[-4:], "\tMatches: ", (temp_merge["User ID"] == oba_user).sum(), " out of ",
                  (temp_merge["GT_Collector"] == collector).sum())

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


def merge_to_many(gt_data, oba_data, tolerance):
    """
    Merge gt_data dataframe and oba_data dataframe using the nearest value between columns 'gt_data.GT_DateTimeOrigUTC' and
    'oba_data.Activity Start Date and Time* (UTC)'. Before merging, the data is grouped by 'GT_Collector' on gt_data and
    each row on gt_data will be paired with one or none of the rows on oba_data grouped by userId.
    :param tolerance: maximum allowed difference (seconds) between 'gt_data.GT_DateTimeOrigUTC' and
    'oba_data.Activity Start Date and Time* (UTC)'.
    :param gt_data: dataframe with preprocessed data from ground truth XLSX data file
    :param oba_data: dataframe with preprocessed data from OBA firebase export CSV data file
    :return: dataframe with the merged data.
    """
    # List of unique collectors and and unique users
    list_collectors = gt_data['GT_Collector'].unique()
    list_oba_users = oba_data['User ID'].unique()

    # Create empty dataframes to be returned
    merged_df = pd.DataFrame()
    matches_df = pd.DataFrame()
    all_unmatched_trips_df = pd.DataFrame()

    list_total_trips = []
    for collector in list_collectors:
        print("Merging data for collector ", collector)
        # Create dataframe for a collector on list_collectors
        gt_data_collector = gt_data[gt_data["GT_Collector"] == collector]
        # Make sure dataframe is sorted by 'ClosesTime'
        gt_data_collector.sort_values('GT_DateTimeOrigUTC', inplace=True)
        # Add total trips per collector
        list_total_trips.append(len(gt_data_collector))
        i = 0
        for oba_user in list_oba_users:
            # Create a dataframe with the oba_user activities only
            oba_data_user = oba_data[oba_data["User ID"] == oba_user]
            # Make sure dataframes is sorted by 'Activity Start Date and Time* (UTC)'
            oba_data_user.sort_values('Activity Start Date and Time* (UTC)', inplace=True)

            # Create df for OBA trips without GT Data match
            oba_unmatched_trips_df = oba_data_user.copy()

            # Iterate over each trip of one collector to match it with zero to many activities of an oba_data_user
            for index, row in gt_data_collector.iterrows():
                bunch_of_matches = oba_data_user[(oba_data_user['Activity Start Date and Time* (UTC)'] >=
                                                 row['GT_DateTimeOrigUTC']) &
                                                 (oba_data_user['Activity Start Date and Time* (UTC)'] <=
                                                  row['GT_DateTimeDestUTC'])
                                                 ]
                # Get the size of bunch_of_matches to create a repeated dataframe to concatenate with
                if bunch_of_matches.empty:
                    len_bunch = 1
                else:
                    len_bunch = bunch_of_matches.shape[0]
                    # Remove matched rows from unmatched trips df
                    oba_unmatched_trips_df = pd.merge(oba_unmatched_trips_df, bunch_of_matches, indicator=True, how='outer').\
                        query('_merge=="left_only"').drop('_merge', axis=1)

                subset_df = gt_data_collector.loc[[index], :]
                # Repeat the firs row `len_bunch` times.
                new_df = pd.DataFrame(np.repeat(subset_df.values, len_bunch, axis=0))
                new_df.columns = gt_data_collector.columns
                # Add backup Start Time Columns
                new_df['GT_DateTimeOrigUTC_Backup'] = new_df['GT_DateTimeOrigUTC']

                # Remove (Fill with NaN) repeated GT rows unless required no to
                if len_bunch > 1 and not command_line_args.repeatGtRows:
                    new_df.loc[1:, new_df.columns.difference(['GT_DateTimeOrigUTC', 'GT_LatOrig', 'GT_LonOrig',
                                                              'GT_TourID', 'GT_TripID'])] = np.NaN

                temp_merge = pd.concat([new_df.reset_index(drop=True), bunch_of_matches.reset_index(drop=True)],
                                       axis=1)
                # Make sure the bunch of matches has the 'User Id' even for the empty rows
                temp_merge["User ID"] = oba_user
                # Merge running matches with current set of found matches
                merged_df = pd.concat([merged_df, temp_merge], ignore_index=True)

                # Add oba_user and number of many matches to the matches_df
                subset_df["User ID"] = oba_user[-4:]
                subset_df["GT_NumberOfTransitions"] = 0 if bunch_of_matches.empty else len_bunch
                matches_df = pd.concat([matches_df, subset_df], ignore_index=True)

            # Reorder the OBA columns
            oba_unmatched_trips_df= oba_unmatched_trips_df[constants.OBA_UNMATCHED_NEW_COLUMNS_ORDER]
            # Add Collector and device to unmatched trips
            oba_unmatched_trips_df['User ID'] = oba_user[-4:]
            # oba_unmatched_trips_df['GT_Collector'] = collector
            oba_unmatched_trips_df.insert(loc=0, column='GT_Collector', value=collector)
            # Append the unmatched trips per collector/device to the all unmatched df
            all_unmatched_trips_df = pd.concat([all_unmatched_trips_df, oba_unmatched_trips_df], ignore_index=True)

    return merged_df, matches_df, all_unmatched_trips_df


if __name__ == '__main__':
    command_line_args = get_parser()
    main()
