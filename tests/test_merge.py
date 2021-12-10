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
import unittest
import pandas as pd

from src.gt_merger import preprocess, constants
from src.gt_merger.matchAndMerge import merge


class MergeTest(unittest.TestCase):
    """
    Merge dataframes by closest activity start time test class.
    """

    def setUp(self):
        """ Load dataframes used to perform tests. """
        oba_file_path = os.path.join(os.path.dirname(__file__), 'data_test/travel-behavior-test.csv')
        self.oba_df = pd.read_csv(oba_file_path)
        self.clean_oba_df, _ = preprocess.preprocess_oba_data(self.oba_df, 5, 50, True)
        gt_file_path = os.path.join(os.path.dirname(__file__), 'data_test/GT_test.xlsx')
        self.gt_df = pd.read_excel(gt_file_path, engine='openpyxl')
        self.clean_gt_df, _ = preprocess.preprocess_gt_data(self.gt_df, True)
        self.merged_data_frame, _ = merge(self.clean_gt_df, self.clean_oba_df, 3000)
        pass

    def tearDown(self):
        """ Clean up test suite - no-op. """
        pass

    def test_first_merge(self):
        """ Test preprocess OBA has not NaN on relevant columns """
        print(self.merged_data_frame)
        self.assertTrue((self.merged_data_frame.loc[0, 'GT_Collector'] == 'Stark') &
                        (self.merged_data_frame.loc[0, 'GT_TourID'] == 1) &
                        (self.merged_data_frame.loc[0, 'GT_TripID'] == 1) &
                        (self.merged_data_frame.loc[0, 'User ID'] == 'obaUser_006') &
                        (self.merged_data_frame.loc[0, 'Trip ID'] == 241))

    def test_second_merge(self):
        """ Test preprocess OBA has not NaN on relevant columns """
        print(self.merged_data_frame)
        self.assertTrue((self.merged_data_frame.loc[16, 'GT_Collector'] == 'Stark') &
                        (self.merged_data_frame.loc[16, 'GT_TourID'] == 1) &
                        (self.merged_data_frame.loc[16, 'GT_TripID'] == 1) &
                        (self.merged_data_frame.loc[16, 'User ID'] == 'obaUser_008') &
                        (self.merged_data_frame.loc[16, 'Trip ID'] == 241))


if __name__ == '__main__':
    unittest.main()
