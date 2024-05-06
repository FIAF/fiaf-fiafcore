
# script to collect FIAF resources into named graph.

import dotenv
import os
import pathlib
import pymongo
import rdflib
import ssl

def wikidata_identifier(f, w):

    ''' Formulate Wikidata triples to match FIAFcore identifier structure. '''

    graph = rdflib.Graph()

    bnode = rdflib.BNode()
    graph.add((rdflib.URIRef(f), rdflib.URIRef('https://ontology.fiafcore.org/hasIdentifier'), bnode))
    graph.add((bnode, rdflib.URIRef('https://ontology.fiafcore.org/hasIdentifierValue'), rdflib.Literal(w)))
    graph.add((bnode, rdflib.URIRef('https://ontology.fiafcore.org/hasIdentifierAuthority'), rdflib.URIRef('https://ontology.fiafcore.org/Wikidata')))

    return graph

# load local turtle files.

g = rdflib.Graph()
g.parse(pathlib.Path.cwd() / 'fiaf.ttl')

# pull wikidata identifiers from mongo atlas.

dotenv.load_dotenv()
atlas_user, atlas_pass = os.getenv('atlas_username'), os.getenv('atlas_password')
client = pymongo.MongoClient(f'mongodb+srv://{atlas_user}:{atlas_pass}@fiafcore.wrscui9.mongodb.net/?retryWrites=true&w=majority&appName=fiafcore')
collection = client['fiafcore']['auth']

# add wikidata identifiers where appropriate.

for s,p,o in g.triples((None, rdflib.RDF.type, rdflib.URIRef('https://ontology.fiafcore.org/CorporateBody'))):

    results = collection.find({ 'fiafcore': str(s) })
    for res in results:
        fiaf = res['fiafcore']
        for wiki in res['local']:
            if 'wikidata' in wiki:
                wiki = pathlib.Path(wiki).name
                g += wikidata_identifier(fiaf, wiki)

# add ontology

# dump turtle file, bonus points for insert sparql direct to graphdb as named graph.

# name for graph is https://graph.fiafcore.org/graphs/fiaf