[TOC]

# Query wikidata with SPARQL #

Wikidata has its own SPARQL endpoint. SPARQL queries can be submitted from any at http://wdqs-beta.wmflabs.org/, or its direct url (http://wdqs-beta.wmflabs.org/bigdata/namespace/wdq/sparql). The latter URL allows integrating Wikidata items with external SPARQL endpoints through [federated queries](http://www.w3.org/TR/sparql11-federated-query/) or to integrate in data analysis packages such as [R](http://www.r-bloggers.com/sparql-with-r-in-less-than-5-minutes/) or any other platform with a SPARQL plugin such as frameworks such as from a external federated query of a framework which includes a SPARQL plugin such as [Text mate with its turtle bundle](https://github.com/peta/turtle.tmbundle). 

### What is this repository for? ###
This repository collects example queries to the SPARQL endpoint of Wikidata. 


## Examples ##
### Get all Wikidata  items with a Disease Ontology ID ###
~~~sparql
PREFIX wd: <http://www.wikidata.org/entity/> 
PREFIX wdt: <http://www.wikidata.org/prop/direct/>

SELECT * WHERE {
   ?diseases wdt:P699 ?doid .
}
~~~
[Execute](http://wdqs-beta.wmflabs.org/#PREFIX%20wd%3A%20%3Chttp%3A%2F%2Fwww.wikidata.org%2Fentity%2F%3E%20%0APREFIX%20wdt%3A%20%3Chttp%3A%2F%2Fwww.wikidata.org%2Fprop%2Fdirect%2F%3E%0A%0ASELECT%20*%20WHERE%20%7B%0A%20%20%20%3Fdiseases%20wdt%3AP699%20%3Fdoid%20.%0A%7D)

### Count the number of Genes in Wikidata grouped by species ###
~~~sparql
PREFIX wd: <http://www.wikidata.org/entity/> 
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?species (count(distinct ?gene) as ?noItems)  WHERE {
   ?gene wdt:P351 ?entrezID . # P351 Entrez Gene ID
   ?gene wdt:P703 ?species . # P703 Found in taxon
 }
 GROUP BY ?species
~~~
[Execute](https://wdqs-beta.wmflabs.org/#PREFIX%20wd%3A%20%3Chttp%3A%2F%2Fwww.wikidata.org%2Fentity%2F%3E%20%0APREFIX%20wdt%3A%20%3Chttp%3A%2F%2Fwww.wikidata.org%2Fprop%2Fdirect%2F%3E%0APREFIX%20rdfs%3A%20%3Chttp%3A%2F%2Fwww.w3.org%2F2000%2F01%2Frdf-schema%23%3E%0A%0ASELECT%20%3Fspecies%20(count(distinct%20%3Fgene)%20as%20%3FnoItems)%20%20WHERE%20%7B%0A%20%20%20%3Fgene%20wdt%3AP351%20%3FentrezID%20.%20%23%20P351%20Entrez%20Gene%20ID%0A%20%20%20%3Fgene%20wdt%3AP703%20%3Fspecies%20.%20%23%20P703%20Found%20in%20taxon%0A%20%7D%0A%20GROUP%20BY%20%3Fspecies)

### Federated queries ###
#### Uniprot ####
The following query is submitted through Uniprot's SPARQL endpoint 
~~~sparql
PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX p: <http://www.wikidata.org/prop/>
PREFIX v: <http://www.wikidata.org/prop/statement/>
PREFIX up:<http://purl.uniprot.org/core/> 
PREFIX database:<http://purl.uniprot.org/database/>

SELECT DISTINCT ?wd_url ?uniprot ?proteinLabel (group_concat(distinct ?pfam ;separator="; ") as ?pfam_id) 
   (group_concat(distinct ?pdb; separator="; ") as ?pdbId)
   (group_concat(distinct ?refseq; separator="; ") as ?RefSeq_Id)
   (group_concat(distinct ?goid; separator="; ") as ?upGoid)
WHERE {
SERVICE <http://wdqs-beta.wmflabs.org/bigdata/namespace/wdq/sparql>{
   ?wd_url wdt:P279 wd:Q8054 .
   ?wd_url rdfs:label ?proteinLabel .
   ?wd_url wdt:P352 ?wduniprot .
   FILTER(lang(?proteinLabel) = "en")
}
BIND(IRI(CONCAT("http://purl.uniprot.org/uniprot/", ?wduniprot)) as ?uniprot) 

?uniprot rdfs:seeAlso ?pfam .
?pfam up:database database:Pfam .
?uniprot rdfs:seeAlso ?pdb .
?pdb up:database database:PDB .
?uniprot rdfs:seeAlso ?refseq .
?refseq up:database database:RefSeq .
?uniprot up:classifiedWith ?keyword  .
?keyword rdfs:seeAlso ?goid  .
?goid rdfs:label ?golabel  .
}
GROUP BY ?uniprot ?proteinLabel ?wd_url
~~~

## Getting Wikidata into R ##
It is possible to get content from Wikidata [into R]( http://www.r-bloggers.com/sparql-with-r-in-less-than-5-minutes/) for further analysis or data analysis. The following R script is an example of such a script:

~~~R
library(SPARQL)
library(ggplot2)
wikidataSparql <- "http://wdqs-beta.wmflabs.org/bigdata/namespace/wdq/sparql"
countGenes <- "#QUERY <http://wdqs-beta.wmflabs.org/bigdata/namespace/wdq/sparql>

               PREFIX wd: <http://www.wikidata.org/entity/> 
               PREFIX wdt: <http://www.wikidata.org/prop/direct/>
               PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

               SELECT ?species (count(distinct ?gene) as ?noItems)  WHERE {
                    ?gene wdt:P351 ?entrezID . # P351 Entrez Gene ID
                    ?gene wdt:P703 ?species . # P703 Found in taxon
               }
               GROUP BY ?species"
results <- SPARQL(wikidataSparql, countGenes)
matrix <- as.matrix(results$results)
View(matrix)
~~~