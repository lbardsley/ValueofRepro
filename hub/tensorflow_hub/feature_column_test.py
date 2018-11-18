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
"""Tests for tensorflow_hub.feature_column."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np
import tensorflow as tf
import tensorflow_hub as hub


def text_module_fn():
  embeddings = [
      ("", [0, 0, 0, 0]),  # OOV items are mapped to this embedding.
      ("hello world", [1, 2, 3, 4]),
      ("pair-programming", [5, 5, 5, 5]),
  ]
  keys = tf.constant([item[0] for item in embeddings], dtype=tf.string)
  indices = tf.constant(list(range(len(embeddings))), dtype=tf.int64)
  tbl_init = tf.contrib.lookup.KeyValueTensorInitializer(keys, indices)
  table = tf.contrib.lookup.HashTable(tbl_init, 0)

  weights_initializer = tf.cast(
      tf.constant(list([item[1] for item in embeddings])),
      tf.float32)

  weights = tf.get_variable(
      "weights",
      dtype=tf.float32,
      initializer=weights_initializer)

  text_tensor = tf.placeholder(dtype=tf.string, name="text", shape=[None])
  indices_tensor = table.lookup(text_tensor)
  embedding_tensor = tf.gather(weights, indices_tensor)
  hub.add_signature(inputs=text_tensor, outputs=embedding_tensor)


def invalid_text_module_fn():
  text = tf.placeholder(tf.string, shape=[10])
  hub.add_signature(inputs=text, outputs=tf.zeros([10, 3]))


class TextEmbeddingColumnTest(tf.test.TestCase):

  def setUp(self):
    self.spec = hub.create_module_spec(text_module_fn)

  def testVariableShape(self):
    text_column = hub.text_embedding_column("text", self.spec, trainable=False)
    self.assertEqual(text_column._variable_shape, [4])

  def testMakeParseExampleSpec(self):
    text_column = hub.text_embedding_column("text", self.spec, trainable=False)
    parsing_spec = tf.feature_column.make_parse_example_spec([text_column])
    self.assertEqual(parsing_spec, {
        "text": tf.FixedLenFeature([1], dtype=tf.string)
    })

  def testInputLayer(self):
    features = {
        "text_a": ["hello world", "pair-programming"],
        "text_b": ["hello world", "oov token"],
    }
    feature_columns = [
        hub.text_embedding_column("text_a", self.spec, trainable=False),
        hub.text_embedding_column("text_b", self.spec, trainable=False),
    ]
    with tf.Graph().as_default():
      input_layer = tf.feature_column.input_layer(features, feature_columns)
      with tf.train.MonitoredSession() as sess:
        output = sess.run(input_layer)
        self.assertAllEqual(output, [[1, 2, 3, 4, 1, 2, 3, 4],
                                     [5, 5, 5, 5, 0, 0, 0, 0]])

  def testWorksWithCannedEstimator(self):
    comment_embedding_column = hub.text_embedding_column(
        "comment", self.spec, trainable=False)
    upvotes = tf.feature_column.numeric_column("upvotes")

    feature_columns = [comment_embedding_column, upvotes]
    estimator = tf.estimator.DNNClassifier(
        hidden_units=[10],
        feature_columns=feature_columns,
        model_dir=self.get_temp_dir())

    # This only tests that estimator apis are working with the feature
    # column without throwing exceptions.
    features = {
        "comment": np.array([
            ["the quick brown fox"],
            ["spam spam spam"],
        ]),
        "upvotes": np.array([
            [20],
            [1],
        ]),
    }
    labels = np.array([[1], [0]])
    input_fn = tf.estimator.inputs.numpy_input_fn(
        features, labels, shuffle=True)
    estimator.train(input_fn, max_steps=1)
    estimator.evaluate(input_fn, steps=1)
    estimator.predict(input_fn)

  def testTrainableEmbeddingColumn(self):
    feature_columns = [
        hub.text_embedding_column("text", self.spec, trainable=True),
    ]

    with tf.Graph().as_default():
      features = {
          "text": ["hello world", "pair-programming"],
      }
      target = [[1, 1, 1, 1], [4, 3, 2, 1]]
      input_layer = tf.feature_column.input_layer(features, feature_columns)

      loss = tf.losses.mean_squared_error(input_layer, target)
      optimizer = tf.train.GradientDescentOptimizer(learning_rate=0.97)
      train_op = optimizer.minimize(loss)

      with tf.train.MonitoredSession() as sess:
        self.assertAllEqual(sess.run(input_layer), [[1, 2, 3, 4], [5, 5, 5, 5]])
        for _ in range(10):
          sess.run(train_op)
        self.assertAllClose(sess.run(input_layer), target, atol=0.5)

  def testInvalidTextModule(self):
    spec = hub.create_module_spec(invalid_text_module_fn)
    with self.assertRaisesRegexp(ValueError, "only one input"):
      hub.text_embedding_column("coment", spec, trainable=False)


def image_module_fn():
  """Maps 1x2 images to sums of each color channel."""
  images = tf.placeholder(dtype=tf.float32, shape=[None, 1, 2, 3])
  sum_channels = tf.reduce_sum(images, axis=[1, 2])
  hub.add_signature(inputs={"images": images}, outputs=sum_channels)


class ImageEmbeddingColumnTest(tf.test.TestCase):

  def setUp(self):
    self.spec = hub.create_module_spec(image_module_fn)

  def testExpectedImageSize(self):
    image_column = hub.image_embedding_column("image", self.spec)
    # The usage comment recommends this code pattern, so we test it here.
    self.assertSequenceEqual(
        hub.get_expected_image_size(image_column.module_spec), [1, 2])

  def testVariableShape(self):
    image_column = hub.image_embedding_column("image", self.spec)
    self.assertEqual(image_column._variable_shape, [3])

  def testMakeParseExampleSpec(self):
    image_column = hub.image_embedding_column("image", self.spec)
    parsing_spec = tf.feature_column.make_parse_example_spec([image_column])
    self.assertEqual(parsing_spec, {
        "image": tf.FixedLenFeature([1, 2, 3], dtype=tf.float32)
    })

  def testInputLayer(self):
    features = {
        "image_a": [[[[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]],
                    [[[0.7, 0.7, 0.7], [0.1, 0.2, 0.3]]]],
        "image_b": [[[[0.1, 0.2, 0.1], [0.2, 0.1, 0.2]]],
                    [[[0.1, 0.2, 0.3], [0.3, 0.2, 0.1]]]],
    }
    feature_columns = [
        hub.image_embedding_column("image_a", self.spec),
        hub.image_embedding_column("image_b", self.spec),
    ]
    with tf.Graph().as_default():
      input_layer = tf.feature_column.input_layer(features, feature_columns)
      with tf.train.MonitoredSession() as sess:
        output = sess.run(input_layer)
        self.assertAllClose(output, [[0.5, 0.7, 0.9, 0.3, 0.3, 0.3],
                                     [0.8, 0.9, 1.0, 0.4, 0.4, 0.4]])

  def testWorksWithCannedEstimator(self):
    image_column = hub.image_embedding_column("image", self.spec)
    other_column = tf.feature_column.numeric_column("number")

    feature_columns = [image_column, other_column]
    estimator = tf.estimator.DNNClassifier(
        hidden_units=[10],
        feature_columns=feature_columns,
        model_dir=self.get_temp_dir())

    # This only tests that estimator apis are working with the feature
    # column without throwing exceptions.
    features = {
        "image": np.array(
            [[[[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]],
             [[[0.7, 0.7, 0.7], [0.1, 0.2, 0.3]]]], dtype=np.float32),
        "number": np.array([[20], [1]]),
    }
    labels = np.array([[1], [0]])
    input_fn = tf.estimator.inputs.numpy_input_fn(features, labels,
                                                  shuffle=True)
    estimator.train(input_fn, max_steps=1)
    estimator.evaluate(input_fn, steps=1)
    estimator.predict(input_fn)


if __name__ == "__main__":
  tf.test.main()
