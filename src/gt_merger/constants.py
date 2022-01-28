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
MIN_ACTIVITY_DURATION = 2
# Default minimum distance (meters) for a trip.
MIN_TRIP_LENGTH = 20
# Default maximum tolerated difference (milliseconds) between matched ground truth data activity and OBA data activity'
TOLERANCE = 3600000

# Folders to save logs an merged data
FOLDER_LOGS = 'logs'
FOLDER_MERGED_DATA = 'merged_data'

# File names for logs and output
GT_DROPPED_DATA_FILE_NAME = "droppedGtData.csv"
OBA_DROPPED_DATA_FILE_NAME = "droppedObaData.csv"
MERGED_DATA_FILE_NAME = "mergedData"

# List of columns where NaN values are not allowed
OBA_RELEVANT_COLS_LIST = ['Activity Start Date and Time* (UTC)', 'Origin location Date and Time (*best) (UTC)',
                          'Duration* (minutes)', 'Origin-Destination Bird-Eye Distance* (meters)',
                          'Destination Location Date and Time (*best) (UTC)']
GT_RELEVANT_COLS_LIST = ['GT_Date', 'GT_TimeOrig', 'GT_TimeDest']

# Boolean to generate results in tolerance ranges every N milliseconds up to the TOLERANCE value
CALCULATE_EVERY_N_SECS = 30000

# New columns order for merged dataframe
GT_NEW_COLUMNS_ORDER = ['GT_Collector', 'GT_Date', 'GT_TimeOrig',
                        'GT_TimeOrigMinuteRounded', 'GT_TimeZone', 'GT_LatOrig', 'GT_LonOrig', 'GT_LocationOrig',
                        'GT_TimeDest', 'GT_TimeDestMinuteRounded', 'GT_LatDest', 'GT_LonDest', 'GT_LocDest',
                        'GT_Comments',
                        'GT_DateTimeCombined', 'GT_DateTimeDestCombined',
                        'GT_TourID', 'GT_TripID', 'GT_Mode', 'GT_DateTimeOrigUTC_Backup', 'GT_DateTimeDestUTC']
OBA_NEW_COLUMNS_ORDER = ['Google Activity', 'Activity Start Date and Time* (UTC)',
                         'Activity Destination Date and Time* (UTC)',
                         'Manual Assignment', 'Trip ID', 'User ID', 'Device Trip ID', 'Google Activity Confidence',
                         'Time_Difference', 'Distance_Difference', 'Time_Difference_Destination',
                         'Distance_Difference_Destination', 'Vehicle type', 'Region ID',
                         'Origin location Date and Time (*best) (UTC)',
                         'Activity Start/Origin Time Diff* (minutes)', 'Origin latitude (*best)',
                         'Origin longitude (*best)',
                         'Origin Horizontal Accuracy (meters) (*best)', 'Origin Location Provider (*best)',
                         'Destination Location Date and Time (*best) (UTC)',
                         'Activity End/Destination Time Diff* (minutes)', 'Destination latitude (*best)',
                         'Destination longitude (*best)', 'Destination Horizontal Accuracy (meters) (*best)',
                         'Destination Location Provider (*best)', 'Duration* (minutes)',
                         'Origin-Destination Bird-Eye Distance* (meters)', 'Chain ID', 'Chain Index', 'Tour ID',
                         'Tour Index', 'Ignoring Battery Optimizations', 'Talk Back Enabled', 'Power Save Mode Enabled',
                         'Origin fused Date and Time (UTC)', 'Origin fused latitude', 'Origin fused longitude',
                         'Origin fused Horizontal Accuracy (meters)', 'Origin gps Date and Time (UTC)',
                         'Origin gps latitude', 'Origin gps longitude', 'Origin gps Horizontal Accuracy (meters)',
                         'Origin network Date and Time (UTC)', 'Origin network latitude', 'Origin network longitude',
                         'Origin network Horizontal Accuracy (meters)', 'Destination fused Date and Time (UTC)',
                         'Destination fused latitude', 'Destination fused longitude',
                         'Destination fused Horizontal Accuracy (meters)', 'Destination gps Date and Time (UTC)',
                         'Destination gps latitude', 'Destination gps longitude',
                         'Destination gps Horizontal Accuracy (meters)', 'Destination network Date and Time (UTC)',
                         'Destination network latitude', 'Destination network longitude',
                         'Destination network Horizontal Accuracy (meters)', 'GT_DateTimeOrigUTC']

OBA_UNMATCHED_NEW_COLUMNS_ORDER = ['Google Activity', 'Activity Start Date and Time* (UTC)',
                                   'Activity Destination Date and Time* (UTC)',
                                   'Trip ID', 'User ID', 'Device Trip ID',
                                   'Google Activity Confidence',
                                   'Vehicle type', 'Region ID',
                                   'Origin location Date and Time (*best) (UTC)',
                                   'Activity Start/Origin Time Diff* (minutes)', 'Origin latitude (*best)',
                                   'Origin longitude (*best)',
                                   'Origin Horizontal Accuracy (meters) (*best)', 'Origin Location Provider (*best)',
                                   'Destination Location Date and Time (*best) (UTC)',
                                   'Activity End/Destination Time Diff* (minutes)', 'Destination latitude (*best)',
                                   'Destination longitude (*best)', 'Destination Horizontal Accuracy (meters) (*best)',
                                   'Destination Location Provider (*best)', 'Duration* (minutes)',
                                   'Origin-Destination Bird-Eye Distance* (meters)', 'Chain ID', 'Chain Index',
                                   'Tour ID',
                                   'Tour Index', 'Ignoring Battery Optimizations', 'Talk Back Enabled',
                                   'Power Save Mode Enabled',
                                   'Origin fused Date and Time (UTC)', 'Origin fused latitude',
                                   'Origin fused longitude',
                                   'Origin fused Horizontal Accuracy (meters)', 'Origin gps Date and Time (UTC)',
                                   'Origin gps latitude', 'Origin gps longitude',
                                   'Origin gps Horizontal Accuracy (meters)',
                                   'Origin network Date and Time (UTC)', 'Origin network latitude',
                                   'Origin network longitude',
                                   'Origin network Horizontal Accuracy (meters)',
                                   'Destination fused Date and Time (UTC)',
                                   'Destination fused latitude', 'Destination fused longitude',
                                   'Destination fused Horizontal Accuracy (meters)',
                                   'Destination gps Date and Time (UTC)',
                                   'Destination gps latitude', 'Destination gps longitude',
                                   'Destination gps Horizontal Accuracy (meters)',
                                   'Destination network Date and Time (UTC)',
                                   'Destination network latitude', 'Destination network longitude',
                                   'Destination network Horizontal Accuracy (meters)']
