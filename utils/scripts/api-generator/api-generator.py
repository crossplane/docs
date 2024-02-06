#!/usr/bin/env python3

import argparse
import os
from os import walk
from pathlib import Path

import yaml

verbose = False


def mapDescriptions(data: any, sep: str = ".", _prefix: str = "", keys:list = None, writeEmpty: bool = False) -> list:
    """ Recursively process the data object and grab all "x.description" keys """
    # Inspired by https://github.com/fa1zali/yaml_keygen

    if keys is None:
        keys = []

    # Keys to universally ignore
    # Defer more specific key filtering to the output consumer.
    excludedKeys = set(("additionalProperties", "required"))
    if _prefix == "CompositeResourceDefinition.properties.spec.properties.versions.items.properties.additionalPrinterColumns.items.properties":
        pass

    if isinstance(data, dict):
        prefixParts = _prefix.split(sep)

        if len(prefixParts) == 3:  # e.g., <kind>.properties.spec
            key = prefixParts[2]
            if key == "spec" or key == "status":
                desc = False
                try:
                    keys.append({f"{_prefix}{sep}description": data["description"]})
                except KeyError:
                    if writeEmpty:
                        keys.append({f"{_prefix}{sep}description": ""})

        else:
            writeDesc = False

            try:
                if not isinstance(data["description"], dict):
                    desc = data["description"]
                    writeDesc = True
            except (KeyError,TypeError):
                if writeEmpty:
                    desc = ""
                    writeDesc = True

            if writeDesc:
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


def processSchema(kind: str, schema: dict, writeEmpty: bool = True) -> dict:
    """Process a CRD schema. Returns a list of description keys}

    kind - root schema key. The CRD "kind".
    schema - dict schema from YAML to process
    writeEmpty - if a key doesn't have a description, create a description key if True anyway.
    """

    return mapDescriptions(schema, _prefix=kind, writeEmpty=writeEmpty)


def parseCRDFile(yamlFile: str) -> dict:
    """Given a string path to a CRD YAML file return a dict of:
    kind: String of the CRD kind
    version: String of the active (storage=True) version
    schema: Dict of the entire active CRD schema
    """

    with open(yamlFile, "r") as file:
        f = yaml.safe_load(file)

    kind = f["spec"]["names"]["kind"]
    group = f["spec"]["group"]

    for version in f["spec"]["versions"]:
        if not version["storage"]:
            continue

        schema = version["schema"]["openAPIV3Schema"]
        return {"group": group, "kind": kind, "schema": schema, "version": version["name"]}


def getFiles(inputDir: str) -> list:
    """Given a string directorypath, return the list of files it contains, excluding subdirectories"""

    fileNames = []

    for path, dir, file in walk(inputDir):
        fileNames.extend(file)

    return fileNames


def writeDescriptions(crdDir: str, descDir: str) -> None:
    """Read in a directory of CRDs and generate unique description markdown files."""

    verbose = True
    totalDescriptions = 0

    files = getFiles(crdDir)

    # Ensure both source and destinations are directories
    if not crdDir[-1] == "/":
        crdDir = crdDir + "/"

    if not descDir[-1] == "/":
        descDir = descDir + "/"

    for crdFile in files:
        if verbose:
            print(f"\nParsing file {crdFile}")

        crd = parseCRDFile(crdDir + crdFile)

        crdDescriptions = processSchema(crd["kind"], crd["schema"])
        crdGroupDir = f"{descDir}{crd['group']}"
        crdKindDir = f"{crdGroupDir}/{crd['kind']}"

        Path(crdKindDir).mkdir(parents=True, exist_ok=True)

        if verbose:
            print(f"Found {len(crdDescriptions)} keys to process")
            totalDescriptions += len(crdDescriptions)

        for item in crdDescriptions:
            for key in item.keys():
                if len(key.split(".")) > 2:
                    # Remove the ending "/description" to get the destination directory path
                    targetDir = f"{crdGroupDir}/{key.replace('.', '/')[:-len('/description')]}"
                    Path(targetDir).mkdir(parents=True, exist_ok=True)
                else:
                    targetDir = crdKindDir

                with open(f"{targetDir}/description.yaml", "w") as f:
                    try:
                        f.write("description:\n")
                        f.write(f"    {item[key]}")
                    except KeyError:
                        f.write("description:")

                totalDescriptions += 1

    if verbose:
        print("\n")

    print(f"Wrote {totalDescriptions} descriptions from {len(files)} files.")


def compareDescriptions(crdFile: str, descDir: str) -> bool:
    if verbose:
        print(f"Comparing CRD files\n\t{crdFile}\n\t{descDir}\n\t")

    diffs = False

    # Process the CRD file and add each description key to a set
    crdDescriptions = set()
    crd = parseCRDFile(crdFile)
    for item in processSchema(crd["kind"], crd["schema"], writeEmpty=False):
        for k in item.keys():
            crdDescriptions.add(k)

    fileDescriptions = set()

    # Determine the subdirectories from the original CRD file.
    crdGroupDir = f"{descDir}/{crd['group']}"
    crdKindDir = f"{crdGroupDir}/{crd['kind']}"

    crdKindPath = Path(crdKindDir)

    yamlFiles = list(crdKindPath.glob("**/*.yaml"))

    for description in yamlFiles:
        # remove the parent directory
        # split on the filename suffix to remove it
        # Replace the directory "/" with "."
        fileDescriptions.add(
            str(description).split(crdGroupDir)[1].split(description.suffix)[0].lstrip("/").replace("/",".")
        )

    # try:
    crdDiff = crdDescriptions.difference(fileDescriptions)
    fileDiff = fileDescriptions.difference(crdDescriptions)

    if crdDiff:
        diffs = True
        print("CRD keys missing description files:")
        for desc in crdDiff:
            descAsPath = desc.replace(".","/")
            print(f"\t{crdGroupDir}/{descAsPath}.yaml")
        print("")

    if fileDiff:
        # If there are CRDs without description fields, that's not an error.
        if verbose:
            print("Description files without matching CRD descriptions:")
            for desc in fileDiff:
                descAsPath = desc.replace(".","/")
                print(f"\t{crdGroupDir}/{descAsPath}.yaml")
            print("")

    if not diffs:
        print(f"No diffs between \n{crdFile} and \n{descDir}\n")

    return diffs


def cliArguments() -> dict:
    """
    Build the CLI arguments and return the arguments and values.
    """

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

    args = parser.parse_args()

    verbose = args.verbose
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
