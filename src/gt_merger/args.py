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
from src.gt_merger import constants


def get_parser():
    parser = argparse.ArgumentParser()

    parser.add_argument('--obaFile', type=str, required=True, help='Path to CSV file exported from OBA Firebase '
                                                                   'Export App')

    parser.add_argument('--gtFile', type=str, required=True, help='Path to XLSX file including the Ground Truth data')

    parser.add_argument('--outputDir', type=str, default=constants.OUTPUT_DIR,
                        help='Path to directory where the merged data and log data will be output')

    parser.add_argument('--minActivityDuration', type=float, default=constants.MIN_ACTIVITY_DURATION,
                        help='Minimum activity time span (minutes, default value = ' +
                             str(constants.MIN_ACTIVITY_DURATION) +
                             '), shorter activities will be dropped before merging.')

    parser.add_argument('--minTripLength', type=int, default=constants.MIN_TRIP_LENGTH,
                        help='Minimum length distance (meters, default value ' + str(constants.MIN_TRIP_LENGTH) +
                             ') for a trip. Shorter trips will be dropped before merging')

    parser.add_argument('--tolerance', type=int, default=constants.TOLERANCE,
                        help='Maximum tolerated difference (milliseconds, default value ' + str(constants.TOLERANCE) +
                             ') between matched ground truth data activity and OBA data activity')

    parser.add_argument('--iterateOverTol', dest='iterateOverTol', action='store_true')
    parser.add_argument('--no-iterateOverTol', dest='iterateOverTol', action='store_false')
    parser.set_defaults(iterateOverTol=False)

    parser.add_argument('--removeStillMode', dest='removeStillMode', action='store_true')
    parser.add_argument('--no-removeStillMode', dest='removeStillMode', action='store_false')
    parser.set_defaults(removeStillMode=True)

    parser.add_argument('--mergeOneToOne', dest='mergeOneToOne', action='store_true')
    parser.add_argument('--no-mergeOneToOne', dest='mergeOneToOne', action='store_false')
    parser.set_defaults(mergeOneToOne=False)

    parser.add_argument('--repeatGtRows', dest='repeatGtRows', action='store_true')
    parser.add_argument('--no-repeatGtRows', dest='repeatGtRows', action='store_false')
    parser.set_defaults(mergeOneToOne=False)

    parser.add_argument('--deviceList', type=str, default="",
                        help='Path to txt file including white list of OBA devices to be used for match and merge')

    args = parser.parse_args()

    return args
