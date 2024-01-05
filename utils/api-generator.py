import argparse
import yaml
from os import walk

def getDescription(spec, key):

    output = []

    output.append("  " + key + ".description: ")

    try:
        output.append("    " + spec["description"])
    except:
        output.append("    *****MISSING***** ")

    output.append("")

    return output

def processSpec(spec, keyString, root=False):

    excludedKeys = ["metadata", "apiVersion", "kind", "metadata", "additionalProperties"]
    output = {}

    if "items" in spec.keys():
        output.extend(getDescription(spec, keyString))

        if "properties" in spec["items"]:
            for item in spec["items"]["properties"]:
                output.extend(processSpec(spec["items"]["properties"][item], keyString + ".items.properties." + item))
    else:
        output.extend(getDescription(spec, keyString))

    if "properties" in spec:
        if "spec" in spec["properties"]:
            output.extend(processSpec(spec["properties"]["spec"], keyString + ".spec"))
        else:
            for key in spec["properties"]:
                if key in excludedKeys:
                    continue
                output.extend(processSpec(spec["properties"][key], keyString + "." + key, ))

    return output

def parseCRDFile(yamlFile):
    with open(yamlFile, 'r') as file:
        f = yaml.safe_load(file)

    name = f["metadata"]["name"]
    kind = f["spec"]["names"]["kind"]
    output = []

    for version in f["spec"]["versions"]:
        if not version["storage"]:
            continue

        schema = version["schema"]["openAPIV3Schema"]
        output.append("kind: " + kind)
        output.extend(processSpec(schema, keyString=kind, root=True))

    return output

def loadCRDs(inputDir, outputFile):
    yamlFiles = []
    crdDescriptions = {}

    for (dirpath, dirnames, filenames) in walk(inputDir):
        yamlFiles.extend(filenames)

    for yamlFile in yamlFiles:
        crdDescriptions[yamlFile] = parseCRDFile(inputDir + yamlFile)

    print(crdDescriptions)

def writeDescriptions(crds, destFile):
    newYaml = {}

    # for file,output in crds.items():
    #     newYaml[file] = {}
    #     for line in output:

    #     # f.write("file: " + file + "\n")
    #     # for line in output:
    #     #     f.write(line + "\n")
    #     # f.write("\n")

    # with open(destFile, "w") as f:
    # f.close()

def compareDescriptions(descriptionFile):
    pass
    rawDescriptions = []
    with open(descriptionFile, 'r') as f:
        rawDescriptions = f.readlines()
    f.close()

    crdDescriptions = {}
    file = ""
    kind = ""

    for line in rawDescriptions:
        thisLine = line.strip()
        if thisLine.lower.startswith("file"):
            file = thisLine.split(":")[1].strip()
            continue

        if thisLine.lower.startswith("kind"):
            kind = thisLine.split(":")[1].strip()
            continue



def main():

    crdDir = "/Users/plumbis/git/crossplane-docs/content/v1.14/api/crds/"
    docsDir = ""

    crdDescriptions = loadCRDs(crdDir, ".")

    writeDescriptions(crdDescriptions, "./descriptions.yaml")

    compareDescriptions("./descriptions.yaml")


if __name__ == "__main__":
    main()

