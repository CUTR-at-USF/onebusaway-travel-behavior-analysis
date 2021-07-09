'''
/*
 * Copyright (C) 2019-2020 University of South Florida
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
 '''

# Import dependencies
from args import get_parser
import numpy as np
import pandas as pd
import datetime, os, random, math
import pytz



# -------------------------------------------

def main(args):
    # Verify the if the data folder exists
    if (not os.path.isdir(args.dataDir)):
        print("Data folder not found:", args.dataDir)
        exit()

    # Create sub-folders for ouput an logs
    path_logs = os.path.join(args.dataDir, "logs")
    if (not os.path.isdir(path_logs)):
        os.mkdir(path_logs)
    
    path_output = os.path.join(args.dataDir, "output")
    if (not os.path.isdir(path_output)):
        os.mkdir(path_output)

    # Create path OS independent for excel file
    excel_path = os.path.join(args.dataDir, "TH trips ExtraHeaders.xlsx")
    # Load ground truth data to a dataframe
    gt_data = pd.read_excel(excel_path)
    
    # Preprocess ground truth data
    gt_data = preprocessGtData(gt_data)
    print(gt_data.info())

    # Create path OS independent for csv file
    csv_path = os.path.join(args.dataDir, "travel-behavior.csv")
    # Load OBA data
    oba_data = pd.read_csv(csv_path)
    # Preprocess OBA data
    oba_data = preprocessObaData(oba_data, args)
    print("OBA data info()\n")
    print(oba_data.info())

    # Data preprocessing is over
    merged_data_frame = pd.merge_asof(gt_data, oba_data, on="ClosestTime", direction="nearest", tolerance=pd.Timedelta(str(args.tolerance)+"ms"))
    print(merged_data_frame.head())

    # Save to csv
    merged_file_path = os.path.join(args.dataDir, "output", "mergedData.csv")
    merged_data_frame.to_csv(path_or_buf =merged_file_path, index=False)
    

def preprocessObaData(data_csv, args):
    """ Preprocess the csv data file from oba-firebase-export as follows:
        - Change activity start date datatype from str to datetime
        - Drop observations whose activity start date are NaN after data type conversion
        - Drop observations that does not mathc the time span and distance requirements from args
          minActivitySpan and minTripLength
        - Add column reuired to be used as key while merging with ground truth data
    
    Args:
        data_csv: A data frame loaded from a csv file genrated by oba-firebase-export
        args: List of arguments from command prompt

    Retunrs:
        Preprocessed dataframe
    """
    # Change Activity Start Date and Time* (UTC) to datetime
    data_csv['Activity Start Date and Time* (UTC)']= pd.to_datetime(data_csv['Activity Start Date and Time* (UTC)'], errors='coerce', utc=True)
    
    # Drop NaN rows for relevant columns
    clean_data_csv = data_csv.dropna(subset= ['Activity Start Date and Time* (UTC)', 'Origin location Date and Time (*best) (UTC)', 
    'Duration* (minutes)', 'Origin-Destination Bird-Eye Distance* (meters)'])

    # Remove trips with Duration less than args.minActivitySpan mins and distance les than args.minTripLength
    clean_data_csv = clean_data_csv[(data_csv['Duration* (minutes)']>=args.minActivitySpan) & (data_csv['Origin-Destination Bird-Eye Distance* (meters)']>=args.minTripLength)]

    # Add the data to be dropped to a data frame
    data_csv_dropped = pd.merge(data_csv, clean_data_csv, how='outer', indicator=True).query("_merge != 'both'").drop('_merge', axis=1).reset_index(drop=True)

    # Save data to be dropped to a csv file
    dropped_file_path = os.path.join(args.dataDir, "logs", "droppedObaData.csv")
    data_csv_dropped.to_csv(path_or_buf = dropped_file_path, index=False)
    
    # Add column to be used in merge_asoft
    clean_data_csv['ClosestTime'] = clean_data_csv['Activity Start Date and Time* (UTC)']
    
    return clean_data_csv

def preprocessGtData(gt_data):
    # Drop unnamed columns
    unnamed_cols = [col for col in gt_data.columns if 'Unnamed' in col]
    gt_data = gt_data.drop(unnamed_cols, axis=1)

    # Replace ? by 0 to correct possible not rounded seconds
    gt_data.GT_TimeOrig = gt_data.GT_TimeOrig.astype(str)
    gt_data['GT_TimeOrig'] = gt_data['GT_TimeOrig'].str.replace('?','0')

    # Change the column to datetime.time, coerce will produce NaN if the change is not possible
    gt_data['GT_TimeOrig']= pd.to_datetime(gt_data['GT_TimeOrig'], errors='coerce').dt.time

    # Drop rows with NaN on GT_Date or GT_TimeOrig
    clean_gt_data = gt_data.dropna(subset= ['GT_Date', 'GT_TimeOrig'])

    # Add the data to be dropped to a data frame
    data_gt_dropped = pd.merge(gt_data, clean_gt_data, how='outer', indicator=True).query("_merge != 'both'").drop('_merge', axis=1).reset_index(drop=True)
    # Save data to be dropped to a csv file
    dropped_file_path = os.path.join(args.dataDir, "logs", "droppedGtData.csv")
    data_gt_dropped.to_csv(path_or_buf = dropped_file_path, index=False)

    # Create GT_DateTimeCombined column
    clean_gt_data.loc[:,'GT_DateTimeCombined'] = clean_gt_data.apply(lambda x: datetime.datetime.combine(x.GT_Date, x.GT_TimeOrig), 1)

    #Assign timezone to GT_DateTimeCombined
    clean_gt_data.loc[:,'GT_DateTimeCombined'] = clean_gt_data.apply(lambda x: pytz.timezone(x.GT_TimeZone).localize(x.GT_DateTimeCombined), 1)
    
    # Add column to be used in merge_asoft
    clean_gt_data['ClosestTime'] = clean_gt_data['GT_DateTimeCombined'].dt.tz_convert('UTC')
    return clean_gt_data

if __name__ == '__main__':
    args = get_parser()
    main(args)
