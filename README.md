# Bibliophile's Dream

[National Novel Generation Month](https://github.com/NaNoGenMo/2016) has kicked
off, and this year I'm going to take a stab. I originally wanted to first train a neural net on Gutenberg book data, then run it backwards (a la Google's [Deep Dream](https://github.com/google/deepdream)) to see what came out, but it turns out that training neural nets is hard.

Instead, I took my Gutenberg book data, grabbed a random selection of 1000 of them, and started grabbing random sentences from those books until I had 50,000 words.

## Step 0: Project Setup

1. Download the [Gutenberg feed in RDF format](https://www.gutenberg.org/wiki/Gutenberg:Feeds).
2. Then import that into a Sqlite database with the db/init.sh script.
3. Rsync a copy of just the text files from Gutenberg.
```
$ rsync -av --del --include='*.txt*' --exclude='*' ftp@ftp.ibiblio.org::gutenberg gutenberg/
```
4. Import the file table to the database with db/load_books.sh.

## Step 1: Run the script

```
$ ./lines.py --book_count=1000 --word_count=50000
```

This ran for 3m25s on my laptop.

