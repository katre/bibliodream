#!/bin/bash

BOOK_DIR="$1"
if [ -z "$BOOK_DIR" ]; then
  echo "usage: load_books.sh gutenberg_dir"
  exit 1
fi

echo "Loading books from $BOOK_DIR" >&2

for path in $(find $BOOK_DIR -name '*.txt' | grep -v old); do
  id=`echo $path | perl -p -e 's/.*\/(\d+)(-\d)?.txt$/\1/'`

  book_id="ebooks/$id"
  is_utf='FALSE'

  if [[ "$path" =~ ^.*-0.txt$ ]]; then
    is_utf='TRUE'
  fi

  echo "INSERT INTO file (book_id, path, is_utf8) VALUES"
  echo "  ('$book_id', '$path', '$is_utf');"
done

