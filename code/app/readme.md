# App (command line script)

Command line application to transform text to RDF triples. The program accepts the following arguments:

```console
fcabla@fcabla-MS-7C56:~/Documents/GSoc/DBpedia-abstracts-to-RDF$ python3 code/app/app.py --help
usage: app.py [-h] --input_text INPUT_TEXT [--all_sentences] [--text_triples] [--no_literals] [--save_debug] [--save_debug]

Text to RDF parser

optional arguments:
  -h, --help displays this help message and exits.
  --input_text INPUT_TEXT
                        Insert abstract text or any other type to generate RDF based on the input
  --all_sentences Use all sentences of the abstract or only the simplest sentences (False recommended)
  --text_triples Print the simplified statements of the triples that have been generated. This is useful for understanding how the pipeline processed the input
  --no_literals Discards all triples containing a literal. This occurs when the pipeline cannot find any lexicalization for the predicate or the object
  --save_debug Prints the text triples and the extracted RDF triples for each sentence.
```

An example of the program execution would be the following:
```console
python3 code/app/app.py --input_text="code/app/input.txt" --all_sentences --save_debug
```

For more information please refer to the [blog post 10](https://fcabla.github.io/DBpedia-abstracts-to-RDF/coding-week10)