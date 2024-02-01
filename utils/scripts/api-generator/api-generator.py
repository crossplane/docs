#!/usr/bin/env python3

import argparse
import os
from os import walk
from pathlib import Path

import yaml

verbose = False


def mapDescriptions(data, sep=".", _prefix="", keys=None, writeEmpty=False):
    # Inspired by https://github.com/fa1zali/yaml_keygen

    if keys is None:
        keys = []

    # Keys to universally ignore
    # Defer more specific key filtering to the output consumer.
    excludedKeys = set(("additionalProperties", "required"))

    if isinstance(data, dict):
        prefixParts = _prefix.split(sep)

        if len(prefixParts) == 3:  # e.g., <kind>.properties.spec
            key = prefixParts[2]
            if key == "spec":
                desc = False
                try:
                    keys.append({f"{_prefix}{sep}description": data["description"]})
                except KeyError:
                    if writeEmpty:
                        keys.append({f"{_prefix}{sep}description": ""})
            if key == "status":
                return keys

        # write the description before iterating to make it easier to determine if an object is missing a description
        elif "description" in data.keys() or writeEmpty:
            if "description" in data.keys():
                desc = data["description"]
            else:
                desc = ""
            # "properties" never has a description and shouldn't have one.
            if not prefixParts[len(prefixParts) - 1] == "properties":
                keys.append({f"{_prefix}{sep}description": desc})

        for k, v in data.items():
            # Ignore "type" when it defines a datatype, but it can also be a valid spec parameter
            if k == "type" and not isinstance(data[k], dict):
                continue

            # Always skip known keys
            elif k in excludedKeys:
                continue

            tmpString = f"{_prefix} {k}".strip().split(" ")
            mapDescriptions(v, sep, ".".join(tmpString), keys, writeEmpty=writeEmpty)

    return keys


def processSchema(kind, schema, writeEmpty=True):
    """Process a CRD schema. Returns a list of description keys}

    kind - root schema Key, CRD "kind".
    schema - YAML schema to process
    """

    return mapDescriptions(schema, _prefix=kind, writeEmpty=writeEmpty)


def parseCRDFile(yamlFile):
    """Given a CRD file path return the active schema"""

    with open(yamlFile, "r") as file:
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

    for path, dir, file in walk(inputDir):
        fileNames.extend(file)

    return fileNames


def removeProperties(key):
    """
    Given a string of
        x.y.properties.z.properties
    Remove all instances of "properties" and reassemble the string.
    """

    splitKey = key.split(".")
    if len(splitKey) > 4:
        # delete <kind>.properties.spec.properties
        del splitKey[:3]

    splitKey = list(filter(lambda a: a != "properties", splitKey))
    key = ".".join(splitKey)

    return key


def getTruncatedName(fileName, truncateTo=6):
    parts = fileName.split(".")
    tempName = []

    # Preserve the first key
    tempName.append(parts[0])

    for part in parts[2:]:
        # Preserve the final key
        if len(tempName) == len(parts) - 1:
            tempName.append(part)
        else:
            tempName.append(part[:truncateTo])

    newName = ".".join(tempName)

    # If the new name is still too long and we can truncate further, try it
    if len(newName) > 200 and truncateTo > 1:
        getTruncatedName(newName, truncateTo=truncateTo - 1)

    return newName


def writeDescriptions(crdDir, descDir):
    """Read in a directory of CRDs and generate unique description markdown files."""

    verbose = True

    files = getFiles(crdDir)

    # Ensure both source and destinations are directories
    if not crdDir[-1] == "/":
        crdDir = crdDir + "/"

    if not descDir[-1] == "/":
        descDir = descDir + "/"

    totalDescriptions = 0

    for crdFile in files:
        crdDescriptions = {}
        crd = {}
        crdDirName = ""
        keySet = set()
        if verbose:
            print(f"\nParsing file {crdFile}")

        crd = parseCRDFile(crdDir + crdFile)
        crdDescriptions = processSchema(crd["kind"], crd["schema"])
        crdDirName = descDir + crdFile[:-5] + "/"  # Drop ".yaml"
        Path(crdDirName).mkdir(parents=True, exist_ok=True)

        if verbose:
            print(f"Found {len(crdDescriptions)} keys to process")
            totalDescriptions += len(crdDescriptions)

        for item in crdDescriptions:
            for key in item.keys():
                originalKey = key

                key = removeProperties(key)

                # Deep keys or long property names can generate filenames too long for an OS
                # This truncates long names to be <kind>.spec.forP.blah... (for characters from each field)
                truncated = False
                if len(key) > 200:
                    truncated = True

                    key = getTruncatedName(key)

                    if verbose:
                        print(f"\nTruncating \n\t{originalKey} \nto \n\t{key}")

                    if len(key) > 250:
                        print("Error:")
                        print(f"\tLength of {crdFile} key")
                        print("\t{oldDesc}")
                        print("\tis too long to process")
                        exit(1)

                    if key in keySet:
                        print("Warning:")
                        print(f"\CRD file {crdFile} key")
                        print(f"\t{originalKey}")
                        print("\tmatches an existing key.")
                        if truncated:
                            print("\tPossible truncated key conflict:")
                            print(f"\t{key}")

                with open(crdDirName + key + ".md", "w") as f:
                    f.write(f"<!-- kind: {originalKey} -->\n {item[originalKey]}")

    if verbose:
        print("\n")

    print(f"Wrote {totalDescriptions} descriptions from {len(files)} files.")


