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

# Import dependencies
import argparse
import constants


def get_parser():
    parser = argparse.ArgumentParser()

    parser.add_argument('--obaFile', type=str, required=True, help='Path to CSV file exported from OBA Firebase '
                                                                   'Export App')

    parser.add_argument('--gtFile', type=str, required=True, help='Path to XLSX file including the Ground Truth data')

    parser.add_argument('--dataDir', type=str, default=constants.DATA_DIR,
                        help='Folder used to save output and log data from preprocess and merge')

    parser.add_argument('--minActivityDuration', type=float, default=constants.MIN_ACTIVITY_DURATION,
                        help='Minimum activity time span (minutes, default value = 5), shorter activities will be '
                             'dropped before merging.')

    parser.add_argument('--minTripLength', type=int, default=constants.MIN_TRIP_LENGTH,
                        help='Minimum length distance (meters, default value 50) for a trip. Shorter trips will be '
                             'dropped before merging')

    parser.add_argument('--tolerance', type=int, default=constants.TOLERANCE,
                        help='Maximum tolerated difference (milliseconds, default value 3000) between matched ground '
                             'truth data activity and OBA data activity')

    args = parser.parse_args()

    return args