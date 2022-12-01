# DBpedia-abstracts-to-RDF
Web application to convert DBpedia abstracts into a set of RDF triples.

This is a Gsoc project in colaboration with DBpedia, more information can be found [here][1].

During the development of the GSoC project, a blog has been created with weekly entries explaining how the tool has been built and what difficulties we have encountered along the way. **This blog can be accessed [here][2].**

In addition, there is a folder [codingweeks][3] where there is a python script for each week with the pipeline developed so far.

The work has been extended incorporating morphosyntactic patterns, new entries in the lexicalization tables, reworking the python code and adding a new page to the web interface to manage the lexicalizations table.

There are currently two versions of this work. The first one is based on morphosyntactic patterns using spacy syntactic trees, called Text2RDF (GSoC). The last approach developed consists in the use of deep learning models such as BART to extract the relations, then lexicalized with a method similar to the first work.

## Repo structure
Explaination of the repo structure (folder meaning):

- code: Text2RDF implementation (webapp, cmd tool and coding weeks from GSoC).

- datasets: lexicalizations, benchmarks, ontologies, etc.

- Rebel: Implementation of the tool using deep learning models such REBEL.

- docs: GSoC development blog.

- evaluation: Evaluation where, which and who made by Pablo.

- pyclausie: First approach of GSoC development using pyclausie repo (aborted)

- results: Several files with results, examples and statistics obtained during GSoC.

- spotlight: Dbpedia Spotlight server and model files

In most folders there is a readme file that explains in more detail each section of the repo.

## Text2RDF pipeline overview 
The tool performs the following steps to translate from text to RDF:
1. Clean up the text superficially (remove some parenthesis and special characters).
2. Apply the dependency parse tree to the original text. 
3. Resolve coreferences.
4. Split the text into sentences.
5. Get all text triples.
   1. Simplify subordinate sentences by applying rule-based patterns.
   2. Split related verbs by conjunctions.
   3. For each simplified sentence, extract text triples (`subject | predicate | object`) by applying rule-based patterns.
6. Apply DBpedia Spotlight on the original text to create a dictionary with those resources identified by NER. 
7. For each text triples replace the subject and object with the resources (URIs) identified by Spotlight (if they have been identified).
8. To translate the predicate, a lookup table is used to search by verb + preposition and obtain a property from the DBpedia ontology.
9. If the verb of the predicate is the verb `to be` the property will be `rdf:type` and the object will be a DBpedia class. For this another lexicalization table is needed.
10. Finally the RDF triples with the structure `resource | property | resource` are obtained if there has not been any lexicalization problem. In the case in which a valid lexicalization is not found we will find a `literal` in the triple.

## REBEL pipeline overview 
The tool performs the following steps to translate from text to RDF:
1. Load the tokenizer and the model from the transformers library.
2. Load the input (dataframe or single text).
3. Load model parameters.
4. For each text loaded in step 2, get triple text.
   1. (Optional) Resolve correferences.
   2. (Optional) Split text into single sentences..
   3. Run the model and format the results into (`subject | predicate | object`).
5. Apply DBpedia Spotlight on the original text and the text triples to create a dictionary with those resources identified by NER. 
6. For each text triples replace the subject and object with the resources (URIs) identified by Spotlight (if they have been perfectly identified).
7. To translate the predicate, a lookup table is used to search from a fixed text [property list][15] and obtain a property from the DBpedia or the wikidata ontology.
8. Depending on the identified property, the object is treated as a resource or as a literal (date, integer or year).
10. Finally the RDF triples with the structure `resource | property | resource` are obtained if there has not been any lexicalization problem. In the case in which a valid lexicalization is not found we will find a `literal` in the triple.s

More in depth of this approach in the[doc file][14] under the REBEL folder.

## Requirements
The first step is to install the requirements:
```console
python -m pip install -r requirements.txt
```

In order to install the spacy and coreferee models, run the following commands:
```console
python -m spacy download en_core_web_trf
python -m spacy download en_core_web_lg
python -m coreferee install en
```

The model ending in `_lg` needs to be installed as it is a requirement to be able to use the coreferee library to deal with coreferences.

The next step, which is optional, would be to install the local DBpedia Spotlight server. To do so, just download the model and the server file from the following [tutorial][7]. It is also explained in detail in the [spotlight][8] folder.

Although it is easier and highly recommended to download the [DBpedia spotlight Docker image][13] to your local machine to run the DBpedia spotlight service.

If you do not want to install the tool you can make use of the Spotlight online API, being this slower. The pipeline is designed so that if you cannot connect to the local server you can use the online API, however you can specify directly to use the online API by modifying an argument of the `brt.get_annotated_text_dict(raw_text, service_url=SPOTLIGHT_LOCAL_URL)` function that can be found in the pipeline.
You should replace `service_url=SPOTLIGHT_LOCAL_URL` with `service_url=SPOTLIGHT_ONLINE_API`.

In order to use REBEL just install the transformers library and import the tokenizer and model from `"Babelscape/rebel-large"`.

## Usage
The application has two interfaces: the web interface and the command line interface.

To run the web application just use the following command:
```console
streamlit run code/webapp/app.py
```

On the other hand, if you want to use the command line application use the following command:
```console
python3 code/app/app.py --input_text="code/app/input.txt" --all_sentences --save_debug
```

