FROM python:3.9-slim

WORKDIR /DBpedia-abstracts-to-RDF

COPY code/webapp code
COPY datasets/classes_lookup.json datasets/verb_prep_property_lookup.json datasets/dbo_ontology_2021.08.06.owl datasets/
COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt && \
python -m spacy download en_core_web_trf && \
python -m spacy download en_core_web_lg && \
python -m coreferee install en && \
rm -rf /root/.cache

EXPOSE 8501

CMD ["streamlit", "run", "code/app.py"]