RDF_DIR=/home/katre/Downloads/cache/epub/
DB_NAME=bibliodream.db

pushd db
rm $DB_NAME
sqlite3 $DB_NAME < tables.sql
find $RDF_DIR -name '*.rdf' | \
  xargs xsltproc gutenberg.xslt | \
  sqlite3 $DB_NAME

