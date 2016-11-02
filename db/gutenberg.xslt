<?xml version="1.0"?>

<xsl:stylesheet version="1.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:pgterms="http://www.gutenberg.org/2009/pgterms/"
    xmlns:dcterms="http://purl.org/dc/terms/"
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    >
  <xsl:output method="text"/>
  <xsl:template match="/rdf:RDF">
INSERT INTO book VALUES (
  '<xsl:value-of select="//pgterms:ebook/@rdf:about"/>', -- id
  '<xsl:value-of select="//pgterms:name"/>', -- author
  '<xsl:value-of select="//dcterms:title"/>', -- title
  '<xsl:value-of select="normalize-space(//pgterms:bookshelf)"/>' -- bookshelf
);
<xsl:for-each select="//pgterms:file[contains(@rdf:about, '.txt')]">
INSERT INTO url VALUES (
  '<xsl:value-of select="//pgterms:ebook/@rdf:about"/>', -- id
  '<xsl:value-of select="@rdf:about"/>' -- url
);
</xsl:for-each>
  </xsl:template>
</xsl:stylesheet>

