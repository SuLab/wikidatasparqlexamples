[TOC]

# Query wikidata with SPARQL #

Wikidata has its own SPARQL endpoint. SPARQL queries can be submitted via a web form at http://query.wikidata.org/, or, for programmatic access:  https://query.wikidata.org/bigdata/namespace/wdq/sparql?query={SPARQL}
. The latter URL allows integrating Wikidata items with external SPARQL endpoints through [federated queries](http://www.w3.org/TR/sparql11-federated-query/) or to integrate in data analysis packages such as [R](http://www.r-bloggers.com/sparql-with-r-in-less-than-5-minutes/) or any other platform with a SPARQL plugin such as frameworks such as from a external federated query of a framework which includes a SPARQL plugin such as [Text mate with its turtle bundle](https://github.com/peta/turtle.tmbundle). 

### What is this repository for? ###
This repository collects example queries to the SPARQL endpoint of Wikidata. 

## Prefixes ##
PREFIX wd: <http://www.wikidata.org/entity/>

PREFIX wdt: <http://www.wikidata.org/prop/direct/>

PREFIX wikibase: <http://wikiba.se/ontology#>

PREFIX p: <http://www.wikidata.org/prop/>

PREFIX q: <http://www.wikidata.org/prop/qualifier/>

PREFIX reference: <http://www.wikidata.org/prop/reference/>

others: see http://prefix.cc

## Examples ##

### Get mapping of Wikipedia to WikiData to Entrez Gene ###
~~~sparql
PREFIX schema: <http://schema.org/>
PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
SELECT ?entrez_id ?cid ?article ?label WHERE {
    ?cid wdt:P351 ?entrez_id .
  	?cid wdt:P703 wd:Q5 . 
    OPTIONAL {
        ?cid rdfs:label ?label filter (lang(?label) = "en") .
    }
    ?article schema:about ?cid .
    ?article schema:inLanguage "en" .
    FILTER (SUBSTR(str(?article), 1, 25) = "https://en.wikipedia.org/") . 
    FILTER (SUBSTR(str(?article), 1, 38) != "https://en.wikipedia.org/wiki/Template")
} 
limit 10
~~~
[Execute](http://tinyurl.com/oktlvsc)

Same query to run in R
~~~R
library(SPARQL)
sparql <- "https://query.wikidata.org/bigdata/namespace/wdq/sparql"
query <- "prefix schema: <http://schema.org/>
PREFIX wikibase: <http://wikiba.se/ontology#>
PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>

SELECT ?cid ?entrez_id ?label ?article WHERE {
    ?cid wdt:P351 ?entrez_id .
    OPTIONAL {
        ?cid rdfs:label ?label filter (lang(?label) = \"en\") .
    }
    OPTIONAL {
      ?article schema:about ?cid .
      ?article schema:inLanguage \"en\" .
      FILTER (SUBSTR(str(?article), 1, 25) = \"https://en.wikipedia.org/\")
    }
} 
"
results <- SPARQL(sparql, query)
View(as.matrix(results$results))
~~~

~~~R
library(SPARQL)
library(ggplot2)
library(rworldmap)

wdqs <- "https://query.wikidata.org/bigdata/namespace/wdq/sparql"
query <- "PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX p: <http://www.wikidata.org/prop/>
PREFIX v: <http://www.wikidata.org/prop/statement/>
PREFIX qualifier: <http://www.wikidata.org/prop/qualifier/>
PREFIX statement: <http://www.wikidata.org/prop/statement/>
SELECT DISTINCT ?countryLabel ?ISO3Code ?latlon ?prevalence ?year WHERE {
wd:Q36956 wdt:P699 ?doid ; # P699 Disease ontology ID
p:P1193 ?prevalencewithProvenance . # P1193 prevalence
?prevalencewithProvenance qualifier:P17 ?country ;
qualifier:P585 ?year ;
statement:P1193 ?prevalence . # P17 country
?country wdt:P625 ?latlon ;
rdfs:label ?countryLabel ;
wdt:P298 ?ISO3Code ;
wdt:P297 ?ISOCode .
FILTER (lang(?countryLabel) = \"en\")
}"

results <- SPARQL(wdqs, query)
resultMatrix <- as.matrix(results$results)
View(resultMatrix)
sPDF <- joinCountryData2Map(results$results, joinCode = "ISO3", nameJoinColumn = "ISO3Code")
mapCountryData(sPDF, nameColumnToPlot="prevalence",  oceanCol="lightblue", missingCountryCol="white", mapTitle="Prevalence of leprosy in the Americas")
View(getMap())


~~~
## Creating a spatial map with R ##
Python
~~~python
__author__ = 'Sebastian Burgstaller'


from SPARQLWrapper import SPARQLWrapper, JSON
import pprint

sparql = SPARQLWrapper("https://query.wikidata.org/bigdata/namespace/wdq/sparql")
sparql.setQuery("""
    prefix schema: <http://schema.org/>
PREFIX wikibase: <http://wikiba.se/ontology#>
PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>

SELECT ?cid ?entrez_id ?label ?article WHERE {
    ?cid wdt:P351 ?entrez_id .
    OPTIONAL {
        ?cid rdfs:label ?label filter (lang(?label) = "en") .
    }
    OPTIONAL {
      ?article schema:about ?cid .
      ?article schema:inLanguage "en" .
      FILTER (SUBSTR(str(?article), 1, 25) = "https://en.wikipedia.org/")
    }
} 
""")

sparql.setReturnFormat(JSON)
results = sparql.query().convert()

pprint.pprint(results)
~~~

## Get all the gene ontology evidence codes used in wikidata ##
~~~sparql
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX wd: <http://www.wikidata.org/entity/>

select distinct ?evidence_code ?evidence_codeLabel where {
	?evidence_code wdt:P31 wd:Q23173209
    SERVICE wikibase:label {
    	bd:serviceParam wikibase:language "en" .
  	}
}
~~~

## Get 10 Gene Ontology subcellular localization information, with evidence codes, and references for Reelin ##
~~~sparql
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX p: <http://www.wikidata.org/prop/>
PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX pq: <http://www.wikidata.org/prop/qualifier/>

SELECT distinct ?go_bp ?go_bpLabel ?determination ?determinationLabel ?reference_stated_inLabel ?reference_retrieved WHERE {
  #?protein wdt:P352 "P78509" . # get a protein by uniprot id 
  # note the difference between wdt:P681 and p:681 in the following two statements
  #wdt gets you to the value of the property (generally what you would expect)
  #p gets you to the wikidata statement (which is where qualifiers and references live)
  wd:Q13561329 wdt:P681 ?go_bp . # get a protein record directly and get biological process annotations
  wd:Q13561329 p:P681 ?go_bp_statement . #get the statements associated with the bp annotations
  ?go_bp_statement pq:P459 ?determination . # get 'determination method' qualifiers associated with the statements
  # change to wd:Q23175558 for ISS (Inferred from Sequence or structural Similarity)
  # or e.g. wd:Q23190881 for IEA (Inferred from Electronic Annotation)
  #add reference links 
  ?go_bp_statement prov:wasDerivedFrom/pr:P248 ?reference_stated_in . #where stated
  ?go_bp_statement prov:wasDerivedFrom/pr:P813 ?reference_retrieved . #when retrieved
  #add labels to everything (and retrieve by appending Label to the item you want in the response)
  SERVICE wikibase:label {
    bd:serviceParam wikibase:language "en" .
  }
}
limit 10
~~~

## Get all the drug-drug interactions for Methadone based on its CHEMBL id CHEMBL651 ##
~~~sparql
PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX p: <http://www.wikidata.org/prop/>
PREFIX v: <http://www.wikidata.org/prop/statement/>
   SELECT ?compound ?chembl ?label WHERE {
       ?p p:P592/v:P592 'CHEMBL651' .
       ?p wdt:P769 ?compound .
       ?compound wdt:P592 ?chembl .
       OPTIONAL  {?compound rdfs:label ?label filter (lang(?label) = "en")}
}
~~~
[Execute](http://tinyurl.com/ofpugzh)

## Get all wikidata statements that cite an academic article as a reference ##
~~~sparql
PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX pr: <http://www.wikidata.org/prop/reference/>

SELECT ?statement ?PMID ?PMCID WHERE {
  ?statement prov:wasDerivedFrom/pr:P248 ?paper .
  ?paper wdt:P31 wd:Q13442814 .
  OPTIONAL { ?paper wdt:P698 ?PMID . }
  OPTIONAL { ?paper wdt:P932 ?PMCID . }
  FILTER (!BOUND(?PMID))
}
~~~

## Get all Wikidata  items with a Disease Ontology ID ##
~~~sparql
PREFIX wd: <http://www.wikidata.org/entity/> 
PREFIX wdt: <http://www.wikidata.org/prop/direct/>

SELECT * WHERE {
   ?diseases wdt:P699 ?doid .
}
~~~
[Execute](http://query.wikidata.org/#PREFIX%20wd%3A%20%3Chttp%3A%2F%2Fwww.wikidata.org%2Fentity%2F%3E%20%0APREFIX%20wdt%3A%20%3Chttp%3A%2F%2Fwww.wikidata.org%2Fprop%2Fdirect%2F%3E%0A%0ASELECT%20*%20WHERE%20%7B%0A%20%20%20%3Fdiseases%20wdt%3AP699%20%3Fdoid%20.%0A%7D)

## Get a Wikidata items with a particular Disease Ontology ID ##
~~~sparql
PREFIX wd: <http://www.wikidata.org/entity/> 
PREFIX wdt: <http://www.wikidata.org/prop/direct/>

SELECT * WHERE {
   ?diseases wdt:P699 "DOID:8577" .
}
~~~
[Execute](https://query.wikidata.org/#PREFIX%20wd%3A%20%3Chttp%3A%2F%2Fwww.wikidata.org%2Fentity%2F%3E%20%0APREFIX%20wdt%3A%20%3Chttp%3A%2F%2Fwww.wikidata.org%2Fprop%2Fdirect%2F%3E%0A%0ASELECT%20*%20WHERE%20%7B%0A%20%20%20%3Fdiseases%20wdt%3AP699%20%22DOID%3A8577%22%20.%0A%7D)

## Count the number of Genes in Wikidata grouped by species ##
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
[Execute](http://tinyurl.com/q296vut)

## Go terms in Wikidata ##
~~~sparql
PREFIX wikibase: <http://wikiba.se/ontology#>
PREFIX wd: <http://www.wikidata.org/entity/> 
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX p: <http://www.wikidata.org/prop/>
PREFIX v: <http://www.wikidata.org/prop/statement/>
PREFIX reference: <http://www.wikidata.org/prop/reference/>
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX schema: <http://schema.org/>
SELECT * WHERE {
  ?wdid wdt:P686 ?go_id .
  ?wdid rdfs:label ?go_name .
  FILTER (LANG(?go_name) = "en")
 }
~~~
[Execute](http://tinyurl.com/qyvtsc6)

###Counts of subcellular localization annotations associated with human genes###
~~~sparql
PREFIX wd: <http://www.wikidata.org/entity/> 
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?gene (count (distinct ?go_term) as ?noGo)  WHERE {
   ?gene wdt:P351 ?entrezID . # P351 Entrez Gene ID
   ?gene wdt:P703 wd:Q5 . # P703 Found in taxon human 
	?gene wdt:P688 ?protein . # encodes a thing
  ?protein wdt:P279 wd:Q8054 . # that thing is a protein
  ?protein wdt:P681 ?go_term    # that protein has some annotation regarding subcellular localization
}
 GROUP BY ?gene
~~~


### All Gene Ontology evidence codes present als qualifiers on items
~~~sparql
PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX pq: <http://www.wikidata.org/prop/qualifier/>

SELECT * WHERE {
  {
      SELECT ?code WHERE {
          ?code wdt:P31 wd:Q23173209 .
      }
      GROUP BY ?code 
  }
  ?p pq:P459 ?code .
}
~~~

### Proteins added by ProteinBoxBot ###
~~~sparql
PREFIX wikibase: <http://wikiba.se/ontology#>
PREFIX wd: <http://www.wikidata.org/entity/> 
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX p: <http://www.wikidata.org/prop/>
PREFIX v: <http://www.wikidata.org/prop/statement/>
PREFIX reference: <http://www.wikidata.org/prop/reference/>
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX schema: <http://schema.org/>
SELECT ?protein_name ?uniprot_id ?wdid ?wdtimestamp ?stated_in WHERE {
  ?wdid wdt:P279 wd:Q8054 .
  ?wdid rdfs:label ?protein_name .
  ?wdid wdt:P352 ?uniprot_id .
  ?wdid schema:dateModified ?wdtimestamp .
  ?wdid p:P279 ?metadata  .
  ?metadata prov:wasDerivedFrom ?prov .
  ?prov reference:P143 wd:Q905695 .
  ?prov reference:P854 ?stated_in .
  FILTER (lang(?protein_name) = "en")
 }
~~~
[Execute](http://tinyurl.com/pn36ulp)

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
SERVICE <https://query.wikidata.org/bigdata/namespace/wdq/sparql>{
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
wikidataSparql <- "https://query.wikidata.org/bigdata/namespace/wdq/sparql"
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

## SPARQL template queries for ProteinBoxBots ##
### Getting all proteins from Uniprot for species 272561 ###
~~~sparql
PREFIX up:<http://purl.uniprot.org/core/> 
PREFIX taxonomy: <http://purl.uniprot.org/taxonomy/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
SELECT DISTINCT *
WHERE
{
	?protein a up:Protein .
        ?protein up:reviewed "true"^^xsd:boolean .
  	?protein rdfs:label ?protein_label .
        ?protein up:organism taxonomy:272561 .
}
~~~
[Execute](http://sparql.uniprot.org/sparql/?format=html&query=PREFIX+up%3A%3Chttp%3A%2F%2Fpurl.uniprot.org%2Fcore%2F%3E+%0D%0APREFIX+taxonomy%3A+%3Chttp%3A%2F%2Fpurl.uniprot.org%2Ftaxonomy%2F%3E%0D%0APREFIX+xsd%3A+%3Chttp%3A%2F%2Fwww.w3.org%2F2001%2FXMLSchema%23%3E%0D%0ASELECT+DISTINCT+*%0D%0AWHERE%0D%0A%7B%0D%0A%09%09%3Fprotein+a+up%3AProtein+.%0D%0A++++++++%3Fprotein+up%3Areviewed+%22true%22%5E%5Exsd%3Aboolean+.%0D%0A++%09%09%3Fprotein+rdfs%3Alabel+%3Fprotein_label+.%0D%0A++++++++%3Fprotein+up%3Aorganism+taxonomy%3A272561+.%0D%0A%7D)

### Getting protein annotations for protein: O84188 ###

~~~sparql
PREFIX up:<http://purl.uniprot.org/core/>
PREFIX skos:<http://www.w3.org/2004/02/skos/core#>
PREFIX taxonomy:<http://purl.uniprot.org/taxonomy/>
PREFIX database:<http://purl.uniprot.org/database/>
SELECT ?uniprot ?plabel ?ecName ?upversion 
       (group_concat(distinct ?encodedBy; separator="; ") as ?encoded_by)
       (group_concat(distinct ?alias; separator="; ") as ?upalias)
       (group_concat(distinct ?pdb; separator="; ") as ?pdbid)
       (group_concat(distinct ?refseq; separator="; ") as ?refseqid)
       (group_concat(distinct ?ensP; separator="; ") as ?ensemblp)
WHERE
{
     VALUES ?uniprot {<http://purl.uniprot.org/uniprot/O84188>}
        ?uniprot rdfs:label ?plabel .
        ?uniprot up:version ?upversion . 
        ?uniprot up:encodedBy ?gene .
		?gene skos:prefLabel ?encodedBy .
        optional{?uniprot up:alternativeName ?upAlias .
        ?upAlias up:ecName ?ecName .}
        
        OPTIONAL{ ?uniprot up:alternativeName ?upAlias .
           {?upAlias up:fullName ?alias .} UNION
           {?upAlias up:shortName ?alias .}}
        ?uniprot up:version ?upversion .
        OPTIONAL{?uniprot rdfs:seeAlso ?pdb .
        ?pdb up:database database:PDB .}
        OPTIONAL{?uniprot rdfs:seeAlso ?refseq .
        ?refseq up:database database:RefSeq .}  
        OPTIONAL{?uniprot rdfs:seeAlso ?ensT .
        ?ensT up:database database:Ensembl .
        ?ensT up:translatedTo ?ensP .}
}
group by ?upAlias ?uniprot ?encodedBy ?plabel ?ecName ?upversion
~~~

### Retrieve all membrane proteins annotated for a role in colorectal cancer ###

~~~sparql
PREFIX up: <http://purl.uniprot.org/core/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX obo: <http://purl.obolibrary.org/obo/>
PREFIX sio: <http://semanticscience.org/resource/>
PREFIX efo: <http://www.ebi.ac.uk/efo/>
PREFIX atlas: <http://rdf.ebi.ac.uk/resource/atlas/>
PREFIX atlasterms: <http://rdf.ebi.ac.uk/terms/atlas/>

SELECT DISTINCT ?geneLabel ?wdncbi ?geneLocStart ?geneLocStop ?disease_text ?goLabel

WHERE
{    
    SERVICE <https://query.wikidata.org/bigdata/namespace/wdq/sparql>
    {
        ?gene wdt:P351 ?wdncbi ;
              wdt:P703 wd:Q5;
         #rdfs:label ?geneLabel ;
         #wdt:P644 ?geneLocStart ;
         #wdt:P645 ?geneLocStop ;
         
         wdt:P688 ?wd_protein .
        ?wd_protein wdt:P352 ?uniprot_id ;
            wdt:P681 ?go_term .
        ?go_term wdt:P686 "GO:0016020" .
            #rdfs:label ?goLabel .   
    }
    BIND(IRI(CONCAT("http://purl.uniprot.org/uniprot/", ?uniprot_id)) as ?protein)
		      ?protein up:annotation ?annotation .
		      ?annotation a up:Disease_Annotation .
        ?annotation up:disease ?disease_annotation .
        ?disease_annotation <http://www.w3.org/2004/02/skos/core#prefLabel> ?disease_text .
    FILTER(REGEX(?disease_text, "Colorectal cancer", "i"))
    FILTER(LANG(?geneLabel) = "en")
    FILTER(LANG(?goLabel) = "en")  
}
~~~

### Get GO annotations for protein O84188 ###

~~~sparql
PREFIX up:<http://purl.uniprot.org/core/> 
PREFIX skos:<http://www.w3.org/2004/02/skos/core#> 
SELECT DISTINCT ?protein ?go ?goLabel ?parentLabel
WHERE
{
  		VALUES ?protein {<http://purl.uniprot.org/uniprot/O84188>}
		?protein a up:Protein .
  		?protein up:classifiedWith ?go .   
        ?go rdfs:label ?goLabel .
        ?go rdfs:subClassOf* ?parent .
        ?parent rdfs:label ?parentLabel .
        optional {?parent rdfs:subClassOf ?grandParent .}
        FILTER (!bound(?grandParent))
}
~~~
[Execute](http://sparql.uniprot.org/sparql/?format=html&query=PREFIX+up%3A%3Chttp%3A%2F%2Fpurl.uniprot.org%2Fcore%2F%3E+%0D%0APREFIX+skos%3A%3Chttp%3A%2F%2Fwww.w3.org%2F2004%2F02%2Fskos%2Fcore%23%3E+%0D%0ASELECT+DISTINCT+%3Fprotein+%3Fgo+%3FgoLabel+%3FparentLabel%0D%0AWHERE%0D%0A%7B%0D%0A++%09%09VALUES+%3Fprotein+%7B%3Chttp%3A%2F%2Fpurl.uniprot.org%2Funiprot%2FO84188%3E%7D%0D%0A%09%09%3Fprotein+a+up%3AProtein+.%0D%0A++%09%09%3Fprotein+up%3AclassifiedWith+%3Fgo+.+++%0D%0A++++++++%3Fgo+rdfs%3Alabel+%3FgoLabel+.%0D%0A++++++++%3Fgo+rdfs%3AsubClassOf*+%3Fparent+.%0D%0A++++++++%3Fparent+rdfs%3Alabel+%3FparentLabel+.%0D%0A++++++++optional+%7B%3Fparent+rdfs%3AsubClassOf+%3FgrandParent+.%7D%0D%0A++++++++FILTER+%28%21bound%28%3FgrandParent%29%29%0D%0A%7D)

### Get all 'isa' parents of GO term given its wikidata identifier ###
~~~sparql
PREFIX wikibase: <http://wikiba.se/ontology#>
PREFIX wd: <http://www.wikidata.org/entity/> 
PREFIX wdt: <http://www.wikidata.org/prop/direct/>

SELECT DISTINCT ?parentLabel 
WHERE
{
    wd:Q14326094 wdt:P279* ?parent .
    SERVICE wikibase:label {
    bd:serviceParam wikibase:language "en" .
  }
}
~~~

# Curation queries for Wikidata

## Get all human proteins added by PBB
~~~sparql
    PREFIX wdt: <http://www.wikidata.org/prop/direct/>
    PREFIX wd: <http://www.wikidata.org/entity/>
    PREFIX p: <http://www.wikidata.org/prop/>
    PREFIX v: <http://www.wikidata.org/prop/statement/>
    PREFIX prov: <http://www.w3.org/ns/prov#>
    PREFIX reference: <http://www.wikidata.org/prop/reference/>
    SELECT ?ncbigeneId WHERE {
    ?gene wdt:P279 wd:Q7187 .
    ?gene p:P351 ?ncbigeneId .
    ?gene wdt:P703 wd:Q5 .
    ?gene ?p ?o .
    ?o prov:wasDerivedFrom ?derivedFrom .
    ?derivedFrom reference:P143 wd:Q20641742 .
}
~~~
[Execute](https://query.wikidata.org/#PREFIX%20wdt%3A%20%3Chttp%3A%2F%2Fwww.wikidata.org%2Fprop%2Fdirect%2F%3E%0A%20%20%20%20PREFIX%20wd%3A%20%3Chttp%3A%2F%2Fwww.wikidata.org%2Fentity%2F%3E%0A%20%20%20%20PREFIX%20p%3A%20%3Chttp%3A%2F%2Fwww.wikidata.org%2Fprop%2F%3E%0A%20%20%20%20PREFIX%20v%3A%20%3Chttp%3A%2F%2Fwww.wikidata.org%2Fprop%2Fstatement%2F%3E%0A%20%20%20%20PREFIX%20prov%3A%20%3Chttp%3A%2F%2Fwww.w3.org%2Fns%2Fprov%23%3E%0A%20%20%20%20PREFIX%20reference%3A%20%3Chttp%3A%2F%2Fwww.wikidata.org%2Fprop%2Freference%2F%3E%0A%20%20%20%20SELECT%20%3FncbigeneId%20WHERE%20%7B%0A%20%20%20%20%3Fgene%20wdt%3AP279%20wd%3AQ7187%20.%0A%20%20%20%20%3Fgene%20p%3AP351%20%3FncbigeneId%20.%0A%20%20%20%20%3Fgene%20wdt%3AP703%20wd%3AQ5%20.%0A%20%20%20%20%3Fgene%20%3Fp%20%3Fo%20.%0A%20%20%20%20%3Fo%20prov%3AwasDerivedFrom%20%3FderivedFrom%20.%0A%20%20%20%20%3FderivedFrom%20reference%3AP143%20wd%3AQ20641742%20.%0A%7D)

## Get all human genes added by PBB
~~~sparql
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
    PREFIX wd: <http://www.wikidata.org/entity/>
    PREFIX p: <http://www.wikidata.org/prop/>
    PREFIX v: <http://www.wikidata.org/prop/statement/>
    PREFIX prov: <http://www.w3.org/ns/prov#>
    PREFIX reference: <http://www.wikidata.org/prop/reference/>
    SELECT DISTINCT ?ncbigeneId WHERE {
    ?gene wdt:P279 wd:Q7187 .
    ?gene p:P351 ?ncbigeneId .
    ?gene wdt:P703 wd:Q5 .
    ?ncbigeneId prov:wasDerivedFrom ?derivedFrom .
    ?derivedFrom reference:P143 wd:Q20641742 .
}
~~~

## Count the Disease ontology terms in Wikidata by their rank (deprecated and normal)
~~~sparql
PREFIX wd: <http://www.wikidata.org/entity/> 
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX p: <http://www.wikidata.org/prop/>
PREFIX wikibase: <http://wikiba.se/ontology#>

SELECT DISTINCT ?rank (count(?rank) as ?counts)  WHERE {
   VALUES ?rank { wikibase:DeprecatedRank wikibase:NormalRank }
   ?diseases p:P699 ?doid .
   ?doid wikibase:rank ?rank .
}
GROUP BY ?rank
~~~
[Execute](https://query.wikidata.org/#PREFIX%20wd%3A%20%3Chttp%3A%2F%2Fwww.wikidata.org%2Fentity%2F%3E%20%0APREFIX%20wdt%3A%20%3Chttp%3A%2F%2Fwww.wikidata.org%2Fprop%2Fdirect%2F%3E%0APREFIX%20p%3A%20%3Chttp%3A%2F%2Fwww.wikidata.org%2Fprop%2F%3E%0APREFIX%20wikibase%3A%20%3Chttp%3A%2F%2Fwikiba.se%2Fontology%23%3E%0A%0ASELECT%20DISTINCT%20%3Frank%20(count(%3Frank)%20as%20%3Fcounts)%20%20WHERE%20%7B%0A%20%20%20VALUES%20%3Frank%20%7B%20wikibase%3ADeprecatedRank%20wikibase%3ANormalRank%20%7D%0A%20%20%20%3Fdiseases%20p%3AP699%20%3Fdoid%20.%0A%20%20%20%3Fdoid%20wikibase%3Arank%20%3Frank%20.%0A%7D%0AGROUP%20BY%20%3Frank)

## Get all disease ontology IDs in wikidata of both rank Normal and deprecated rank


```
#!SPARQL

PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX p: <http://www.wikidata.org/prop/>
PREFIX wikibase: <http://wikiba.se/ontology#>
PREFIX statement: <http://www.wikidata.org/prop/statement/>

SELECT DISTINCT ?do WHERE {
   VALUES ?rank { wikibase:DeprecatedRank wikibase:NormalRank }
   ?diseases p:P699 ?doid .
   ?doid statement:P699 ?do .
   ?doid wikibase:rank ?rank .
}
```
[Execute](https://query.wikidata.org/#PREFIX%20wd%3A%20%3Chttp%3A%2F%2Fwww.wikidata.org%2Fentity%2F%3E%0APREFIX%20wdt%3A%20%3Chttp%3A%2F%2Fwww.wikidata.org%2Fprop%2Fdirect%2F%3E%0APREFIX%20p%3A%20%3Chttp%3A%2F%2Fwww.wikidata.org%2Fprop%2F%3E%0APREFIX%20wikibase%3A%20%3Chttp%3A%2F%2Fwikiba.se%2Fontology%23%3E%0APREFIX%20statement%3A%20%3Chttp%3A%2F%2Fwww.wikidata.org%2Fprop%2Fstatement%2F%3E%0A%0ASELECT%20DISTINCT%20%3Fdo%20WHERE%20%7B%0A%20%20%20VALUES%20%3Frank%20%7B%20wikibase%3ADeprecatedRank%20wikibase%3ANormalRank%20%7D%0A%20%20%20%3Fdiseases%20p%3AP699%20%3Fdoid%20.%0A%20%20%20%3Fdoid%20statement%3AP699%20%3Fdo%20.%0A%20%20%20%3Fdoid%20wikibase%3Arank%20%3Frank%20.%0A%7D)

# microbial queries
## Request all wikidata items that are instance of or subclass of genes and have taxon any child of Bacteria
~~~sparql
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
    PREFIX wd: <http://www.wikidata.org/entity/>
    PREFIX p: <http://www.wikidata.org/prop/>
    SELECT DISTINCT ?gene ?taxa WHERE {
    {?gene wdt:P31 wd:Q7187 }
    UNION  
    {?gene wdt:P279 wd:Q7187 } .
    ?gene wdt:P703 ?taxa .
    ?taxa wdt:P171* wd:Q10876  
}
~~~
[Execute](https://query.wikidata.org/#PREFIX%20wdt%3A%20%3Chttp%3A%2F%2Fwww.wikidata.org%2Fprop%2Fdirect%2F%3E%0A%20%20%20%20PREFIX%20wd%3A%20%3Chttp%3A%2F%2Fwww.wikidata.org%2Fentity%2F%3E%0A%20%20%20%20PREFIX%20p%3A%20%3Chttp%3A%2F%2Fwww.wikidata.org%2Fprop%2F%3E%0A%20%20%20%20SELECT%20DISTINCT%20%3Fgene%20%3Ftaxa%20WHERE%20%7B%0A%20%20%20%20%7B%3Fgene%20wdt%3AP31%20wd%3AQ7187%20%7D%0A%20%20%20%20UNION%20%20%0A%20%20%20%20%7B%3Fgene%20wdt%3AP279%20wd%3AQ7187%20%7D%20.%0A%20%20%20%20%3Fgene%20wdt%3AP703%20%3Ftaxa%20.%0A%20%20%20%20%3Ftaxa%20wdt%3AP171*%20wd%3AQ10876%20%20%0A%7D)

## Request all operons, their regulators, and their products
~~~sparql
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX wd: <http://www.wikidata.org/entity/>
SELECT ?taxa_name ?regulator_name ?operon_name ?go_name ?product_name 
WHERE {   
?operon wdt:P279 wd:Q139677 ;
rdfs:label ?operon_name ;
   	wdt:P527 ?gene ;
   	wdt:P1056 ?protein .  
?regulator wdt:P128 ?operon  ;
   	rdfs:label ?regulator_name .
?protein ?function_type ?go_term ;
 	wdt:P1056 ?product .
?go_term wdt:P686 ?go_id ;
   	rdfs:label ?go_name .   
?product rdfs:label ?product_name . 
?gene wdt:P703 ?taxa .
?taxa rdfs:label ?taxa_name . 
FILTER (LANG(?taxa_name) = "en") .
   	FILTER (LANG(?regulator_name) = "en") .
   	FILTER (LANG(?go_name) = "en") 
  	FILTER (LANG(?product_name) = "en") .  
}
~~~
[Execute](http://tinyurl.com/pt9apmy)

## Request all bacterial genes, their linked proteins, and their linked GO terms
~~~sparql
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX wd: <http://www.wikidata.org/entity/>
SELECT DISTINCT ?taxa_name ?gene_id ?uniprot_id ?prot_name ?go_name 
WHERE {
?gene wdt:P351 ?gene_id ; 
wdt:P688 ?protein ;
  wdt:P703 ?taxa .
  ?protein rdfs:label ?prot_name ;  
	wdt:P352 ?uniprot_id ; 
	?function_type ?go_term .
  ?go_term rdfs:label ?go_name . 
  ?taxa wdt:P171* wd:Q10876 ;
	rdfs:label ?taxa_name .
FILTER (LANG(?go_name) = "en") .
FILTER (LANG(?taxa_name) = "en") .
FILTER (LANG(?prot_name) = "en") .
}
~~~
[Execute](http://tinyurl.com/pulsew3)

## Request all organisms that are located (P276) in the female urogential tract (wd:Q5880) and that have a gene with product (P1056) indole (wd:Q319541). 
~~~sparql

PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX wd: <http://www.wikidata.org/entity/>
SELECT ?organism_name WHERE {   
  ?organism_item wdt:P276 wd:Q5880 ;
    rdfs:label ?organism_name . 
  ?gene wdt:P703 ?organism_item ; 
    wdt:P1056 wd:Q319541 . 
  FILTER (LANG(?organism_name) = "en") .    
}  
~~~
[Execute](http://tinyurl.com/no7sxv8)

# Queries for problems #
## Get a list of human genes with wikidata items but no English wikipedia page associated with them.  (results would eventually contain wikipedia links, the linkless appear on the top of the list)##
~~~sparql
PREFIX schema: <http://schema.org/>
PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
SELECT ?entrez_id ?cid ?article ?label WHERE {
    ?cid wdt:P351 ?entrez_id .
  	?cid wdt:P703 wd:Q5 . 
    OPTIONAL {
        ?cid rdfs:label ?label filter (lang(?label) = "en") .
    	?article schema:about ?cid .
    	?article schema:inLanguage "en" .
      }
} 
  ORDER BY ASC(?article)
limit 10
~~~
Get entrez gene ids mapped to multiple wikidata items
~~~sparql
PREFIX schema: <http://schema.org/>
PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
SELECT ?entrez_id (COUNT(DISTINCT ?cid) as ?C) WHERE {
    ?cid wdt:P351 ?entrez_id .
} 
GROUP BY ?entrez_id
ORDER BY DESC(?C) 
limit 100
~~~

# Jenkins queries
Identify the time Wikidata's sparql endpoint was updated last
~~~sparql
PREFIX schema: <http://schema.org/>
SELECT * WHERE { <http://www.wikidata.org> schema:dateModified ?y }
~~~

# Random Queries of interest for demos # 
Find the richest countries per capita in the world
~~~sparql
PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX wikibase: <http://wikiba.se/ontology#>
PREFIX p: <http://www.wikidata.org/prop/>
PREFIX v: <http://www.wikidata.org/prop/statement/>
PREFIX q: <http://www.wikidata.org/prop/qualifier/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT distinct ?countryLabel ?population ?gdp (xsd:float(xsd:float(?gdp)/xsd:float(?population)) AS ?perCapita)
WHERE 
{
  ?country wdt:P31/wdt:P279* wd:Q6256 .  # find instances or subclasses of country
  ?country wdt:P1082 ?population . 
  ?country wdt:P2131 ?gdp .
  FILTER ( ?population > 1000 ) 
  SERVICE wikibase:label {
    bd:serviceParam wikibase:language "en" .
  }
}
order by DESC(?perCapita)
limit 100
~~~

# Data unit tests
## Report all Gene ontology gene annotations which do not have Gene Ontology ID

~~~sparql
PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>

SELECT ?pot_go WHERE {
  {
  SELECT distinct ?pot_go WHERE {
      {?protein wdt:P680 ?pot_go} 
      UNION {?protein wdt:P681 ?pot_go} 
      UNION {?protein wdt:P682 ?pot_go} .

    }
    Group BY ?pot_go
  }

  FILTER NOT EXISTS {?pot_go wdt:P686 ?no_go} .
 }
 ORDER BY ?pot_go
~~~

## Query for all Wikidata items that are both annotated as being of subclass of gene and protein
~~~sparql
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX wd: <http://www.wikidata.org/entity/>
SELECT * WHERE {
  ?gene wdt:P279 wd:Q7187 .
  ?gene wdt:P279 wd:Q8054 .
}
~~~
[Execute](https://query.wikidata.org/#PREFIX%20wikibase%3A%20%3Chttp%3A%2F%2Fwikiba.se%2Fontology%23%3E%0APREFIX%20wd%3A%20%3Chttp%3A%2F%2Fwww.wikidata.org%2Fentity%2F%3E%20%0APREFIX%20wdt%3A%20%3Chttp%3A%2F%2Fwww.wikidata.org%2Fprop%2Fdirect%2F%3E%0APREFIX%20rdfs%3A%20%3Chttp%3A%2F%2Fwww.w3.org%2F2000%2F01%2Frdf-schema%23%3E%0APREFIX%20p%3A%20%3Chttp%3A%2F%2Fwww.wikidata.org%2Fprop%2F%3E%0APREFIX%20v%3A%20%3Chttp%3A%2F%2Fwww.wikidata.org%2Fprop%2Fstatement%2F%3E%0ASELECT%20*%20WHERE%20%7B%0A%20%20%3Fgene%20wdt%3AP279%20wd%3AQ7187%20.%0A%20%20%3Fgene%20wdt%3AP279%20wd%3AQ8054%20.%0A%20%7D)