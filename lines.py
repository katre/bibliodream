#! /usr/bin/env python

"""Stitch together a book from random lines."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from tensorflow.python.platform import flags
from tensorflow.python.platform import gfile

FLAGS = flags.FLAGS

flags.DEFINE_integer('word_count', 100, 'Target word count for the output.')
flags.DEFINE_integer('book_count', 10, 'Number of books to use.')
flags.DEFINE_string('output', 'book.txt', 'Filename to write to.')

# Functions to get books and lines.

def main(argv=None):
  with open(FLAGS.output) as f:
    pass

if __name__ == '__main__':
  from tensorflow.python.platform import app
  app.run()
