""" 
This is from the Tensorflow tutorial, but I'm adding regularization.

ALTERNATIVE REGULARIZATION, and it's actually easier I think.

Results with regularization terms:

0.0     0.9481 (compared with 0.9468 from earlier code)
0.0001  0.9502 (compared with 0.9476 from earlier code) 
0.01    0.9191 (compared with 0.9183 from earlier code)
1.0     0.1135 (compared with 0.1135 from earlier code)

Huh, so all in all it's basically the same. I strongly believe this is easier
than the other way, so let me convert my code to this method.
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import argparse
import sys
from tensorflow.examples.tutorials.mnist import input_data
import tensorflow as tf
import tensorflow.contrib.layers as layers
import numpy as np
FLAGS = None


def easier_network(x):
    """ A network based on tf.contrib.learn, with input `x`. NO regularization
    goes here, we do that elsewhere. """
    with tf.variable_scope('EasyNet'):
        out = layers.flatten(x)
        out = layers.fully_connected(out, 
                num_outputs=200,
                weights_initializer = layers.xavier_initializer(uniform=True),
                activation_fn = tf.nn.tanh)
        out = layers.fully_connected(out, 
                num_outputs=200,
                weights_initializer = layers.xavier_initializer(uniform=True),
                activation_fn = tf.nn.tanh)
        out = layers.fully_connected(out, 
                num_outputs=10, # Because there are ten digits!
                weights_initializer = layers.xavier_initializer(uniform=True),
                activation_fn = None)
        return out


def main(_):
    mnist = input_data.read_data_sets(FLAGS.data_dir, one_hot=True)
    x = tf.placeholder(tf.float32, [None, 784])
    y_ = tf.placeholder(tf.float32, [None, 10])

    # Make a network with regularization
    y_conv = easier_network(x)
    weights = tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, 'EasyNet') 
    print("")
    for w in weights:
        shp = w.get_shape().as_list()
        print("- {} shape:{} size:{}".format(w.name, shp, np.prod(shp)))
    print("")
    test_list = [v for v in weights if 'bias' not in v.name]
    for item in test_list:
        print(item)
    print("")
    lossL2 = tf.add_n([tf.nn.l2_loss(v) for v in weights if 'bias' not in v.name]) * FLAGS.regu

    # Make the loss function `loss_fn` with regularization.
    cross_entropy = tf.reduce_mean(
        tf.nn.softmax_cross_entropy_with_logits(labels=y_, logits=y_conv))
    loss_fn = cross_entropy + lossL2
    train_step = tf.train.AdamOptimizer(1e-4).minimize(loss_fn)
    correct_prediction = tf.equal(tf.argmax(y_conv, 1), tf.argmax(y_, 1))
    accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))

    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())
        # Training
        for i in range(5000):
            batch = mnist.train.next_batch(50)
            feed = {x: batch[0], y_: batch[1]}
            if i % 50 == 0:
                train_accuracy = accuracy.eval(feed_dict=feed)
                print('step %d, training accuracy %g' % (i, train_accuracy))
            train_step.run(feed_dict = feed)
        # Testing
        print('test accuracy %g' % accuracy.eval(feed_dict={
            x: mnist.test.images, y_: mnist.test.labels}))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_dir', type=str,
                        default='/tmp/tensorflow/mnist/input_data',
                        help='Directory for storing input data')
    parser.add_argument('--regu', type=float, default=0.0)
    FLAGS, unparsed = parser.parse_known_args()
    tf.app.run(main=main, argv=[sys.argv[0]] + unparsed)
