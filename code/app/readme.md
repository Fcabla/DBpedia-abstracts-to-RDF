# App (command line script)

Command line application to transform text to RDF triples. The program accepts the following arguments:

```console
fcabla@fcabla-MS-7C56:~/Documents/GSoc/DBpedia-abstracts-to-RDF$ python3 code/app/app.py --help
usage: app.py [-h] --input_text INPUT_TEXT [--text_triples] [--save_debug]

Text to RDF parser

optional arguments:
  -h, --help displays this help message and exits.
  --input_text INPUT_TEXT Insert abstract text or any other type to generate RDF based on the input
  --text_triples Print the simplified statements of the triples that have been generated. This is useful for understanding how the pipeline processed the input
  --save_debug Prints the text triples and the extracted RDF triples for each sentence.
```

An example of the program execution would be the following:
```console
python3 code/app/app.py --input_text="code/app/input.txt" --text_triples --save_debug
```
