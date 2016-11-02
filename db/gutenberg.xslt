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
  '<xsl:call-template name="escapeQuotes"><xsl:with-param name="txt" select="//pgterms:ebook/@rdf:about"/></xsl:call-template>', -- id
  '<xsl:call-template name="escapeQuotes"><xsl:with-param name="txt" select="//pgterms:name"/></xsl:call-template>', -- author
  '<xsl:call-template name="escapeQuotes"><xsl:with-param name="txt" select="//dcterms:title"/></xsl:call-template>', -- title
  '<xsl:call-template name="escapeQuotes"><xsl:with-param name="txt" select="normalize-space(//pgterms:bookshelf)"/></xsl:call-template>' -- bookshelf
);
<xsl:for-each select="//pgterms:file[contains(@rdf:about, '.txt')]">
INSERT INTO url VALUES (
  '<xsl:call-template name="escapeQuotes"><xsl:with-param name="txt" select="//pgterms:ebook/@rdf:about"/></xsl:call-template>', -- id
  '<xsl:call-template name="escapeQuotes"><xsl:with-param name="txt" select="@rdf:about"/></xsl:call-template>' -- url
);
</xsl:for-each>
  </xsl:template>
  <xsl:template name="escapeQuotes">
        <xsl:param name="txt"/>
        <!-- Escape with slash -->
        <!-- <xsl:variable name="backSlashQuote">&#92;&#39;</xsl:variable> -->
        <!-- MsSql escape -->
        <xsl:variable name="backSlashQuote">&#39;&#39;</xsl:variable>
        <xsl:variable name="singleQuote">&#39;</xsl:variable>

        <xsl:choose>
            <xsl:when test="string-length($txt) = 0">
                <!-- ... -->
            </xsl:when>

            <xsl:when test="contains($txt, $singleQuote)">
                <xsl:value-of disable-output-escaping="yes" select="concat(substring-before($txt, $singleQuote), $backSlashQuote)"/>

                <xsl:call-template name="escapeQuotes">
                    <xsl:with-param name="txt" select="substring-after($txt, $singleQuote)"/>
                </xsl:call-template>
            </xsl:when>

            <xsl:otherwise>
                <xsl:value-of disable-output-escaping="yes" select="$txt"/>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>
</xsl:stylesheet>

