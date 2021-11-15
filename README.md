# onebusaway-travel-behavior-analysis [![Python application](https://github.com/CUTR-at-USF/onebusaway-travel-behavior-analysis/actions/workflows/python-app.yml/badge.svg)](https://github.com/CUTR-at-USF/onebusaway-travel-behavior-analysis/actions/workflows/python-app.yml)
Python utilities to process and analyze travel behavior data collected by OneBusAway and exported as csv file by oba-firebase-export.

### matchAndMerge utility
This utility matches ground truth data activities in excel format with activities data generated by oba-firebase-export in csv format. The algorithm will match each activity in the ground truth dataset with the nearest activity in the oba-firebase-export generated file. 

### Run
To run the matchAndMerge script use `python` command and pass the desired arguments:
`python matchAndMerge.py --obaFile obaFile.csv --gtFile gtFile.xlsx`

### Required Input Data
matchAndMerge works over two expected input data files, one generates from OBA firebase export and one containing the ground truth data:
* `--obaFile <oba csv file>` A csv file generated by [OBA firebase export](https://github.com/CUTR-at-USF/onebusaway-firebase-export).
The csv file must include the following columns:
  * `Activity Start Date and Time* (UTC)` Date and time recorded for the start of the activity using UTC timezone.
  * `Origin location Date and Time (*best) (UTC)` Date and time recorded for the location where the activity started using UTC timezone.
  * `Duration* (minutes)` Duration of the activity in minutes.
  * `Origin-Destination Bird-Eye Distance* (meters)` Euclidean distance (meters) between origin and destination recorded for the activity.
  * `Google Activity` Detected activity including Android supported activities plus 'OBA firebase export' additional activities ('IN_VEHICLE', 'ON_BICYCLE', 'RUNNING', 'WALKING', 'WALKING/RUNNING', 'STILL')
* `--gtFile <ground truth xlsx file>` A xlsx file that must be formatted as shown below. The main (required) column descriptions are:
  * `GT_Collector` User name of the GT data collector
  * `GT_Mode` Activity mode ('WALKING', 'IN_VEHICLE', 'STILL', 'ON_BICYCLE', 'IN_BUS')
  * `GT_Date` Date of the recorded activity
  * `GT_TimeOrig` Time recorded at the origin of the recorded activity
  * `GT_TimeMinuteRounded` One (1) if the `GT_TimeOrig` value was rounded to the closest minute while recording the activity, zero (0) otherwise.
  * `GT_TimeZone` Time zone for the recorded activity
  * `GT_TimeDest` Time recorded at the destination of the recorded activity
  * `GT_TimeDestMinuteRounded` One (1) if the `GT_TimeDest` value was rounded to the closest minute while recording the activity, zero (0) otherwise.

| GT_Collector | GT_TourID | GT_TripID | GT_Mode    | GT_Date  | GT_TimeOrig | GT_TimeMinuteRounded | GT_TimeZone     | GT_LatOrig | GT_LonOrig | GT_LocationOrig  | GT_TimeDest | GT_TimeDestMinuteRounded | GT_LatDest | GT_LonDest | GT_LocDest      |
|--------------|-----------|-----------|------------|----------|-------------|----------------------|-----------------|------------|------------|------------------|-------------|--------------------------|------------|------------|-----------------|
| DoeJohn      | 1         | 1         | IN_VEHICLE | 3/4/2021 | 3:28:15 PM  | 0                    | America/Chicago | 33.588713  | -76.33308  | 2045 Small St    | 3:40:10 PM  | 1                        | 35.617885  | -76.312499 | 305 Large Dr    |
| DoeJohn      | 1         | 2         | WALKING    | 3/4/2021 | 3:41:51 PM  | 0                    | America/Chicago | 23.617885  | -86.312499 | 305 Holly Dr     | 3:58:01 PM  | 0                        | 43.615829  | -86.305452 | Red Pen River   |
| DoeJohn      | 1         | 3         | STILL      | 3/4/2021 | 3:58:20 PM  | 0                    | America/Chicago | 35.615829  | -61.305452 | Red Pen River    | 4:19:05 PM  | 0                        | 56.615829  | -61.305452 | Red Pen River   |
| DoeJohn      | 1         | 4         | WALKING    | 3/4/2021 | 4:20:00 PM  | 1                    | America/Chicago | 43.615829  | -67.305452 | Red Pen River    | 4:59:15 PM  | 0                        | 65.617885  | -67.312499 | 305 Holly Dr    |

### Additional Optional Command Line Arguments 
* `--outputDir <data folder>` Takes a string with the name of the folder where the merged data and log files will be stored. If the folder does not exist, the application will try to create it. The default values is `merger_output`. Example usage:
`--outputDir outputData` will look for the folder `outputData`.
* `--minActivityDuration <minutes>` Minimum activity time span (in minutes), shorter activities will be dropped before merging. The default values is 5 minutes. For example `--minActivityDuration 3` will remove, from the oba generated data, activities whose duration is less than 3 minutes.
* `--minTripLength <meters>` Minimum distance (in meters) for a trip. Shorter trips will be dropped before merging. The default values is 50 meters. Example usage:
`--minTripLength 60` will remove, from the oba generated data, activities whose `Origin-Destination Bird-Eye Distance* (meters)` is less than 60 meters.
* `--tolerance <milliseconds>` Maximum tolerated difference (milliseconds) between matched ground truth data start activity and OBA data start activity. 
By default, it is 3000 milliseconds. Example usage: `--tolerance 5000` will consider only a difference equal or less than 5000 milliseconds while looking for a match between a ground truth data start activity and a OBA data start activity.
* `no-iterateOverTol` When used, the merging process will only be applied once over the tolerance defined by `tolerance`. 
By default, the merging process is applied over tolerances iterating from 30000 to `tolerance` in steps of 30000.
Example usage: `no-iterateOverTol`.
* `--no-removeStillMode` When used, preprocess of input datasets will not eliminate the records with activity mode equal to `STILL`.
By default, preprocess of input dataset eliminates the records with activity mode equal to `STILL`.
Example usage: `--no-removeStillMode`.
* `--mergeOneToOne` This flag will force the merging system to merge each `Ground Truth trip` with one and only one OBA 
record according to the other command line parameters. By default, this flag is set to False. In such case, the merger 
will match each `Ground Truth trip` with all the OBa records that starts after the `Ground Truth trip` starts and before
the `Ground Truth trip` ends. Example usage: `--mergeOneToOne`
* `--repeatGtRows` This flag will force the merging system to repeat a GT trip as many rows as matches are found
before exporting the output. By default, this flag is set to False. In such case, the merger wil only include
one DT data row per trip while merging with a device. Example usage: `--repeatGtRows`

### Acknowledgements

This project was funded under the [National Institute for Congestion Reduction (NICR)](https://nicr.usf.edu/2020/12/11/3-1-influencing-travel-behavior-via-open-source-platform/).

### License

```
/*
 * Copyright (C) 2021 University of South Florida
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
 ```
