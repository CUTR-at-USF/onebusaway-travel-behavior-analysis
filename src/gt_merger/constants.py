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
# Folder used to save output and log data from preprocess and merge
OUTPUT_DIR = 'merger_output'
# Default minimum activity duration (minutes)
MIN_ACTIVITY_DURATION = 5
# Default minimum distance (meters) for a trip.
MIN_TRIP_LENGTH = 25
# Default maximum tolerated difference (milliseconds) between matched ground truth data activity and OBA data activity'
TOLERANCE = 5000

# Folders to save logs an merged data
FOLDER_LOGS = 'logs'
FOLDER_MERGED_DATA = 'merged_data'

# File names for logs and output
GT_DROPPED_DATA_FILE_NAME = "droppedGtData.csv"
OBA_DROPPED_DATA_FILE_NAME = "droppedObaData.csv"
MERGED_DATA_FILE_NAME = "mergedData.csv"

# List of columns where NaN values are not allowed
OBA_RELEVANT_COLS_LIST = ['Activity Start Date and Time* (UTC)', 'Origin location Date and Time (*best) (UTC)',
                          'Duration* (minutes)', 'Origin-Destination Bird-Eye Distance* (meters)']
