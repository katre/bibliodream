CREATE TABLE book (
  id TEXT PRIMARY KEY NOT NULL,
  author TEXT,
  title TEXT,
  lang TEXT
);

CREATE TABLE file (
  book_id TEXT NOT NULL,
  path TEXT NOT NULL,
  is_utf8 BOOLEAN,
  FOREIGN KEY(book_id) REFERENCES book(id)
);

CREATE TABLE url (
  book_id TEXT NOT NULL,
  url TEXT NOT NULL,
  content_type TEXT,
  is_utf8 BOOLEAN,
  FOREIGN KEY(book_id) REFERENCES book(id)
);

CREATE TABLE subject (
  book_id TEXT NOT NULL,
  name TEXT NOT NULL,
  FOREIGN KEY(book_id) REFERENCES book(id)
);

CREATE INDEX subject_book_idx
ON subject(book_id);

