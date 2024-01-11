from os import walk
# from ruamel.yaml import YAML
from difflib import *
from pathlib import Path
import yaml
import sys

def getDescription(schema):
    """ Return the `description` value of a schema or False """
    try:
        return schema["description"]
    except:
        return False

def processSchema(kind, schema):
    """Process a CRD schema. Returns a dict of {<key>: <description>}"""

    # Standard Kubernetes object keys to ignore
    excludedKeys = ["metadata", "apiVersion", "kind", "metadata", "additionalProperties"]
    output = {}

    if "items" in schema.keys():
        output[kind] = getDescription(schema)

        # If the child element is a list
        if "properties" in schema["items"]:
            for item in schema["items"]["properties"]:
                output.update(processSchema(kind + ".items.properties." + item, schema["items"]["properties"][item]))
    else:
        output[kind] = getDescription(schema)

    if "properties" in schema:
        if "spec" in schema["properties"]:
            # Child element is an object
            output.update(processSchema(kind + ".spec", schema["properties"]["spec"]))
        else:
            for key in schema["properties"]:
                if key in excludedKeys:
                    # Skip standard Kubernetes keys
                    continue
                output.update(processSchema(kind + "." + key, schema["properties"][key]))

    return output

def parseCRDFile(yamlFile):
    """Given a CRD file path return the active schema"""

    with open(yamlFile, 'r') as file:
        f = yaml.safe_load(file)

    kind = f["spec"]["names"]["kind"]

    for version in f["spec"]["versions"]:
        if not version["storage"]:
            continue

        schema = version["schema"]["openAPIV3Schema"]
        return {"kind": kind, "schema": schema}

def getFiles(inputDir):
    """Given a directory, return the list of files it contains, excluding subdirectories"""

    fileNames = []

    for (path, dir, file) in walk(inputDir):
        fileNames.extend(file)

    return fileNames

def writeDescriptions(crdDir, descDir):
    """ Read in a directory of CRDs and generate unique description markdown files. """

    # Ensure both source and destinations are directories
    if not crdDir[:-1] == "/":
        crdDir = crdDir + "/"

    if not descDir[:-1] == "/":
        descDir = descDir + "/"

    files = getFiles(crdDir)

    for crdFile in files:
        crd = parseCRDFile(crdDir + crdFile)
        crdDescription = processSchema(crd["kind"], crd["schema"])
        crdDirName = crdFile[:-5]

        for key,desc in crdDescription.items():
            descFile = crdDirName + key + ".md"
            Path(descDir + crdDirName).mkdir(parents=True, exist_ok=True)
            truncated = False

            # Deep keys or long property names can generate filenames too long for an OS
            # This truncates long names to be <kind>.spec.forP.... (for characters from each field)
            if len(descFile) > 200:
                print(crdFile)
                truncated = True
                descParts = (descFile + key).split(".")
                path = descParts[0]
                descPartsCounter = 0
                tempName = []

                for part in descParts:
                    if descPartsCounter < 1:
                        descPartsCounter += 1
                        continue

                    if len(tempName) == len(descParts) - 1:
                        tempName.append(part)
                    else:
                        tempName.append(part[:4])

                descFile = path + "." + ".".join(tempName)

            with open(descFile, 'w') as f:
                f.write("<!-- source: " + crdFile + " -->\n")
                if truncated:
                    f.write("<!-- kind: " + key + " -->\n") # Write the full path in the file if the filename is truncated
                if not desc:
                    print("Missing Description: " + descFile)
                    f.write("")
                else:
                    f.write(desc)

def compareDescriptions(crdFile, descDir):

    crd = parseCRDFile(crdFile)
    crdDescriptions = set(processSchema(crd["kind"], crd["schema"]).keys())
    descFilesSet = set()
    diffs = False

    for file in getFiles(descDir):
        key = file.split(".")[0]
        noSuffixFile = file[:-3]    # Remove .md suffix

        if key == crd["kind"]:
            descFilesSet.add(noSuffixFile)

    # try:
    crdDiff = crdDescriptions.difference(descFilesSet)

    if crdDiff:
        diffs = True
        print("Missing description files:")
        for desc in crdDiff:
            print("\t" + desc)
        print("")

    descDiff = descFilesSet.difference(crdDescriptions)

    if descDiff:
        diffs = True
        print("Description files without matching CRD descriptions:")
        for desc in descDiff:
            print("\t" + desc)
        print("")

    # Exit 0 if no diffs
    # Exit 1 if diffs
    exit(int(diffs))



def main():

    #crdDir = "/Users/plumbis/git/crossplane-docs/content/v1.14/api/crds/"
    crdDir = "/Users/plumbis/git/provider-aws/package/crds/"
    descDir = "/Users/plumbis/git/provider-aws/descriptions"


    writeDescriptions(crdDir, descDir)
    # compareDescriptions(
    #                      "/Users/plumbis/git/provider-aws/package/crds/descriptions/DataCatalogEncryptionSettings/DataCatalogEncryptionSettings.spec.forP.data.item.prop.conn.item.prop.awsK")
    # compareDescriptions("/Users/plumbis/git/crossplane-docs/content/v1.14/api/crds/apiextensions.crossplane.io_compositeresourcedefinitions.yaml", descDir)

if __name__ == "__main__":
    main()

