#! /usr/bin/env python

"""Train the book-category classifier."""

import tensorflow as tf
import numpy as np
import os
import time
import datetime
import re
import itertools
from tensorflow.contrib import learn

# Local things.
import gutenberg
from text_cnn import TextCNN

# Parameters
# ==================================================

# Data loading params
tf.flags.DEFINE_integer('subject_count', 10, 'The number of subjects to use.')
tf.flags.DEFINE_integer('book_limit', 20, 'The max number of books to load.')
tf.flags.DEFINE_float('dev_sample_percentage', .1, 'Percentage of the training data to use for validation')

# Model Hyperparameters
tf.flags.DEFINE_integer('embedding_dim', 128, 'Dimensionality of character embedding (default: 128)')
tf.flags.DEFINE_string('filter_sizes', '3,4,5', 'Comma-separated filter sizes (default: "3,4,5")')
tf.flags.DEFINE_integer('num_filters', 128, 'Number of filters per filter size (default: 128)')
tf.flags.DEFINE_float('dropout_keep_prob', 0.5, 'Dropout keep probability (default: 0.5)')
tf.flags.DEFINE_float('l2_reg_lambda', 0.0, 'L2 regularizaion lambda (default: 0.0)')

# Training parameters
tf.flags.DEFINE_integer('batch_size', 64, 'Batch Size (default: 64)')
tf.flags.DEFINE_integer('num_epochs', 200, 'Number of training epochs (default: 200)')
tf.flags.DEFINE_integer('evaluate_every', 100, 'Evaluate model on dev set after this many steps (default: 100)')
tf.flags.DEFINE_integer('checkpoint_every', 100, 'Save model after this many steps (default: 100)')
# Misc Parameters
tf.flags.DEFINE_boolean('allow_soft_placement', True, 'Allow device soft device placement')
tf.flags.DEFINE_boolean('log_device_placement', False, 'Log placement of ops on devices')

FLAGS = tf.flags.FLAGS

# Data Preparatopn
# ==================================================

def clean_str(string):
  """
  Tokenization/string cleaning for all datasets except for SST.
  Original taken from https://github.com/yoonkim/CNN_sentence/blob/master/process_data.py
  """
  string = re.sub(r'[^A-Za-z0-9(),!?\'\`]', ' ', string)
  string = re.sub(r'\'s', ' \'s', string)
  string = re.sub(r'\'ve', ' \'ve', string)
  string = re.sub(r'n\'t', ' n\'t', string)
  string = re.sub(r'\'re', ' \'re', string)
  string = re.sub(r'\'d', ' \'d', string)
  string = re.sub(r'\'ll', ' \'ll', string)
  string = re.sub(r',', ' , ', string)
  string = re.sub(r'!', ' ! ', string)
  string = re.sub(r'\(', ' \( ', string)
  string = re.sub(r'\)', ' \) ', string)
  string = re.sub(r'\?', ' \? ', string)
  string = re.sub(r'\s{2,}', ' ', string)
  return string.strip().lower()

# Load data
def load_data(data):
  """Load and return correctly labelled training data."""
  x = []
  y = []
  for (text, subject) in data.labelled_data():
    text = clean_str(text)
    x.append(clean_str(text))
    y.append(subject)
  return (np.array(x), np.array(y))


# Build vocabulary
def build_vocab(texts):
  """Build the vocabulary from the input texts."""
  max_document_length = max([len(text.split(' ')) for text in texts])
  vocab_processor = learn.preprocessing.VocabularyProcessor(max_document_length)
  texts = np.array(list(vocab_processor.fit_transform(texts)))
  return (texts, vocab_processor)

# Randomly shuffle data
def shuffle_data(x, y):
  np.random.seed(10)
  np.random.shuffle(x)
  np.random.shuffle(y)

