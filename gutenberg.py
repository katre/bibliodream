#! /usr/bin/env python

"""Functions for downloading and reading Gutenberg books."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import sqlite3

from tensorflow.contrib.learn.python.learn.datasets import base
from tensorflow.python.platform import flags

FLAGS = flags.FLAGS

flags.DEFINE_string('gutenberg_data', './gutenberg_data',
                    """Location of Gutenberg books.""")
flags.DEFINE_string('gutenberg_db', './db/bibliodream.db',
                    """Location of the SQLite DB with book data.""")


# Queries to use against the DB.

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
  file.path as path,
  group_concat(upper(subject.name),'||') as subjects
from book
  join file on book.id = file.book_id
  join subject on book.id = subject.book_id
where
  file.is_utf8 = 'TRUE'
  and upper(subject.name) in (%(subject_clause)s)
group by id
order by id
limit :limit;
"""

# Books data.

def lookup_books(conn, limit, subjects):
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
  for row in conn.execute(query, arguments):
    books.append(Book(row))

  #print('Found %d books!' % len(books))
  #print('Found books:\n%s' % '\n'.join(str(book) for book in books))
  return books

class Book(object):
  def __init__(self, row):
    self.id = row['id']
    self.path = row['path']
    self.subjects = row['subjects'].split('||')

  @property
  def data(self):
    with open(self.path, 'r') as f:
      return f.read()

  def __str__(self):
    return 'Book %s' % self.id

# Subjects data.

def lookup_subjects(conn, limit):
  print('Looking up %d subjects to categorize on.' % limit)
  subjects = Subjects()
  for row in conn.execute(SUBJECT_QUERY,
      {
        'limit': limit,
      }):
    subjects.append(row['name'])
  #print('Found %s' % subjects)
  return subjects

class Subjects(object):
  def __init__(self):
    self.names = []
    self.next_ordinal = 0
    self.ordinals = {}

  def append(self, name):
    self.names.append(name)
    self.ordinals[name] = self.next_ordinal
    self.next_ordinal += 1

  def one_hot(self, targets):
    arr = [0.0] * len(self.names)
    for target in targets:
      if target in self.ordinals:
        arr[self.ordinals[target]] = 1.0
    return arr

  def __str__(self):
    return 'Subjects: [%s]' % ', '.join(self.names)

# Overall main class.
class GutenbergData(object):
  def __init__(self, subjects_limit, book_limit):
    self.subjects_limit = subjects_limit
    self.book_limit = book_limit

    self.subjects = None
    self.books = None

    # Open the DB eagerly.
    self.conn = sqlite3.connect(FLAGS.gutenberg_db)
    self.conn.row_factory = sqlite3.Row

  @property
  def subjects(self)
    if not self.subjects:
      self.subjects = lookup_subjects(self.conn, self.subjects_limit)
    return self.subjects

  @property
  def books(self):
    if not self.books:
      self.books = lookup_books(self.conn, self.books_limit, self.subjects)
    return self.books

  def labelled_data(self):
    for book in self.books:
      book_text = book.data
      subject_one_hot = self.subjects.one_hot(book.subjects)
      yield (book_text, subject_one_hot)
    
def main(argv=None):  # pylint: disable=unused-argument
  gutenberg = Gutenberg(10, 20)
  for (text, subject) in gutenberg.labelled_data():
    print('Text: %s' % text[:100])
    print('Subject: %s' % subject)

if __name__ == '__main__':
  from tensorflow.python.platform import app
  app.run()

