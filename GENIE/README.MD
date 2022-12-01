# GENIE APPROACH
IN PROGRESS
Genie can generate RDF triplets from raw text in one only step (no lexicalization needed) since the text triplets that the model generates are bound to the constrictions of the ontology. The downside is that Genie is made with WIKIDATA as the ontology.

After some discussion with the author of the repo:

```
I don't know all the details of how DBpedia is structured, but you could potentially:

Try to match GenIE's output to DBpedia (for this, you would need a mapping between Wikidata entities and relations and their DBpedia counterparts). This case does not require re-training the model.
Get training data that corresponds to DBpedia (DBpediaTriplets-to-Text) and retrain the model.
Let me know if you have any other questions!
```

I have been trying to associate resources and properties from Wikidata to DBpedia.