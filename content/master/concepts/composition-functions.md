---
title: Composition Functions
state: alpha
alphaVersion: "1.11"
weight: 80
description: "Composition Functions or XFNs allow for complex Composition patches"
aliases: 
  - /knowledge-base/guides/composition-functions
---

<!-- TODO: XFN only use read-only filesystem.
https://github.com/crossplane/crossplane/issues/4182
-->

Composition Functions allow you to supplement or replace your Compositions with
advanced logic not implementable through available patching strategies. 


You can build a Function using general purpose programming
languages such as Go or Python, or relevant tools such as Helm, 
[Kustomize](https://kustomize.io/), or
[CUE](https://cuelang.org/).  

Functions compliment contemporary "Patch and Transform" (P&T) style
Composition. It's possible to use only P&T, only Functions, or a mix of both in
the same Composition.

```yaml
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
metadata:
  name: example
spec:
  compositeTypeRef:
    apiVersion: database.example.org/v1alpha1
    kind: XPostgreSQLInstance
  functions:
  - name: my-cool-Function
    type: Container
    container:
      image: xpkg.upbound.io/my-cool-Function:0.1.0
```

A Composition Function is a short-lived OCI container that tells Crossplane how
to reconcile a Composite Resource (XR). The preceding example shows a minimal
`Composition` that uses a Composition Function. Note that it has a `functions`
array rather than the typical P&T style array of `resources`.

## Enabling functions

Enable support for Composition Functions by enabling the alpha feature flag in Crossplane with `helm install --args`.

```shell
helm install crossplane --namespace crossplane-system crossplane-stable/crossplane \
    --create-namespace \
    --set "args={--debug,--enable-composition-functions}" \
    --set "xfn.enabled=true" \
    --set "xfn.args={--debug}"
```

The preceding Helm command installs Crossplane with the Composition Functions
feature flag enabled, and with the reference _xfn_ Composition Function runner
deployed as a sidecar container. Confirm Composition Functions were enabled by
looking for a log line:

```shell {copy-lines="1"}
 kubectl -n crossplane-system logs -l app=crossplane
{"level":"info","ts":1674535093.36186,"logger":"crossplane","msg":"Alpha feature enabled","flag":"EnableAlphaCompositionFunctions"}
```

You should see the log line emitted shortly after Crossplane starts.


## Using functions

To use Composition Functions you must:

1. Find one or more Composition Functions, or write your own.
2. Create a `Composition` that uses your Functions.
3. Create an XR that uses your `Composition`.

Your XRs, claims, and providers don't need to be updated or otherwise aware
of Composition Functions to use them. They need only use a `Composition` that
includes one or more entries in its `spec.functions` array.

Composition Functions are designed to be run in a pipeline, so you can 'stack'
several of them together. Each Function is passed the output of the previous
Function as its input. Functions can also be used in conjunction with P&T
Composition (a `spec.resources` array). 

In the following example P&T Composition composes an RDS instance. A pipeline of
(hypothetical) Composition Functions then mutates the desired RDS instance by
adding a randomly generated password, and composes an RDS security group.

```yaml
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
metadata:
  name: example
spec:
  compositeTypeRef:
    apiVersion: database.example.org/v1alpha1
    kind: XPostgreSQLInstance
  resources:
    - name: rds-instance
      base:
        apiVersion: rds.aws.upbound.io/v1beta1
        kind: Instance
        spec:
          forProvider:
            dbName: exmaple
            instanceClass: db.t3.micro
            region: us-west-2
            skipFinalSnapshot: true
            username: exampleuser
            engine: postgres
            engineVersion: "12"
      patches:
        - fromFieldPath: spec.parameters.storageGB
          toFieldPath: spec.forProvider.allocatedStorage
      connectionDetails:
        - type: FromFieldPath
          name: username
          fromFieldPath: spec.forProvider.username
        - type: FromConnectionSecretKey
          name: password
          fromConnectionSecretKey: attribute.password
  functions:
  - name: rds-instance-password
    type: Container
    container:
      image: xpkg.upbound.io/provider-aws-xfns/random-rds-password:v0.1.0
  - name: compose-dbsecuritygroup
    type: Container
    container:
      image: xpkg.upbound.io/example-org/compose-rds-securitygroup:v0.9.0
```


Use `kubectl explain` to explore the configuration options available when using
Composition Functions, or take a look at the following example.

{{< expand "View Composition Function configuration options" >}}
```shell {copy-lines="1"}
kubectl explain composition.spec.functions
KIND:     Composition
VERSION:  apiextensions.crossplane.io/v1

RESOURCE: Functions <[]Object>

DESCRIPTION:
     Functions is list of Composition Functions that will be used when a
     composite resource referring to this composition is created. At least one
     of resources and Functions must be specified. If both are specified the
     resources will be rendered first, then passed to the Functions for further
     processing. THIS IS AN ALPHA FIELD. Do not use it in production. It is not
     honored unless the relevant Crossplane feature flag is enabled, and may be
     changed or removed without notice.

     A Function represents a Composition Function.

FIELDS:
   config       <>
     Config is an optional, arbitrary Kubernetes resource (i.e. a resource with
     an apiVersion and kind) that will be passed to the Composition Function as
     the 'config' block of its FunctionIO.

   container    <Object>
     Container configuration of this Function.

   name <string> -required-
     Name of this Function. Must be unique within its Composition.

   type <string> -required-
     Type of this Function.
```
{{< /expand >}}

{{< expand "An example of most Composition Function configuration options" >}}
```yaml
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
metadata:
  name: example
spec:
  compositeTypeRef:
    apiVersion: database.example.org/v1alpha1
    kind: XPostgreSQLInstance
  functions:
  - name: my-cool-Function
    # Currently only Container is supported. Other types may be added in future.
    type: Container
    # Configuration specific to type: Container.
    container:
      # The OCI image to pull and run.
      image: xkpg.io/my-cool-Function:0.1.0
      # Whether to pull the Function image Never, Always, or IfNotPresent.
      imagePullPolicy: IfNotPresent
      # Note that only resource limits are supported - not requests.
      # The Function will be run with the specified resource limits, specified
      # in Kubernetes-style resource.Quantity form.
      resources:
        limits:
          # Defaults to 128Mi
          memory: 64Mi
          # Defaults to 100m (a 10th of a core)
          cpu: 250m
      # Defaults to 'Isolated' - an isolated network namespace with no network
      # access. Use 'Runner' to allow a Function access to the runner's (the xfn
      # container's) network namespace.
      network:
        policy: Runner
      # How long the Function may run before it's killed. Defaults to 20s.
      # Keep in mind the Function pipeline is typically invoked once every
      # 30 to 60 seconds - sometimes more frequently during error conditions.
      timeout: 30s
    # An arbitrary Kubernetes resource. Passed to the Function as the config
    # block of its FunctionIO. Doesn't need to exist as a Custom Resource (CR),
    # since this resource doesn't exist by itself in the API server but must be
    # a valid Kubernetes resource (have an apiVersion and kind).
    config:
      apiVersion: database.example.org/v1alpha1
      kind: Config
      metadata:
        name: cloudsql
      spec:
        version: POSTGRES_9_6
```
{{< /expand >}}

Use `kubectl describe <xr-kind> <xr-name>` to debug Composition Functions. Look
for status conditions and events. Most Functions will emit events associated
with the XR if they experience issues.

## Building a function

 Crossplane doesn't have opinions about how a Composition Function is
 implemented. Functions must:

 * Be packaged as an OCI image, where the `ENTRYPOINT` is the Function.
 * Accept input in the form of a `FunctionIO` document on stdin.
 * Return the `FunctionIO` they were passed, optionally mutated, on stdout.
 * Run within the constraints specified by the Composition that includes them,
   such as timeouts, compute, network access.

This means Functions may be written using a general purpose programming language
like Python, Go, or TypeScript. They may also be implemented using a shell
script, or an existing tool like Helm or Kustomize.

### FunctionIO

When a Composition Function runner like `xfn` runs your Function it will write
`FunctionIO` to its stdin. A `FunctionIO` is a Kubernetes style YAML manifest.
It's not a custom resource (it never gets created in the API server) but it
follows Kubernetes conventions.

A `FunctionIO` consists of:

* An optional, arbitrary `config` object.
* The `observed` state of the XR, any existing composed resources, and their connection details.
* The `desired` state of the XR and any composed resources.
* Optional `results` of the Function pipeline.

Here's a brief example of a `FunctionIO`:

```yaml
apiVersion: apiextensions.crossplane.io/v1alpha1
kind: FunctionIO
config:
  apiVersion: database.example.org/v1alpha1
  kind: Config
  metadata:
    name: cloudsql
  spec:
    version: POSTGRES_9_6
observed:
  composite:
    resource:
      apiVersion: database.example.org/v1alpha1
      kind: XPostgreSQLInstance
      metadata:
        name: platform-ref-gcp-db-p9wrj
    connectionDetails:
    - name: privateIP
      value: 10.135.0.3
  resources:
  - name: db-instance
    resource:
      apiVersion: sql.gcp.upbound.io/v1beta1
      kind: DatabaseInstance
      metadata:
        name: platform-ref-gcp-db-p9wrj-tvvtg
    connectionDetails:
    - name: privateIP
      value: 10.135.0.3
desired:
  composite:
    resource:
      apiVersion: database.example.org/v1alpha1
      kind: XPostgreSQLInstance
      metadata:
        name: platform-ref-gcp-db-p9wrj
    connectionDetails:
    - name: privateIP
      value: 10.135.0.3
  resources:
  - name: db-instance
    resource:
      apiVersion: sql.gcp.upbound.io/v1beta1
      kind: DatabaseInstance
      metadata:
        name: platform-ref-gcp-db-p9wrj-tvvtg
  - name: db-user
    resource:
      apiVersion: sql.gcp.upbound.io/v1beta1
      kind: User
      metadata:
        name: platform-ref-gcp-db-p9wrj-z8lpz
    connectionDetails:
    - name: password
      type: FromValue
      value: very-secret
    readinessChecks:
    - type: None
results:
- severity: Normal
  message: "Successfully composed GCP SQL user"
```

The `config` object is copied from the `Composition`. It will match what's
passed as your Function's `config` in the `Functions` array. It must be a valid
Kubernetes object - have an `apiVersion` and `kind`.

The `observed` state of the XR and any existing composed resources reflects the
observed state at the beginning of a reconcile, before any Composition happens.
Your Function will only see composite and composed resources that _actually
exist_ in the API server in the `observed` state. The `observed` state also
includes any observed connection details. Initial function invocations
might see empty connection details, but once external resources are created,
connection details will be passed to the functions. Access to the connection
details enables us to implement quite sophisticated tweaks on composed resources.

For example, if a composition is declared on two or more resources, it is possible
to use one resource's connection details to update another. This ability is not available
with any of the available patch types available.

The `desired` state of the XR and composed resources is how your Function tells
Crossplane what it should do. Crossplane 'bootstraps' the initial desired state
passed to a Function pipeline with:

* A copy of the observed state of the composite resource (XR).
* A copy of the observed state of any existing composed resources produced
  from the `resources` array.
* Any new composed resources or modifications to observed resources produced
  from the `resources` array.

{{< hint "note" >}}
The initial desired state doesn't include any copies of observed resources
produced by the function pipeline. When using multiple functions each function
passes their desired resources output as input to the next pipeline function.
{{< /hint >}}

When adding a new desired resource to the `desired.resources` array you don't
need to:

* Update the XR's resource references.
* Add any composition annotations like `crossplane.io/composite-resource-name`.
* Set the XR as a controller/owner reference of the desired resource.

Crossplane will take care of all of these for you. It won't do anything else,
including setting a sensible `metadata.name` for the new composed resource -
this is up to your Function.

Finally, the `results` array allows your Function to surface events and debug
logs on the XR. Results support the following severities:

* `Normal` emits a debug log and a `Normal` event associated with the XR.
* `Warning` emits a debug log and a `Warning` event associated with the XR.
* `Fatal` stops the Composition process before applying any changes.

When Crossplane encounters a `Fatal` result it will finish running the
Composition Function pipeline. Crossplane will then return an error without
applying any changes to the API server. Crossplane surfaces this error as a
`Warning` event, a debug log, and by setting the `Synced` status condition of
the XR to "False".

The preceding example is heavily edited for brevity. Expand the following
example for a more detailed, realistic, and commented example of a `FunctionIO`.

{{< expand "A more detailed example" >}}
In this example a `XPostgreSQLInstance` XR has one existing composed resource -
`db-instance`. The composition Function returns a `desired` object with one new
composed resource, a `db-user`, to tell Crossplane it should also create a
database user.

```yaml
apiVersion: apiextensions.crossplane.io/v1alpha1
kind: FunctionIO
config:
  apiVersion: database.example.org/v1alpha1
  kind: Config
  metadata:
    name: cloudsql
  spec:
    version: POSTGRES_9_6
observed:
  # The observed state of the Composite Resource.
  composite:
    resource:
      apiVersion: database.example.org/v1alpha1
      kind: XPostgreSQLInstance
      metadata:
        creationTimestamp: "2023-01-27T23:47:12Z"
        finalizers:
        - composite.apiextensions.crossplane.io
        generateName: platform-ref-gcp-db-
        generation: 5
        labels:
          crossplane.io/claim-name: platform-ref-gcp-db
          crossplane.io/claim-namespace: default
          crossplane.io/composite: platform-ref-gcp-db-p9wrj
        name: platform-ref-gcp-db-p9wrj
        resourceVersion: "6817"
        uid: 96623f41-be2e-4eda-84d4-9668b48e284d
      spec:
        claimRef:
          apiVersion: database.example.org/v1alpha1
          kind: PostgreSQLInstance
          name: platform-ref-gcp-db
          namespace: default
        compositionRef:
          name: xpostgresqlinstances.database.example.org
        compositionRevisionRef:
          name: xpostgresqlinstances.database.example.org-eb6c684
        compositionUpdatePolicy: Automatic
        parameters:
          storageGB: 10
        resourceRefs:
        - apiVersion: sql.gcp.upbound.io/v1beta1
          kind: DatabaseInstance
          name: platform-ref-gcp-db-p9wrj-tvvtg
        writeConnectionSecretToRef:
          name: 96623f41-be2e-4eda-84d4-9668b48e284d
          namespace: upbound-system
      status:
        conditions:
        - lastTransitionTime: "2023-01-27T23:47:12Z"
          reason: ReconcileSuccess
          status: "True"
          type: Synced
        - lastTransitionTime: "2023-01-28T00:09:12Z"
          reason: Creating
          status: "False"
          type: Ready
        connectionDetails:
          lastPublishedTime: "2023-01-28T00:08:12Z"
    # Any observed Composite Resource connection details.
    connectionDetails:
    - name: privateIP
      value: 10.135.0.3
  # The observed state of any existing Composed Resources.
  resources:
  - name: db-instance
    resource:
      apiVersion: sql.gcp.upbound.io/v1beta1
      kind: DatabaseInstance
      metadata:
        annotations:
          crossplane.io/composition-resource-name: db-instance
          crossplane.io/external-name: platform-ref-gcp-db-p9wrj-tvvtg
        creationTimestamp: "2023-01-27T23:47:12Z"
        finalizers:
        - finalizer.managedresource.crossplane.io
        generateName: platform-ref-gcp-db-p9wrj-
        generation: 80
        labels:
          crossplane.io/claim-name: platform-ref-gcp-db
          crossplane.io/claim-namespace: default
          crossplane.io/composite: platform-ref-gcp-db-p9wrj
        name: platform-ref-gcp-db-p9wrj-tvvtg
        ownerReferences:
        - apiVersion: database.example.org/v1alpha1
          blockOwnerDeletion: true
          controller: true
          kind: XPostgreSQLInstance
          name: platform-ref-gcp-db-p9wrj
          uid: 96623f41-be2e-4eda-84d4-9668b48e284d
        resourceVersion: "7992"
        uid: 43919834-fdce-427e-85d9-d03eab9501f1
      spec:
        forProvider:
          databaseVersion: POSTGRES_13
          deletionProtection: false
          project: example
          region: us-west2
          settings:
          - diskSize: 10
            ipConfiguration:
            - privateNetwork: projects/example/global/networks/platform-ref-gcp-cluster
              privateNetworkRef:
                name: platform-ref-gcp-cluster
            tier: db-f1-micro
        providerConfigRef:
          name: default
        writeConnectionSecretToRef:
          name: 96623f41-be2e-4eda-84d4-9668b48e284d-gcp-postgresql
          namespace: upbound-system
      status:
        atProvider:
          connectionName: example:us-west2:platform-ref-gcp-db-p9wrj-tvvtg
          firstIpAddress: 34.102.103.85
          id: platform-ref-gcp-db-p9wrj-tvvtg
          privateIpAddress: 10.135.0.3
          publicIpAddress: 34.102.103.85
          settings:
          - version: 1
        conditions:
        - lastTransitionTime: "2023-01-28T00:07:30Z"
          reason: Available
          status: "True"
          type: Ready
        - lastTransitionTime: "2023-01-27T23:47:14Z"
          reason: ReconcileSuccess
          status: "True"
          type: Synced
    # Any observed composed resource connection details.
    connectionDetails:
    - name: privateIP
      value: 10.135.0.3
desired:
  # The observed state of the Composite Resource.
  composite:
    resource:
      apiVersion: database.example.org/v1alpha1
      kind: XPostgreSQLInstance
      metadata:
        creationTimestamp: "2023-01-27T23:47:12Z"
        finalizers:
        - composite.apiextensions.crossplane.io
        generateName: platform-ref-gcp-db-
        generation: 5
        labels:
          crossplane.io/claim-name: platform-ref-gcp-db
          crossplane.io/claim-namespace: default
          crossplane.io/composite: platform-ref-gcp-db-p9wrj
        name: platform-ref-gcp-db-p9wrj
        resourceVersion: "6817"
        uid: 96623f41-be2e-4eda-84d4-9668b48e284d
      spec:
        claimRef:
         e apiVersion: database.example.org/v1alpha1
          kind: PostgreSQLInstance
          name: platform-ref-gcp-db
          namespace: default
        compositionRef:
          name: xpostgresqlinstances.database.example.org
        compositionRevisionRef:
          name: xpostgresqlinstances.database.example.org-eb6c684
        compositionUpdatePolicy: Automatic
        parameters:
          storageGB: 10
        resourceRefs:
        - apiVersion: sql.gcp.upbound.io/v1beta1
          kind: DatabaseInstance
          name: platform-ref-gcp-db-p9wrj-tvvtg
        writeConnectionSecretToRef:
          name: 96623f41-be2e-4eda-84d4-9668b48e284d
          namespace: upbound-system
      status:
        conditions:
        - lastTransitionTime: "2023-01-27T23:47:12Z"
          reason: ReconcileSuccess
          status: "True"
          type: Synced
        - lastTransitionTime: "2023-01-28T00:09:12Z"
          reason: Creating
          status: "False"
          type: Ready
        connectionDetails:
          lastPublishedTime: "2023-01-28T00:08:12Z"
    # Any desired Composite Resource connection details. Your Composition
    # Function can add new entries to this array and Crossplane will record them
    # as the XR's connection details.
    connectionDetails:
    - name: privateIP
      value: 10.135.0.3
  # The desired composed resources.
  resources:
  # This db-instance matches the entry in observed. Functions must include any
  # observed resources in their desired resources array. If you omit an observed
  # resource from the desired resources array Crossplane will delete it.
  # Crossplane will 'bootstrap' the desired state passed to the Function
  # pipeline by copying all observed resources into the desired resources array.
  - name: db-instance
    resource:
      apiVersion: sql.gcp.upbound.io/v1beta1
      kind: DatabaseInstance
      metadata:
        annotations:
          crossplane.io/composition-resource-name: DBInstance
          crossplane.io/external-name: platform-ref-gcp-db-p9wrj-tvvtg
        creationTimestamp: "2023-01-27T23:47:12Z"
        finalizers:
        - finalizer.managedresource.crossplane.io
        generateName: platform-ref-gcp-db-p9wrj-
        generation: 80
        labels:
          crossplane.io/claim-name: platform-ref-gcp-db
          crossplane.io/claim-namespace: default
          crossplane.io/composite: platform-ref-gcp-db-p9wrj
        name: platform-ref-gcp-db-p9wrj-tvvtg
        ownerReferences:
        - apiVersion: database.example.org/v1alpha1
          blockOwnerDeletion: true
          controller: true
          kind: XPostgreSQLInstance
          name: platform-ref-gcp-db-p9wrj
          uid: 96623f41-be2e-4eda-84d4-9668b48e284d
        resourceVersion: "7992"
        uid: 43919834-fdce-427e-85d9-d03eab9501f1
      spec:
        forProvider:
          databaseVersion: POSTGRES_13
          deletionProtection: false
          project: example
          region: us-west2
          settings:
          - diskSize: 10
            ipConfiguration:
            - privateNetwork: projects/example/global/networks/platform-ref-gcp-cluster
              privateNetworkRef:
                name: platform-ref-gcp-cluster
            tier: db-f1-micro
        providerConfigRef:
          name: default
        writeConnectionSecretToRef:
          name: 96623f41-be2e-4eda-84d4-9668b48e284d-gcp-postgresql
          namespace: upbound-system
      status:
        atProvider:
          connectionName: example:us-west2:platform-ref-gcp-db-p9wrj-tvvtg
          firstIpAddress: 34.102.103.85
          id: platform-ref-gcp-db-p9wrj-tvvtg
          privateIpAddress: 10.135.0.3
          publicIpAddress: 34.102.103.85
          settings:
          - version: 1
        conditions:
        - lastTransitionTime: "2023-01-28T00:07:30Z"
          reason: Available
          status: "True"
          type: Ready
        - lastTransitionTime: "2023-01-27T23:47:14Z"
          reason: ReconcileSuccess
          status: "True"
          type: Synced
  # This db-user is a desired composed resource that doesn't yet exist. This
  # Composition Function is requesting it be created.
  - name: db-user
    resource:
      apiVersion: sql.gcp.upbound.io/v1beta1
      kind: User
      metadata:
        annotations:
          crossplane.io/composition-resource-name: db-user
          crossplane.io/external-name: platform-ref-gcp-db-p9wrj-z8lpz
        creationTimestamp: "2023-01-27T23:47:12Z"
        finalizers:
        - finalizer.managedresource.crossplane.io
        generateName: platform-ref-gcp-db-p9wrj-
        generation: 115
        labels:
          crossplane.io/claim-name: platform-ref-gcp-db
          crossplane.io/claim-namespace: default
          crossplane.io/composite: platform-ref-gcp-db-p9wrj
        name: platform-ref-gcp-db-p9wrj-z8lpz
        ownerReferences:
        - apiVersion: database.example.org/v1alpha1
          blockOwnerDeletion: true
          controller: true
          kind: XPostgreSQLInstance
          name: platform-ref-gcp-db-p9wrj
          uid: 96623f41-be2e-4eda-84d4-9668b48e284d
        resourceVersion: "9951"
        uid: ab5dafbe-2bc8-47ea-8b5b-9bcb40183e45
      spec:
        forProvider:
          instance: platform-ref-gcp-db-p9wrj-tvvtg
          project: example
        providerConfigRef:
          name: default
    # Any desired connection details for the new db-user composed resource.
    # Desired connection details can be FromValue, FromFieldPath, or
    # FromConnectionSecretKey, just like their P&T Composition equivalents.
    connectionDetails:
    - name: password
      type: FromValue
      value: very-secret
    # Any desired readiness checks for the new db-user composed resource.
    # Desired readiness checks can be NonEmpty, MatchString, MatchInteger, or
    # None, just like their P&T Composition equivalents.    
    readinessChecks:
    - type: None
# An optional array of results.
results:
- severity: Normal
  message: "Successfully composed GCP SQL user"
```
{{< /expand >}}

### An example Function

You can write a Composition Function using any programming language that can be
containerized, or existing tools like Helm or Kustomize.

Here's a Python Composition Function that doesn't create any new desired
resources, but instead annotates any existing desired resources with a quote.
Because this function accesses the internet it needs to be run with the `Runner`
network policy.

```python
import sys

import requests
import yaml

ANNOTATION_KEY_AUTHOR = "quotable.io/author"
ANNOTATION_KEY_QUOTE = "quotable.io/quote"


def get_quote() -> tuple[str, str]:
    """Get a quote from quotable.io"""
    rsp = requests.get("https://api.quotable.io/random")
    rsp.raise_for_status()
    j = rsp.json()
    return (j["author"], j["content"])


def read_Functionio() -> dict:
    """Read the FunctionIO from stdin."""
    return yaml.load(sys.stdin.read(), yaml.Loader)


def write_Functionio(Functionio: dict):
    """Write the FunctionIO to stdout and exit."""
    sys.stdout.write(yaml.dump(Functionio))
    sys.exit(0)


def result_warning(Functionio: dict, message: str):
    """Add a warning result to the supplied FunctionIO."""
    if "results" not in Functionio:
        Functionio["results"] = []
    Functionio["results"].append({"severity": "Warning", "message": message})


def main():
    """Annotate all desired composed resources with a quote from quotable.io"""
    try:
        Functionio = read_Functionio()
    except yaml.parser.ParserError as err:
        sys.stdout.write("cannot parse FunctionIO: {}\n".format(err))
        sys.exit(1)

    # Return early if there are no desired resources to annotate.
    if "desired" not in Functionio or "resources" not in Functionio["desired"]:
        write_Functionio(Functionio)

    # If we can't get our quote, add a warning and return early.
    try:
        quote, author = get_quote()
    except requests.exceptions.RequestException as err:
        result_warning(Functionio, "Cannot get quote: {}".format(err))
        write_Functionio(Functionio)

    # Annotate all desired resources with our quote.
    for r in Functionio["desired"]["resources"]:
        if "resource" not in r:
            # This shouldn't happen - add a warning and continue.
            result_warning(
                Functionio,
                "Desired resource {name} missing resource body".format(
                    name=r.get("name", "unknown")
                ),
            )
            continue

        if "metadata" not in r["resource"]:
            r["resource"]["metadata"] = {}

        if "annotations" not in r["resource"]["metadata"]:
            r["resource"]["metadata"]["annotations"] = {}

        if ANNOTATION_KEY_QUOTE in r["resource"]["metadata"]["annotations"]:
            continue

        r["resource"]["metadata"]["annotations"][ANNOTATION_KEY_AUTHOR] = author
        r["resource"]["metadata"]["annotations"][ANNOTATION_KEY_QUOTE] = quote

    write_Functionio(Functionio)


if __name__ == "__main__":
    main()
```

Building this function requires its `requirements.txt` and a `Dockerfile`:

{{< expand "The Function's requirements" >}}
```python
certifi==2022.12.7
charset-normalizer==3.0.1
click==8.1.3
idna==3.4
pathspec==0.10.3
platformdirs==2.6.2
PyYAML==6.0
requests==2.28.2
tomli==2.0.1
urllib3==1.26.14
```
{{< /expand >}}

{{< expand "The Function's Dockerfile" >}}
```Dockerfile
FROM debian:11-slim AS build
RUN apt-get update && \
    apt-get install --no-install-suggests --no-install-recommends --yes python3-venv && \
    python3 -m venv /venv && \
    /venv/bin/pip install --upgrade pip setuptools wheel

FROM build AS build-venv
COPY requirements.txt /requirements.txt
RUN /venv/bin/pip install --disable-pip-version-check -r /requirements.txt

FROM gcr.io/distroless/python3-debian11
COPY --from=build-venv /venv /venv
COPY . /app
WORKDIR /app
ENTRYPOINT ["/venv/bin/python3", "main.py"]
```
{{< /expand >}}

Create and push the Function just like you would any Docker image.

Build the function.

```shell {copy-lines="1"}
docker build .
Sending build context to Docker daemon  38.99MB
Step 1/10 : FROM debian:11-slim AS build
 ---> 4810399f6c13
Step 2/10 : RUN apt-get update &&     apt-get install --no-install-suggests --no-install-recommends --yes python3-venv gcc && python3 -m venv /venv &&     /venv/bin/pip install --upgrade pip setuptools wheel
 ---> Using cache
 ---> 9b34960c88d7
Step 3/10 : FROM build AS build-venv
 ---> 9b34960c88d7
Step 4/10 : COPY requirements.txt /requirements.txt
 ---> Using cache
 ---> fae19dad52af
Step 5/10 : RUN /venv/bin/pip install --disable-pip-version-check -r /requirements.txt
 ---> Using cache
 ---> f4b811c75812
Step 6/10 : FROM gcr.io/distroless/python3-debian11
 ---> 2a0e74a2b005
Step 7/10 : COPY --from=build-venv /venv /venv
 ---> Using cache
 ---> cf727d3f20d3
Step 8/10 : COPY . /app
 ---> a044aef45e32
Step 9/10 : WORKDIR /app
 ---> Running in d08a6144815b
Removing intermediate container d08a6144815b
 ---> 7250f5aa653e
Step 10/10 : ENTRYPOINT ["/venv/bin/python3", "main.py"]
 ---> Running in 3f4d9dc55bad
Removing intermediate container 3f4d9dc55bad
 ---> bfd2f920c591
Successfully built bfd2f920c591
```

Tag the function.
```shell
docker tag bfd2f920c591 example-org/xfn-quotable-simple:v0.1.0
```

Push the function.

```shell {copy-lines="1"}
docker push xpkg.upbound.io/example-org/xfn-quotable-simple:v0.1.0
The push refers to repository [xpkg.upbound.io/example-org/xfn-quotable-simple]
cf6d94b88843: Pushed
77646fd315d2: Mounted from example-org/xfn-quotable
50630ee42b6e: Mounted from example-org/xfn-quotable
7e2cf97ed8c4: Mounted from example-org/xfn-quotable
96e320b34b54: Mounted from example-org/xfn-quotable
fba4381f2bb7: Mounted from example-org/xfn-quotable
v0.1.0: digest: sha256:d8a6404e5fe38936aa8dadd861fea35ede0aded6168d501052f91cdabab0135e size: 1584
```

You can now use this Function in your Composition. The following example will
create an `RDSInstance` using P&T Composition, then run the Function to annotate
it with a quote.

```yaml
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
metadata:
  name: example
spec:
  compositeTypeRef:
    apiVersion: database.example.org/v1alpha1
    kind: XPostgreSQLInstance
  resources:
    - name: rds-instance
      base:
        apiVersion: rds.aws.upbound.io/v1beta1
        kind: Instance
        spec:
          forProvider:
            dbName: example
            instanceClass: db.t3.micro
            region: us-west-2
            skipFinalSnapshot: true
            username: exampleuser
            engine: postgres
            engineVersion: "12"
      patches:
        - fromFieldPath: spec.parameters.storageGB
          toFieldPath: spec.forProvider.allocatedStorage
      connectionDetails:
        - type: FromFieldPath
          name: username
          fromFieldPath: spec.forProvider.username
        - type: FromConnectionSecretKey
          name: password
          fromConnectionSecretKey: attribute.password
  functions:
  - name: quotable
    type: Container
    container:
      image: xpkg.upbound.io/example-org/xfn-quotable-simple:v0.1.0
      network:
        policy: Runner
```

### Tips for new functions

Here are some things to keep in mind when building a Composition Function:

* Your Function may be running as part of a pipeline. This means your Function
  _must_ pass through any desired state that it's unconcerned with. If your
  Function is passed a desired composed resource and doesn't return that
  composed resource in its output, it will be deleted. Crossplane considers the
  desired state of the XR and any composed resources to be whatever `FunctionIO`
  is returned by the last Function in the pipeline.
* Crossplane won't set a `metadata.name` for your desired resources resources.
  It's a good practice to match P&T Composition's behavior by setting
  `metadata.generateName: "name-of-the-xr-"` for any new desired resources.
* Don't add new entries to the desired resources array every time your function
  is invoked. Remember to check whether your desired resource is already in the
  `observed` and/or `desired` objects. You may need to update it rather than
  create it.
* Don't bypass providers. Composition Functions are designed to tell Crossplane
  how to orchestrate managed resources - not to directly orchestrate external
  systems.
* Include your function name and version in any results you return to aid in
  debugging.
* Write tests for your function. Pass it a `FunctionIO` on stdin in and ensure
  it returns the expected `FunctionIO` on stdout.
* Keep your Functions fast and lightweight. Remember that Crossplane runs them
  approximately once every 30-60 seconds.

## The xfn runner

Composition Function runners are designed to be pluggable. Each time Crossplane
needs to invoke a Composition Function it makes a gRPC call to a configurable
endpoint. The default, reference Composition Function runner is named `xfn`.

{{< hint "note" >}}
The default runner endpoint is `unix-abstract:crossplane/fn/default.sock`. It's
possible to run Functions using a different endpoint, for example:

```yaml
  functions:
  - name: my-cool-Function
    type: Container
    container:
      image: xkpg.io/my-cool-Function:0.1.0
      runner:
        endpoint: unix-abstract:/your/custom/runner.sock
```

Currently Crossplane uses unauthenticated, unencrypted gRPC requests to run
Functions, so requests shouldn't be sent over the network. Encryption and
authentication will be added in a future release.
{{< /hint >}}

`xfn` runs as a sidecar container within the Crossplane pod. It runs each
Composition Function as a nested [rootless container][rootless-containers].

{{< img src="media/composition-functions-xfn-runner.png" alt="Crossplane running Functions using xfn via gRPC" size="tiny" >}}

The Crossplane Helm chart deploys `xfn` with:

* The [`Unconfined` seccomp profile][kubernetes-seccomp].
* The `CAP_SETUID` and `CAP_SETGID` capabilities.

The `Unconfined` seccomp profile allows Crossplane to make required syscalls
such as `unshare` and `mount` that are not allowed by most `RuntimeDefault`
profiles. It's possible to run `xfn` with nearly the same restrictions as most
`RuntimeDefault` profiles by authoring a custom `Localhost` profile. Refer to
the [seccomp documentation][kubernetes-seccomp] for information on how to do so.

Granting `CAP_SETUID` and `CAP_SETGID` allows `xfn` to create Function
containers that support up to 65,536 UIDs and GIDs. If `xfn` is run without
these capabilities it will be restricted to creating Function containers that
support only UID and GID 0.

Regardless of capabilities `xfn` always runs each Composition Function as an
unprivileged user. That user will appear to be root inside the Composition
Function container thanks to [`user_namespaces(7)`].

[rootless-containers]: https://rootlesscontaine.rs
[kubernetes-seccomp]: https://kubernetes.io/docs/tutorials/security/seccomp/
[`user_namespaces(7)`]: https://man7.org/linux/man-pages/man7/user_namespaces.7.html
