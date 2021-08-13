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

import unittest
import pandas as pd

from src.gtMerger import preprocess, constants


class MergeTest(unittest.TestCase):
    """
    Merge dataframes by closest activity start time test class.
    """

    def setUp(self):
        """ Load dataframes used to perform tests. """
        self.oba_df = pd.read_csv("data_test/travel-behavior-test.csv")
        self.clean_oba_df, _ = preprocess.preprocess_oba_data(self.oba_df, 5, 50)
        self.gt_df = pd.read_excel("data_test/GT_test.xlsx")
        self.clean_gt_df, _ = preprocess.preprocess_gt_data(self.gt_df)
        pass

    def tearDown(self):
        """ Clean up test suite - no-op. """
        pass

    def test_no_nan(self):
        """ Test preprocess OBA has not NaN on relevant columns """
        self.assertEqual(0, self.clean_oba_df[constants.OBA_RELEVANT_COLS_LIST].isna().any().sum())
        pd._testing.assert_frame_equal(self.gt_df, self.gt_df)

    def test_datetime_type_column(self):
        """ Test Activity Start date and Time column was converted to datetime"""
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(self.clean_oba_df['Activity Start Date and Time* (UTC)']))

    def test_no_activities_duration_shorter_than_required(self):
        """ Test that duration of each of all activities is no shorter than required"""
        self.assertEqual(0, (self.clean_oba_df['Duration* (minutes)'] < constants.MIN_ACTIVITY_DURATION).sum())

    def test_no_activities_length_shorter_than_required(self):
        """ Test that length of each of all activities is no shorter than required"""
        self.assertEqual(0, (self.clean_oba_df['Origin-Destination Bird-Eye Distance* (meters)'] <
                         constants.MIN_TRIP_LENGTH).sum())


if __name__ == '__main__':
    unittest.main()
