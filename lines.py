#! /usr/bin/env python

"""Stitch together a book from random lines."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import random
import re

from tensorflow.python.platform import flags
from tensorflow.python.platform import gfile

import gutenberg

FLAGS = flags.FLAGS

flags.DEFINE_integer('word_count', 100, 'Target word count for the output.')
flags.DEFINE_integer('book_count', 10, 'Number of books to use.')
flags.DEFINE_string('output', 'book.txt', 'Filename to write to.')

# Functions to get books and lines.
def get_random_book(books):
  return random.choice(books)

END_PUNCTUATION = re.compile(r'[.?!]')

def get_random_line(book):
  # Split text on ending punctuation
  lines = END_PUNCTUATION.split(book.data)
  line = random.choice(lines) + '.'
  # Remove any newlines.
  return line.replace('\n', '')

def count_words(line):
  words = line.split()
  return len(words)

def main(argv=None):
  data = gutenberg.GutenbergData(0, FLAGS.book_count, random=True)

  # Find the books.
  books = data.books

  print('Found %d books' % len(books))

  total_words = 0
  with open(FLAGS.output, 'w') as f:
    while total_words < FLAGS.word_count:
      # Pick a random line from a random book.
      book = get_random_book(books)
      line = get_random_line(book)

      # Count the words.
      new_words = count_words(line)
      total_words += new_words

      # Write the line.
      f.write(line)


if __name__ == '__main__':
  from tensorflow.python.platform import app
  app.run()

