from collections import OrderedDict
from lxml import etree
from flask import Flask, request, Response, abort, app
import xmltodict
import json
import os
import logging
from git import Repo
from glob import glob

app = Flask(__name__)

logger = logging.getLogger('service')
working_dir = 'tmp_files'


class readXML:
    def __init__(self):
        self._entities = {
                "infrastructure": [],
                "track": [],
                "trackBegin": [],
                "openEnd": [],
                "trackEnd": [],
                "bufferStop": [],
                "mileageChange": [],
                "crossSection": [],
                "speedChange": [],
                "gradientChange": [],
                "radiusChange": [],
                "tunnel": [],
                "signal": [],
                "trainDetector": [],
                "stopPost": [],
                "line": [],
                "ocp": [],
                "propOperational": [],
                "geoCoord": [],
                "switch": [],
                "connection": [],
                "trackCircuitBorder": [],
                "balise": [],
                "crossing": []
                }

        self.resultList = []  # matched nodes from current source file
        self.parentIdList = []  # parent nodes for the matched nodes
        self.fileName = ""

    def get_entities(self, path, node):
        if not node in self._entities:
            abort(404)
        else:
            return self.read_file(path)

    def read_file(self, filename):
        filehandler = open(filename, "r")
        raw_data = etree.parse(filehandler)
        data_root = raw_data.getroot()
        filehandler.close()
        return data_root

    def findNodes(self, data, node):
        for child in data:
            if child.tag == '{http://www.railml.org/schemas/2013}%s' %node:
                self.resultList.append(child.attrib)
                self.findParentNode(data, child.attrib)
            self.findNodes(child, node)

    def findParentNode(self, data, attributes):
        for child in data:
            if child.attrib == attributes:
                parent = child.findall("..")

                while (len(parent[0].attrib) == 0):
                    parent = parent[0].findall("..")
                self.parentIdList.append(parent[0].attrib)

            self.findParentNode(child, attributes)

    def createXML(self, data, parentIdList, tag, filename):
        tagList = []
        counter = 0

        for element in data:
            child = etree.Element(tag)
            
            for k, v in element.items():
                child.attrib[k] = v
            
            parentids = parentIdList[counter]
            
            for key, val in parentids.items():
                child.attrib["parent_" + key] = val
            
            concat = "OT_" + filename

            if 'parent_id' in child.attrib:
                concat += "_" + child.attrib["parent_id"]
            if 'parent_name' in child.attrib:
                concat += "_" + child.attrib["parent_name"]
            if 'id' in child.attrib:
                concat += "_" + child.attrib["id"]
            if 'name' in child.attrib:
                concat += "_" + child.attrib["name"]

            child.attrib['_id'] = concat
            child.attrib['infrastructure_name'] = filename
            counter += 1
            
            tagList.append(child)

        return tagList

# ============================================================


# removed @ from attribute names
def remover(x):
    if isinstance(x, list):
        return [remover(y) for y in x]

    elif isinstance(x, OrderedDict):
        for ky in list(x.keys()):
            if ky[0] in ["@", ""]:
                x[ky[1:]] = remover(x[ky])
                del x[ky]
            else:
                x[ky] = remover(x[ky])
        return x
    else:
        return x


def to_json(data):
    dumplist = []
    for k ,v in data.items():
        for l in v:
            dumplist.append(l)
    dump = json.dumps(dumplist)
    return dump


# ============================================================

data_access_layer = readXML()


@app.route('/<datatype>')
def get_entities(datatype):
    sync_repo()

    path = "%s/%s" % (working_dir, os.environ["FILE_PATTERN"])
    tagList = []

    files = glob(path)

    for f in files:
        current_file = readXML()
        src_xml = current_file.get_entities(f, datatype)
        
        for child in src_xml:
            if child.tag == '{http://www.railml.org/schemas/2013}%s' % 'infrastructure':
                current_file.fileName = child.attrib['name']

        current_file.findNodes(src_xml, datatype)
        tagList += current_file.createXML(current_file.resultList, current_file.parentIdList, datatype, current_file.fileName)
        
    root = etree.Element('root')
    for tag in tagList:
        root.append(tag)

    root = etree.tostring(root, encoding='utf-8')

    toDict = xmltodict.parse(root.decode("utf-8"))
    outAsJson = remover(toDict['root'])
    json = to_json(outAsJson)

    return Response(json, mimetype='application/json', )


def sync_repo():
    ssh_cmd = 'ssh -o "StrictHostKeyChecking=no" -i /id_deployment_key'
    if not os.path.exists(working_dir):
        repo_url = os.environ['GIT_REPO']
        logger.info('cloning %s', repo_url)
        Repo.clone_from(repo_url, working_dir, env=dict(GIT_SSH_COMMAND=ssh_cmd))
    else:
        repo = Repo(working_dir)
        with repo.git.custom_environment(GIT_SSH_COMMAND=ssh_cmd):
            logger.info('fetching %s origin')
            repo.remotes.origin.fetch()

if __name__ == '__main__':
#    path = 'testfiles/*'
#    datatype = 'signal'
#
#    tagList = []
#
#    files = glob(path)
#
#    for f in files:
#        current_file = readXML()
#        src_xml = current_file.get_entities(f, datatype)
#        
#        for child in src_xml:
#            if child.tag == '{http://www.railml.org/schemas/2013}%s' % 'infrastructure':
#                current_file.fileName = child.attrib['name']
#
#        current_file.findNodes(src_xml, datatype)
#        tagList += current_file.createXML(current_file.resultList, current_file.parentIdList, datatype, current_file.fileName)
#        
#    root = etree.Element('root')
#    for tag in tagList:
#        root.append(tag)
#
#    root = etree.tostring(root, encoding='utf-8')
#
#    toDict = xmltodict.parse(root.decode("utf-8"))
#    outAsJson = remover(toDict['root'])
#    json = to_json(outAsJson)
#    print ("json:\n%s" % json)

    with open("id_deployment_key", "w") as key_file:
        key_file.write(os.environ['SSH_PRIVATE_KEY'])
    os.chmod("/id_deployment_key", 0o600)

    app.run(debug=True, host='0.0.0.0')
