<?xml version="1.0"?>

<xsl:stylesheet version="1.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:pgterms="http://www.gutenberg.org/2009/pgterms/"
    xmlns:dcterms="http://purl.org/dc/terms/"
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    >
  <xsl:output method="text"/>
  <xsl:template match="/rdf:RDF">
BEGIN TRANSACTION;

INSERT INTO book VALUES (
  '<xsl:call-template name="escapeQuotes"><xsl:with-param name="txt" select="//pgterms:ebook/@rdf:about"/></xsl:call-template>', -- id
  '<xsl:call-template name="escapeQuotes"><xsl:with-param name="txt" select="//pgterms:name"/></xsl:call-template>', -- author
  '<xsl:call-template name="escapeQuotes"><xsl:with-param name="txt" select="//dcterms:title"/></xsl:call-template>', -- title
  '<xsl:call-template name="escapeQuotes"><xsl:with-param name="txt" select="//dcterms:language//rdf:value"/></xsl:call-template>' -- lang
);
<xsl:for-each select="//pgterms:file">
  <xsl:call-template name="url">
    <xsl:with-param name="book_id" select="//pgterms:ebook/@rdf:about"/>
    <xsl:with-param name="file" select="."/>
  </xsl:call-template>
</xsl:for-each>

<xsl:call-template name="subject">
  <xsl:with-param name="book_id" select="//pgterms:ebook/@rdf:about"/>
  <xsl:with-param name="name" select="//pgterms:bookshelf"/>
</xsl:call-template>
<xsl:for-each select="//dcterms:subject/rdf:Description/rdf:value">
  <xsl:call-template name="subject">
    <xsl:with-param name="book_id" select="//pgterms:ebook/@rdf:about"/>
    <xsl:with-param name="name" select="."/>
  </xsl:call-template>
</xsl:for-each>

COMMIT TRANSACTION;
  </xsl:template>

  <xsl:template name="url">
    <xsl:param name="book_id"/>
    <xsl:param name="file"/>

    <xsl:variable name="name" select="@rdf:about"/>
    <xsl:variable name="type" select="dcterms:format//rdf:value"/>
    <xsl:if test="contains($type, 'text/plain') and contains($name, '.txt')">
INSERT INTO url VALUES (
  '<xsl:call-template name="escapeQuotes"><xsl:with-param name="txt" select="$book_id"/></xsl:call-template>', -- id
  '<xsl:call-template name="escapeQuotes"><xsl:with-param name="txt" select="$name"/></xsl:call-template>', -- url
  '<xsl:call-template name="escapeQuotes"><xsl:with-param name="txt" select="$type"/></xsl:call-template>', -- content type
  <xsl:choose>
    <xsl:when test="contains($type, 'utf-8') or contains($name, 'utf-8')">
  'TRUE'
    </xsl:when>
    <xsl:otherwise>
  'FALSE'
    </xsl:otherwise>
  </xsl:choose>
);
    </xsl:if>
  </xsl:template>

  <xsl:template name="subject">
    <xsl:param name="book_id"/>
    <xsl:param name="name"/>
    
<xsl:if test="normalize-space($name) != ''">
INSERT INTO subject VALUES (
  '<xsl:call-template name="escapeQuotes"><xsl:with-param name="txt" select="$book_id"/></xsl:call-template>', -- book_id
  '<xsl:call-template name="escapeQuotes"><xsl:with-param name="txt" select="normalize-space($name)"/></xsl:call-template>' -- name
);
</xsl:if>

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

