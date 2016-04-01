[TOC]

# Count available language version for the DO terms #
~~~sparql
SELECT ?disease ?doid ?enLabel (count(?language) as ?languages) 
WHERE
{
	?disease wdt:P699 ?doid ;
             rdfs:label ?label ;
             rdfs:label ?enLabel .
    FILTER (lang(?enLabel) = "en")
    
    BIND (lang(?label) AS ?language)
}
group by ?disease ?doid ?enLabel
order by desc(?languages)
~~~
[Execute](http://tinyurl.com/he7dpsl)

![alt tag](http://embed.vida.io/documents/sy7vzWW7BJEvKdZeL)