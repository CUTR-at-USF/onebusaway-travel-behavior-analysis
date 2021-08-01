"""
Match and Merge simple test class.
"""

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

import unittest

class SimpleTest(unittest.TestCase):
  """
  Fibonacci numbers test class.
  """

  def setUp(self):
    """ Initialise test suite - no-op. """
    pass

  def tearDown(self):
    """ Clean up test suite - no-op. """
    pass

  def testAssert0(self):
    """ Test fibonacci(0). """
    self.assertEqual(0, 0)

if __name__ == '__main__':
  unittest.main()