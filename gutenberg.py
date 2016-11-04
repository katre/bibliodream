"""Functions for downloading and reading Gutenberg books."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from tensorflow.python.platform import app
from tensorflow.python.platform import flags

FLAGS = flags.FLAGS

flags.DEFINE_string('gutenberg_db', './db/bibliodream.db',
                    """Location of the SQLite DB with book data.""")



def read_data_sets(train_dir):
  pass

def load_gutenberg(train_dir='GUTENBERG_data'):
  return read_data_sets(train_dir)

def main(argv=None):  # pylint: disable=unused-argument
  return load_gutenberg()

if __name__ == '__main__':
  app.run()

