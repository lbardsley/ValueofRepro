# Copyright 2018 The TensorFlow Hub Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""Tests for half plus two TF-Hub example."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import subprocess

import tensorflow as tf
import tensorflow_hub as hub

from tensorflow_hub import test_utils

EXPORT_TOOL_PATH = "org_tensorflow_hub/examples/half_plus_two/export"


class HalfPlusTwoTest(tf.test.TestCase):

  def testExportTool(self):
    # Use the export tool to create the Module.
    module_path = os.path.join(self.get_temp_dir(), "half-plus-two-module")

    export_tool_path = os.path.join(test_utils.test_srcdir(), EXPORT_TOOL_PATH)
    self.assertEquals(0, subprocess.call([export_tool_path, module_path]))

    # Test the Module computes (0.5*input + 2).
    with tf.Graph().as_default():
      m = hub.Module(module_path)
      output = m([10, 3, 4])
      with tf.Session() as session:
        session.run(tf.initializers.global_variables())
        self.assertAllEqual(session.run(output), [7, 3.5, 4])


if __name__ == "__main__":
  tf.test.main()
