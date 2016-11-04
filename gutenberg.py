"""Functions for downloading and reading Gutenberg books."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import sqlite3

from tensorflow.contrib.learn.python.learn.datasets import base
from tensorflow.python.platform import flags

FLAGS = flags.FLAGS

flags.DEFINE_string('gutenberg_db', './db/bibliodream.db',
                    """Location of the SQLite DB with book data.""")
flags.DEFINE_string('bookshelf', 'Science Fiction',
                    """The Gutenberg Bookshelf to train on.""")
flags.DEFINE_integer('book_count', 10,
                     """The number of books to fetch for each dataset.""")


class Book(object):
  def __init__(self, row):
    self.id = row['id']
    self.url = row['url']
    self.filename = self.id.replace('/', '_') + '.txt'

  def maybe_download(self, dir):
    base.maybe_download(self.filename, dir, self.url) 

  def __str__(self):
    return 'Book %s' % self.id

def get_books(con, bookshelf, limit):
  books = []
  con.row_factory = sqlite3.Row
  for row in con.execute('''
      select book.id as id, url.url as url
      from book
        join url on book.id = url.book_id
      where book.bookshelf = :bookshelf
        and url.url like '%.txt.utf-8'
      order by id
      limit :limit;''', {
        'bookshelf': FLAGS.bookshelf,
        'limit': FLAGS.book_count
      }):
    books.append(Book(row))
  return books

def maybe_download_books(dir, books):
  for book in books:
    book.maybe_download(dir)

def read_data_sets(train_dir):
  con = sqlite3.connect(FLAGS.gutenberg_db)
  training_books = get_books(con, FLAGS.bookshelf, FLAGS.book_count)
  maybe_download_books(train_dir, training_books)

def load_gutenberg(train_dir='GUTENBERG_data'):
  return read_data_sets(train_dir)

def main(argv=None):  # pylint: disable=unused-argument
  return load_gutenberg()

if __name__ == '__main__':
  from tensorflow.python.platform import app
  app.run()

