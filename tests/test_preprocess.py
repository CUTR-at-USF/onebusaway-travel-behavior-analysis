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


class PreprocessTest(unittest.TestCase):
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
        pass

    def tearDown(self):
        """ Clean up test suite - no-op. """
        pass

    def test_oba_no_nan(self):
        """ Test preprocess OBA has not NaN on relevant columns """
        self.assertEqual(0, self.clean_oba_df[constants.OBA_RELEVANT_COLS_LIST].isna().any().sum())

    def test_oba_datetime_type_column(self):
        """ Test Activity Start date and Time column were converted to datetime"""
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(self.clean_oba_df['Activity Start Date and Time* (UTC)']))

    def test_oba_no_activities_duration_shorter_than_required(self):
        """ Test that duration of each of all activities is no shorter than required"""
        self.assertEqual(0, (self.clean_oba_df['Duration* (minutes)'] < constants.MIN_ACTIVITY_DURATION).sum())

    def test_oba_no_activities_length_shorter_than_required(self):
        """ Test that length of each of all activities is no shorter than required"""
        self.assertEqual(0, (self.clean_oba_df['Origin-Destination Bird-Eye Distance* (meters)'] <
                         constants.MIN_TRIP_LENGTH).sum())

    def test_gt_no_unnamed_cols(self):
        """ Test that unnamed columns were removed"""
        unnamed_cols = [col for col in self.clean_gt_df.columns if 'Unnamed' in col]
        self.assertFalse(unnamed_cols)

    def test_gt_datetime_type_column(self):
        """ Test that 'GT_DateTimeDestUTC' was converted to datetime, this column is used for asoft merging"""
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(self.clean_gt_df['GT_DateTimeDestUTC']))


if __name__ == '__main__':
    unittest.main()