# Split train/test set
def split_data(x, y):
  # TODO: This is very crude, should use cross-validation
  dev_sample_index = -1 * int(FLAGS.dev_sample_percentage * float(len(y)))
  x_train, x_dev = x[:dev_sample_index], x[dev_sample_index:]
  y_train, y_dev = y[:dev_sample_index], y[dev_sample_index:]
  return ((x_train, y_train), (x_dev, y_dev))


# Training
# ==================================================

def find_output_dir():
  timestamp = str(int(time.time()))
  out_dir = os.path.abspath(os.path.join(os.path.curdir, 'runs', timestamp))
  os.makedirs(out_dir)
  return out_dir

def train(x_train, y_train, x_dev, y_dev, vocab_processor, out_dir):
  with tf.Graph().as_default():
    session_conf = tf.ConfigProto(
        allow_soft_placement=FLAGS.allow_soft_placement,
        log_device_placement=FLAGS.log_device_placement)
    sess = tf.Session(config=session_conf)
    with sess.as_default():
      cnn = TextCNN(
          sequence_length=x_train.shape[1],
          num_classes=y_train.shape[1],
          vocab_size=len(vocab_processor.vocabulary_),
          embedding_size=FLAGS.embedding_dim,
          filter_sizes=list(map(int, FLAGS.filter_sizes.split(','))),
          num_filters=FLAGS.num_filters,
          l2_reg_lambda=FLAGS.l2_reg_lambda)

      # Define Training procedure
      global_step = tf.Variable(0, name='global_step', trainable=False)
      optimizer = tf.train.AdamOptimizer(1e-3)
      grads_and_vars = optimizer.compute_gradients(cnn.loss)
      train_op = optimizer.apply_gradients(grads_and_vars, global_step=global_step)

      # Keep track of gradient values and sparsity (optional)
      grad_summaries = []
      for g, v in grads_and_vars:
        if g is not None:
          grad_hist_summary = tf.histogram_summary('{}/grad/hist'.format(v.name), g)
          sparsity_summary = tf.scalar_summary('{}/grad/sparsity'.format(v.name), tf.nn.zero_fraction(g))
          grad_summaries.append(grad_hist_summary)
          grad_summaries.append(sparsity_summary)
      grad_summaries_merged = tf.merge_summary(grad_summaries)

      # Output directory for models and summaries
      print('Writing to {}\n'.format(out_dir))

      # Summaries for loss and accuracy
      loss_summary = tf.scalar_summary('loss', cnn.loss)
      acc_summary = tf.scalar_summary('accuracy', cnn.accuracy)

      # Train Summaries
      train_summary_op = tf.merge_summary([loss_summary, acc_summary, grad_summaries_merged])
      train_summary_dir = os.path.join(out_dir, 'summaries', 'train')
      train_summary_writer = tf.train.SummaryWriter(train_summary_dir, sess.graph)

      # Dev summaries
      dev_summary_op = tf.merge_summary([loss_summary, acc_summary])
      dev_summary_dir = os.path.join(out_dir, 'summaries', 'dev')
      dev_summary_writer = tf.train.SummaryWriter(dev_summary_dir, sess.graph)

      # Checkpoint directory. Tensorflow assumes this directory already exists so we need to create it
      checkpoint_dir = os.path.abspath(os.path.join(out_dir, 'checkpoints'))
      checkpoint_prefix = os.path.join(checkpoint_dir, 'model')
      if not os.path.exists(checkpoint_dir):
        os.makedirs(checkpoint_dir)
      saver = tf.train.Saver(tf.all_variables())

      # Initialize all variables
      sess.run(tf.initialize_all_variables())

      def train_step(x_batch, y_batch):
        """
        A single training step
        """
        feed_dict = {
            cnn.input_x: x_batch,
            cnn.input_y: y_batch,
            cnn.dropout_keep_prob: FLAGS.dropout_keep_prob
        }
        _, step, summaries, loss, accuracy = sess.run(
            [train_op, global_step, train_summary_op, cnn.loss, cnn.accuracy],
            feed_dict)
        time_str = datetime.datetime.now().isoformat()
        print('{}: step {}, loss {:g}, acc {:g}'.format(time_str, step, loss, accuracy))
        train_summary_writer.add_summary(summaries, step)

      def dev_step(x_batch, y_batch, writer=None):
        """
        Evaluates model on a dev set
        """
        feed_dict = {
            cnn.input_x: x_batch,
            cnn.input_y: y_batch,
            cnn.dropout_keep_prob: 1.0
        }
        step, summaries, loss, accuracy = sess.run(
            [global_step, dev_summary_op, cnn.loss, cnn.accuracy],
            feed_dict)
        time_str = datetime.datetime.now().isoformat()
        print('{}: step {}, loss {:g}, acc {:g}'.format(time_str, step, loss, accuracy))
        if writer:
          writer.add_summary(summaries, step)

      # Generate batches
      batches = batch_iter(
          list(zip(x_train, y_train)), FLAGS.batch_size, FLAGS.num_epochs)
      # Training loop. For each batch...
      for batch in batches:
        x_batch, y_batch = zip(*batch)
        train_step(x_batch, y_batch)
        current_step = tf.train.global_step(sess, global_step)
        if current_step % FLAGS.evaluate_every == 0:
          print('\nEvaluation:')
          dev_step(x_dev, y_dev, writer=dev_summary_writer)
          print('')
        if current_step % FLAGS.checkpoint_every == 0:
          path = saver.save(sess, checkpoint_prefix, global_step=current_step)
          print('Saved model checkpoint to {}\n'.format(path))

