"""Functions for downloading and reading Gutenberg books."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import sqlite3

from tensorflow.python.platform import flags

FLAGS = flags.FLAGS

flags.DEFINE_string('gutenberg_db', './db/bibliodream.db',
                    """Location of the SQLite DB with book data.""")
flags.DEFINE_string('bookshelf', 'Science Fiction',
                    """The Gutenberg Bookshelf to train on.""")
flags.DEFINE_integer('book_count', 10,
                     """The number of books to fetch for each dataset.""")


def read_data_sets(train_dir):
  con = sqlite3.connect(FLAGS.gutenberg_db)
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
    print('Row id %s, url %s' % (row['id'], row['url']))

def load_gutenberg(train_dir='GUTENBERG_data'):
  return read_data_sets(train_dir)

def main(argv=None):  # pylint: disable=unused-argument
  return load_gutenberg()

if __name__ == '__main__':
  from tensorflow.python.platform import app
  app.run()

