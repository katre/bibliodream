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
flags.DEFINE_integer('training_count', 10,
                     """The number of books to fetch for training.""")


class Book(object):
  def __init__(self, row):
    self.id = row['id']
    self.url = row['url']
    self.subjects = row['subjects'].split('||')
    self.filename = self.id.replace('/', '_') + '.txt'

  def maybe_download(self, dir):
    #print('Maybe downloading %s' % self)
    base.maybe_download(self.filename, dir, self.url) 

  def __str__(self):
    return 'Book %s' % self.id

# The top 50 subjects.
SUBJECT_QUERY = """
select
  upper(subject.name) as name
from
  book
  join subject on book.id = subject.book_id
group by name
order by count desc
limit 50;
"""

BOOK_QUERY = """
select
  book.id as id,
  url.url as url,
  group_concat(upper(subject.name),'||') as subjects
from book
  join url on book.id = url.book_id
  join subject on book.id = subject.book_id
where
  url.is_utf8 = 'TRUE'
group by id
order by id
limit :limit;
"""

def lookup_books(con, limit):
  print('Looking up %d books to train on.' % limit)
  books = []
  con.row_factory = sqlite3.Row
  for row in con.execute(BOOK_QUERY,
      {
        'limit': limit
      }):
    books.append(Book(row))
  #print('Found %d books!' % len(books))
  return books

def maybe_download_books(dir, books):
  #print('Considering downloading books.')
  for book in books:
    book.maybe_download(dir)

def read_data_sets(data_dir):
  con = sqlite3.connect(FLAGS.gutenberg_db)
  books = lookup_books(con, FLAGS.training_count)
  maybe_download_books(data_dir, books)

def load_gutenberg(data_dir='GUTENBERG_data'):
  return read_data_sets(data_dir)

def main(argv=None):  # pylint: disable=unused-argument
  return load_gutenberg()

if __name__ == '__main__':
  from tensorflow.python.platform import app
  app.run()