def batch_iter(data, batch_size, num_epochs, shuffle=True):
  """
  Generates a batch iterator for a dataset.
  """
  data = np.array(data)
  data_size = len(data)
  num_batches_per_epoch = int(len(data)/batch_size) + 1
  for epoch in range(num_epochs):
    # Shuffle the data at each epoch
    if shuffle:
      shuffle_indices = np.random.permutation(np.arange(data_size))
      shuffled_data = data[shuffle_indices]
    else:
      shuffled_data = data
    for batch_num in range(num_batches_per_epoch):
      start_index = batch_num * batch_size
      end_index = min((batch_num + 1) * batch_size, data_size)
      yield shuffled_data[start_index:end_index]

# Main run function.
def main(argv=None):
  print('\nParameters:')
  for attr, value in sorted(FLAGS.__flags.items()):
    print('{}={}'.format(attr.upper(), value))
  print('')

  # Train on the data.
  print('Loading data...')
  gutenberg_data = gutenberg.GutenbergData(FLAGS.subject_count, FLAGS.book_limit)
  x, y = load_data(gutenberg_data)
  #for i in xrange(len(x)):
  #  print('Text: %s' % x[i][:100])
  #  print('Subject: %s' % y[i])
  #return

  print('Extracting vocabulary...')
  x, vocab_processor = build_vocab(x)
  #for i in xrange(len(x)):
  #  print('Text: %s' % x[i][:100])
  #return

  print('Shuffling data...')
  shuffle_data(x, y)
  #for i in xrange(len(x)):
  #  print('Text: %s' % x[i][:100])
  #  print('Subject: %s' % y[i])
  #return

  print('Splitting data...')
  ((x_train, y_train), (x_dev, y_dev)) = split_data(x, y)

  # Summarize data.
  print('Vocabulary Size: {:d}'.format(len(vocab_processor.vocabulary_)))
  print('Train/Dev split: {:d}/{:d}'.format(len(y_train), len(y_dev)))

  # Write vocabulary
  out_dir = find_output_dir()
  vocab_processor.save(os.path.join(out_dir, 'vocab'))

  # Write subjects data
  gutenberg_data.subjects.save(os.path.join(out_dir, 'subjects'))

  print('Training...')
  train(x_train, y_train, x_dev, y_dev, vocab_processor, out_dir)


if __name__ == '__main__':
  from tensorflow.python.platform import app
  app.run()