def compareDescriptions(crdFile, descDir):
    if verbose:
        print(f"Comparing CRD files\n\t{crdFile}\n\t{descDir}\n\t")

    diffs = False

    crd = parseCRDFile(crdFile)
    crdDescriptions = set()

    for item in processSchema(crd["kind"], crd["schema"], writeEmpty=False):
        for k in item.keys():
            crdDescriptions.add(k)

    descFiles = set()
    descSubDir = os.path.basename(crdFile.split(".yaml")[0])
    filenameMap = {}

    # The crdFile path is the same name as the directory for the description files
    for descFile in getFiles(descDir + "/" + descSubDir):
        with open(descDir + "/" + descSubDir + "/" + descFile, "r") as f:
            line = f.readline()
            try:
                # split on "--", get "kind: <kind>.properties.spec..."
                # strip and split on "kind:" to get the path string
                kind = line.split("--")[1].strip().split("kind:")[1].strip()
                descFiles.add(kind)
                filenameMap[kind] = descFile
            except IndexError:
                print("Warning: unable to determine description endpoint.")
                print(f"\t{descFile}")

    # try:
    crdDiff = crdDescriptions.difference(descFiles)
    descDiff = descFiles.difference(crdDescriptions)

    if crdDiff:
        diffs = True
        print("CRD keys missing description files:")
        for desc in crdDiff:
            print(f"\t{desc}")
        print("")

    if descDiff:
        diffs = True
        print("Description files without matching CRD descriptions:")
        for desc in descDiff:
            print(f"\t{descDir}/{descSubDir}/{filenameMap[desc]}")
        print("")

    return diffs


def cliArguments():
    global verbose

    parser = argparse.ArgumentParser(
        description="Generate and diff markdown description files from Kubernetes CRDs."
    )

    actionGroup = parser.add_mutually_exclusive_group()
    actionGroup.add_argument(
        "-w",
        "--writeDescriptions",
        action="store_true",
        help="Overwrite existing markdown files",
    )
    actionGroup.add_argument(
        "-d",
        "--diff",
        action="store_true",
        help="Find missing or extra markdown description files.",
    )

    parser.add_argument(
        "-crd",
        "--crdPath",
        metavar="<file or path>",
        type=str,
        nargs=1,
        required=True,
        help="CRD file or directory.",
    )

    parser.add_argument(
        "-desc",
        "--descriptionDirectory",
        metavar="<path>",
        type=str,
        nargs=1,
        required=True,
        help="Directory of markdown description files.",
    )

    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Print verbose logging"
    )

    args =  parser.parse_args([
        "-d",
        '-crd',
        '/Users/plumbis/git/crossplane-docs/content/v1.14/api/crds',
        '-desc',
        '/Users/plumbis/git/crossplane-docs/content/v1.14/api/descriptions',
        '-v'
    ])
    #args = parser.parse_args()

    # verbose = args.verbose
    errors = False
    crdPath = args.crdPath[0]
    descDir = args.descriptionDirectory[0]


    # Paths can't match
    if crdPath == descDir:
        print("Error: CRD path and description directory can't be the same path")
        exit(1)

    # Valiate that the file/directories exist
    crdExists = os.path.exists(crdPath)
    descExists = os.path.exists(descDir)

    if not crdExists:
        print(f"Error: Can't find CRD path {crdPath}")
        errors = True

    if not descExists:
        print(f"Error: Can't find description directory {descDir}")
        errors = True
    elif not os.path.isdir(descDir):
        print("Error: Description path must be a directory")
        errors = True

    # CRD input must be a directory with -w
    if args.writeDescriptions and not os.path.isdir(crdPath):
        print("Error: CRD path must be a directory with -w")
        errors = True

    if errors:
        exit(1)
    else:
        return {
            "write": args.writeDescriptions,
            "diff": args.diff,
            "crd": crdPath,
            "desc": descDir,
        }


def main():
    args = cliArguments()

    if verbose:
        print(f"Arguments: {args}")
        print()

    if args["write"]:
        if verbose:
            print("Writing descriptions...\n")
        writeDescriptions(args["crd"], args["desc"])

    if args["diff"]:
        if verbose:
            print("Comparing descriptions...\n")

        if os.path.isdir(args["crd"]):
            crdFiles = getFiles(args["crd"])
            for crd in crdFiles:
                hasDiffs = compareDescriptions(args["crd"] + "/" + crd, args["desc"])

                if hasDiffs:
                    exit(1)
        else:
            exit(compareDescriptions(args["crd"], args["desc"]))


if __name__ == "__main__":
    main()
