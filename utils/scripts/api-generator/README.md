# CRD to Markdown Docs Generator

The `api-generator` script reads parses YAML files representing Kubernetes CRDs 
and extracts each key field and their related descriptions. 

The script supports a `-w` write mode to generate new Markdown files and 
`-d` diff mode to show any CRD keys missing associated description markdown
files or show any markdown files that don't map to an associated CRD description. 

## Install

Install the prerequisites for the script:

### Install pipx
sudo apt update
sudo apt install pipx

### Install poetry
pipx install poetry


### Install pyyaml
poetry install --no-root

### Run the script
python3 ./api-generator.py

## Writing markdown files

To generate new markdown files use the `-w` argument. 

```shell
 api-generator.py -w -crd <file or path> -desc <path>
```

The `-w` argument takes a directory of containing CRD YAML files with the 
`-crd` argument and the destination directory to write Markdown files to with 
`-desc`.

The script looks through each CRD looking for the `description` field of each 
key inside the `.schema.openAPIV3Schema` section of the `spec`, except the 
`properties` keys. 

The script creates a directory matching the CRD filename and writes a single 
markdown file for each description. The script copies the `description` from the 
CRD key into the markdown file. If the CRD key doesn't have a `description` the 
script creates an empty markdown file. 

This example of a CompositeResourceDefinition file named
`apiextensions.crossplane.io_compositeresourcedefinitions.yaml` 
would generate the following:

* A directory named `apiextensions.crossplane.io_compositeresourcedefinitions/`
* Description files:
  * `CustomResourceDefinition.md` - There's no `openAPIV3Schema.description` field. The script generates an empty markdown file. 
  * `CustomResourceDefinition.spec.md` - The description of the `spec` field. The script puts "The spec's description." into the markdown file.
  * `CustomResourceDefinition.spec.claimNames.md` - The description of `spec.properties.claimNames`, "This is a claimName."
  * `CustomResourceDefinition.spec.claimNames.categories.md` - "Claims can have a category."
```yaml
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
spec:
  group: apiextensions.crossplane.io
  versions:
    schema:
      openAPIV3Schema:
        properties:
          spec:
            description: The spec's description.
            properties:
              claimNames:
                description: This is a claimName.
                properties:
                  categories:
                    description: Claims can have a category.
# Removed for brevity
```

### Long keys

The script generates the markdown filename from a subset of the keys.

For long key names or deep nested keys the filenames may be too long. The 
script truncates filenames over 200 characters by first trying to trim all keys, 
except the first and last key, to three characters. If the result is still too 
long, the script truncates each key to a single character.

Any markdown file with a truncated has the full key written as an HTML comment 
at the beginning of the file. 

For example, the key:
`DeploymentRuntimeConfig.spec.deploymentTemplate.spec.template.spec.affinity.nodeAffinity.preferredDuringSchedulingIgnoredDuringExecution.items.properties.preference.matchExpressions.items.properties.values`

Creates the file:
`pkg.crossplane.io_deploymentruntimeconfigs/DeploymentRuntimeConfig.spec.depl.spec.temp.spec.affi.node.pref.item.prop.pref.matc.item.prop.values.md`

The file contents are:
```markdown
<!-- kind: DeploymentRuntimeConfig.spec.deploymentTemplate.spec.template.spec.affinity.nodeAffinity.preferredDuringSchedulingIgnoredDuringExecution.items.properties.preference.matchExpressions.items.properties.values -->
An array of string values. If the operator is In or NotIn, the values array must be non-empty. If the operator is Exists or DoesNotExist, the values array must be empty. If the operator is Gt or Lt, the values array must have a single element, which will be interpreted as an integer. This array is replaced during a strategic merge patch.
```

If a file is missing the comment, the script can't diff the description.

## Diff markdown files

The `--diff` argument runs against a single CRD or directory of CRDs.  
The script collects all keys in the CRD and matches them to description files. 

The script prints any missing description markdown files. The script also prints 
any description files in a group that don't match fields in the CRD. 

For example, if the descriptions directory 

```shell
python3 api-generator.py --diff -crd content/v1.14/api/crds/apiextensions.crossplane.io_compositeresourcedefinitions.yaml -desc content/v1.14/api/descriptions
Missing description files:
	content/v1.14/api/descriptions/apiextensions.crossplane.io_compositeresourcedefinitions/CompositeResourceDefinition.spec.connectionSecretKeys.md
	content/v1.14/api/descriptions/apiextensions.crossplane.io_compositeresourcedefinitions/CompositeResourceDefinition.spec.claimNames.listKind.md

Description files without matching CRD descriptions:
	content/v1.14/api/descriptions/apiextensions.crossplane.io_compositeresourcedefinitions/CompositeResourceDefinition/spec.test.md
```