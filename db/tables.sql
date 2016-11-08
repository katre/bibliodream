CREATE TABLE book (
  id TEXT PRIMARY KEY NOT NULL,
  author TEXT,
  title TEXT,
  lang TEXT
);

CREATE TABLE url (
  book_id TEXT NOT NULL,
  url TEXT NOT NULL,
  FOREIGN KEY(book_id) REFERENCES book(id)
);

CREATE TABLE subject (
  book_id TEXT NOT NULL,
  name TEXT NOT NULL,
  FOREIGN KEY(book_id) REFERENCES book(id)
);
