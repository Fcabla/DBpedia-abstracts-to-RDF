import requests, re, glob
import os

# More info in https://archivo.dbpedia.org/api
POM_FILE_LATEST_ONTOLOGY = "https://akswnc7.informatik.uni-leipzig.de/dstreitmatter/archivo/dbpedia.org/ontology/pom.xml"
ARCHIVO_ONTOLOGY_ONLINE_API = "https://archivo.dbpedia.org/download?o=http://dbpedia.org/ontology/&f=owl"
local_ontology_path = 'datasets/'

def get_latest_ontology_filename():
    # get pom.xml which includes the name of latest ontology file
    try:
        resp = requests.get(POM_FILE_LATEST_ONTOLOGY)
    except:
        print("Error at https://akswnc7.informatik.uni-leipzig.de/dstreitmatter/archivo")
        return None

    if resp.status_code != 200:
        print(f"error, status code{resp.status_code}")
        return None

    # name of latest ontology file with format 2022.06.30-XXXXXX between tags <version></version>
    pos = re.search("<version>202\d\.(0?[1-9]|1[012])\.(0?[1-9]|[1-2]\d|3[0-1])-\d{6}</version>",resp.text)
    if pos:
        fullname = resp.text[pos.regs[0][0] + 9: pos.regs[0][1] - 10] # remove tags <version> and </version>
        date = fullname[:-7] # remove timestamp from the filename
    else:
        print('Unable to get date of the latest ontology file from POM.XML file')
        return None

    return date

def update_ontology_file():
    date = get_latest_ontology_filename()
    if date is not None:
        # Local files ending with .owl
        local_ontology = glob.glob(local_ontology_path + '*.owl')
        names = [os.path.basename(x) for x in local_ontology]

        # Check if the date of the latest ontology is included in the name of the local ontology file
        for file in names:
            if file.find(date) >= 0:
                return False, "Local DBpedia ontology doesn't need to be updated"

        # Download the latest ontology file
        try:
            print("Local DBpedia ontology is being updated. Please wait...")
            headerinfo = {'Accept': 'application/rdf+xml'}
            resp2 = requests.get(ARCHIVO_ONTOLOGY_ONLINE_API, headers=headerinfo)
        except:
            return False, "Error at DBpedia Archivo post/get"

        if resp2.status_code != 200:
            print(f"error, status code{resp2.status_code}")
            return False, "Error at DBpedia Archivo post/get"

        # Write downloaded content in a local file with name 'dbo_ontology_date.owl'
        new_ontology = local_ontology_path + 'dbo_ontology_' + date + '.owl'
        open(new_ontology, "wb").write(resp2.content)
        return True, "New DBpedia ontology file saved " + new_ontology
    return False, "Unable to download DBpedia ontology, problems to locate pom.xml file"