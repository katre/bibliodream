CREATE TABLE book (
  id TEXT PRIMARY KEY NOT NULL,
  author TEXT NOT NULL,
  title TEXT NOT NULL,
  bookshelf TEXT
);

CREATE TABLE url (
  book_id TEXT NOT NULL,
  url TEXT NOT NULL,
  FOREIGN KEY(book_id) REFERENCES book(id)
);