Both alternatives require three configuration files at your fingertips. These are the verb lexicalization table [`verb_prep_property_lookup.json`][4], the DBpedia class lexicalization table [`classes_lookup.json`][5] and the DBpedia ontology [`dbo_ontology_2021.08.06.owl`][10]. If there are any problems reading any of these files please modify the paths to these files as you see fit.

For more information visit [blog post 10][9] where the different arguments that exist when executing any interface are explained.

## Docker usage
This docker image will run the web application [`code/webapp/app.py`][11]. In order to use the Docker image with all the neccesary libraries installed, you should run the following command:
```bash
docker run -p 8501:8501 pablohdez98/dbpedia-abstracts-to-rdf:latest  # To run the web application
```
After that, open [localhost:8501][12] and you will see the web application.

## Future work (what is left to do after GSoC)
The main problem of the pipeline right now is that of all the triples it can generate, only half of them are free of errors in their structure. This kind of errors occur when the pipeline is unable to find a valid lexicalization for the predicate (verb+preposition) or for the object, leaving these elements as Literals instead of as resources or properties.
When we mention lexicalization we refer to the translation of text to URIs using tables for [properties][4] and [DBpedia classes][5].
As already seen during [blog post 9][6] the origin of most of these errors is when lexicalizing verbs and prepositions, since the current state of the lookup table does not cover the estimated number of cases.

Because of the above, the next step in the development of this tool would be to collaboratively add many more translations, so we will be able to cover many more cases and therefore generate more RDF triples.

Once many more lexicalizations are added we will be able to be stricter when generating RDF triples because at the moment there are also some errors associated with the content of the triple. This occurs when the range or domain of the RDF property does not match the classes of the resources in the subject and predicate. The reason for this error is again the fact that there are hardly any property lexicalizations at the moment.

Another future line of development to consider would be to support more languages such as Spanish, German, etc.

It would also be nice to implement a system to always have the lexicalization tables updated, so that each time the application is run it checks if these tables are in the latest possible version.

Finally, it would be desirable to define more patterns that encompass more types of subordinated sentences and compound sentences.

### Future work with REBEL
In this case we have completed a pipeline that is able to transform unstructured text into RDF triples more consistently and in greater quantity. However, there are some elements that are still pending and others that can be improved.

First, we need to create a way to evaluate the generated RDF triples. We have shuffled and tested with buying the range and property domain of each triple, as well as checking how many generated triples are already part of the network. Manual evaluation is probably necessary.

The model and the choice of hyperparameters can also be improved, as the results vary a lot depending on the choice of the main configuration. Generally a balance has to be found between generating few good quality triplets or many medium quality triplets.
Other methods of preparing the model input can also be explored. According to the author, a very good way to improve the results would be to develop a method that divides the text into fragments in an intelligent way.

On the lexicalization part, there is not much to do, since we are completely dependent on Dbpedia Spotlight and a manual association between the set of [relations generated by the model][15] and the [lexicalization table developed][16]. Perhaps one could fine tune the selection of Spotlight parameters and refine the lexicalization table.

Not every property is generated correctly from the set of properties. There are some cases in which we obtain a fraction of the property. (e.g. from 'position held' we obtain sometimes position). At the moment we have not identified the cause of this behaviour, maybe its from the model or maybe its from a step after the inference.

Finally, reviewing models such as [GenIE][17] can be very useful for the development of a close-information model. Where the generated triples are already constrained by the rules of the ontology, i.e. text/RDF triples that do not meet the constraints of the network cannot be generated.

## License
Copyright (C) Fernando Casabñan Blasco, 2021

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see http://www.gnu.org/licenses/.

[1]: https://summerofcode.withgoogle.com/projects/#6560166180290560
[2]: https://fcabla.github.io/DBpedia-abstracts-to-RDF/
[3]: https://github.com/Fcabla/DBpedia-abstracts-to-RDF/tree/main/code/codingweeks
[4]: https://github.com/Fcabla/DBpedia-abstracts-to-RDF/blob/main/datasets/verb_prep_property_lookup.json
[5]: https://github.com/Fcabla/DBpedia-abstracts-to-RDF/blob/main/datasets/classes_lookup.json
[6]: https://fcabla.github.io/DBpedia-abstracts-to-RDF/coding-week9
[7]: https://github.com/dbpedia-spotlight/dbpedia-spotlight/wiki/Run-from-a-JAR
[8]: https://github.com/Fcabla/DBpedia-abstracts-to-RDF/tree/main/spotlight
[9]: https://fcabla.github.io/DBpedia-abstracts-to-RDF/coding-week10
[10]: https://github.com/Fcabla/DBpedia-abstracts-to-RDF/blob/main/datasets/dbo_ontology_2021.08.06.owl
[11]: ./code/webapp/app.py
[12]: http://localhost:8501
[13]: https://hub.docker.com/r/dbpedia/dbpedia-spotlight
[14]: https://github.com/Fcabla/DBpedia-abstracts-to-RDF/blob/main/Rebel/doc.md
[15]: https://github.com/Babelscape/rebel/blob/main/data/relations_count.tsv
[16]: https://github.com/Fcabla/DBpedia-abstracts-to-RDF/blob/main/Rebel/lexicalization_properties.json
[17]: https://github.com/epfl-dlab/GenIE
