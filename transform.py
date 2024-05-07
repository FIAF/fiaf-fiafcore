
# script to collect FIAF resources into named graph.

import dotenv
import os
import pathlib
import pymongo
import rdflib
import requests

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
for x in ['fiaf.ttl', 'members.ttl', 'associates.ttl']:
    g.parse(pathlib.Path.cwd() / x)

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

# skolemize graph.

g = g.skolemize()

# connection details for graphdb.

graph_user, graph_pass = os.getenv('graph_username'), os.getenv('graph_password')
endpoint = 'http://37.27.26.36:7200/repositories/fiafkg/statements'
headers = {'Content-Type': 'application/sparql-update'}

# remove existing triples.

query = ''' delete {?s ?p ?o } where {?s ?p ?o} '''
r = requests.post(endpoint, headers=headers, data=query, auth=(graph_user, graph_pass))
if r.status_code != 204:
    raise Exception('Problem sending payload.')

# write new triples.

query = ''' insert data { '''+g.serialize(format='nt')+''' } '''
r = requests.post(endpoint, headers=headers, data=query.encode('utf-8'), auth=(graph_user, graph_pass))
if r.status_code != 204:
    raise Exception('Problem sending payload.')
