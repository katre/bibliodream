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
flags.DEFINE_integer('subject_count', 10,
                     """The number of subjects to fetch for categorizing.""")
flags.DEFINE_integer('books_count', 10,
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

class Subjects(object):
  def __init__(self):
    self.names = []
    self.next_ordinal = 0
    self.ordinals = {}

  def append(self, name):
    self.names.append(name)
    self.ordinals[name] = self.next_ordinal
    self.next_ordinal += 1

  def one_hot(self, name):
    if name not in self.ordinals:
      return None
    arr = [0.0] * len(self.names)
    arr[self.ordinals[name]] = 1.0
    return arr

  def __str__(self):
    return 'Subjects: [%s]' % ', '.join(self.names)

# The top subjects for english-language books.
SUBJECT_QUERY = """
select
  upper(subject.name) as name,
  count(*) as count
from subject
  join book on subject.book_id = book.id
where
  length(subject.name) > 2
  and book.lang = 'en'
group by upper(subject.name)
order by count desc
limit :limit;
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
  and upper(subject.name) in (%(subject_clause)s)
group by id
order by id
limit :limit;
"""

def lookup_subjects(con, limit):
  print('Looking up %d subjects to categorize on.' % limit)
  subjects = Subjects()
  con.row_factory = sqlite3.Row
  for row in con.execute(SUBJECT_QUERY,
      {
        'limit': limit,
      }):
    subjects.append(row['name'])
  return subjects

def lookup_books(con, limit, subjects):
  print('Looking up %d books to train on.' % limit)
  books = []

  # Create the subject-specific query
  subject_clause = ', '.join(':subject_%d' % i for i in xrange(len(subjects)))
  query = BOOK_QUERY % {'subject_clause': subject_clause}

  # Create the arguments.
  arguments = {}
  for i, subject in enumerate(subjects):
    arguments['subject_%d' % i] = subject
  arguments['limit'] = limit

  # Execute the query
  con.row_factory = sqlite3.Row
  for row in con.execute(query, arguments):
    books.append(Book(row))

  #print('Found %d books!' % len(books))
  return books

def maybe_download_books(dir, books):
  #print('Considering downloading books.')
  for book in books:
    book.maybe_download(dir)

def read_data_sets(data_dir):
  con = sqlite3.connect(FLAGS.gutenberg_db)
  subjects = lookup_subjects(con, FLAGS.subject_count)
  #print('Found %s' % subjects)
  books = lookup_books(con, FLAGS.books_count, subjects.names)
  #print('Found books:\n%s' % '\n'.join(str(book) for book in books))
  maybe_download_books(data_dir, books)

  # Split into train, verify, test sets.
  train_size = int(0.80 * len(books))
  verify_size = int(0.10 * len(books))
  test_size = int(0.10 * len(books))

  train_books = books[0..train_size]
  verify_books = books[train_size+1:train_size+verify_size]
  test_books = books[train_size+verify_size+1:]

  # Create data set for each group

  # return entire dataset

def load_gutenberg(data_dir='GUTENBERG_data'):
  return read_data_sets(data_dir)

def main(argv=None):  # pylint: disable=unused-argument
  return load_gutenberg()

if __name__ == '__main__':
  from tensorflow.python.platform import app
  app.run()

