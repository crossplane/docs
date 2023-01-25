---
title: Composition Functions
state: alpha
---

Composition Functions allow you to supplement or replace your Compositions with
advanced logic, using either programming languages such as Go or Python, or
relevant tools such as Helm, kustomize, or CUE. They compliment contemporary
"Patch and Transform" (P&T) style Composition - it's possible to use only P&T,
only Functions, or a mix of both in the same Composition.

```yaml
apiVersion: apiextensions.crossplane.io/v2alpha1
kind: Composition
metadata:
  name: example
spec:
  compositeTypeRef:
    apiVersion: database.example.org/v1alpha1
    kind: XPostgreSQLInstance
  functions:
  - name: my-cool-function
    type: Container
    container:
      image: xpkg.upbound.io/my-cool-function:0.1.0
```

A Composition Function is a short-lived OCI container that tells Crossplane how
to reconcile a Composite Resource (XR). The preceding example shows a minimal
`Composition` that uses a Composition Function rather than the typical P&T style
array of `resources`.

## Enabling Composition Functions

To enable support for Composition Functions you must:

 * Enable the alpha feature flag.
 * Deploy a runner that is responsible for running functions.

```console
# TODO(negz): Update this to use crossplane-stable, not an RC build, once v1.11 has been released.

kubectl create namespace crossplane-system

helm repo add crossplane-master https://charts.crossplane.io/master/
helm repo update

# Find the latest RC build of Crossplane - e.g. 1.11.0-rc.0.274.g51a07e50
helm search repo crossplane-master/crossplane --devel

RC_VERSION="v1.11.0-rc.0.274.g51a07e50"
helm install crossplane --namespace crossplane-system crossplane-master/crossplane \
    --devel --version ${RC_VERSION} \
    --set "args={--debug,--enable-composition-functions}" \
    --set "xfn.enabled=true" \
    --set "xfn.args={--debug}"
```

The preceding Helm command installs Crossplane with the Composition Functions
feature flag enabled, and with the reference "`xfn`" Composition Function runner
deployed as a sidecar pod. You can confirm Composition Functions are enabled by
looking for a log line like:

```json
$ kubectl -n crossplane-system logs -l app=crossplane
{"level":"info","ts":1674535093.36186,"logger":"crossplane","msg":"Alpha feature enabled","flag":"EnableAlphaCompositionFunctions"}
```

You should see the log line emitted shortly after Crossplane starts.

## The xfn Runner

Composition Function runners are designed to be pluggable. Each time Crossplane
needs to invoke a Composition Function it makes a gRPC call to a configurable
endpoint. The default, reference Composition Function runner is named `xfn`.

{{< img src="composition-functions-xfn-runner.png" alt="Crossplane running functions using xfn via gRPC" size="tiny" >}}

`xfn` is deployed as a sidecar container within the Crossplane pod. It runs each
Composition Function as a nested [rootless container][rootless-containers]. The
Crossplane Helm chart deploys `xfn` with slightly elevated permissions. Namely:

* The [Unconfined seccomp profile][kubernetes-seccomp].
* `CAP_SETUID` and `CAP_SETGID`.

`xfn` doesn't strictly need either of these. It's possible to run it under
seccomp but doing so is onerous. You must author a custom profile that allows a
few additional syscalls required to run containers, including `unshare`,
`mount`, and `unmount`. Refer to the [seccomp documentation][kubernetes-seccomp]
for information on how to do so.

Granting `CAP_SETUID` and `CAP_SETGID` is optional. Doing so allows `xfn` to
create slightly better rootless containers. If `xfn` is not granted these
capabilities it will not support multiple users and groups inside Composition
Function containers; only UID and GID 0 will exist. Regardless of capabilities
`xfn` always runs each Composition Function as an unprivileged user. That user
will appear to be root inside the Composition Function container thanks to 
[`user_namespaces(7)`].

## Using Composition Functions

To use Composition Functions you must:

1. Find one or more Composition Functions, or write your own.
2. Write a `Composition` that uses your Composition Functions.
3. Create an XR that uses your `Composition`.

Your XRs, claims, and providers don't need to be updated or otherwise aware
of Composition Functions to use them - they need only use a Composition that
includes one or more entries in its `spec.functions` array.

Composition Functions are designed to be run in a pipeline, so you can 'stack'
several of them together. Each function is passed the output of the previous
function as its input. Functions can also be used in conjunction with P&T
Composition (i.e. a `spec.resources` array). 

In the following example P&T Composition composes an RDS instance. A pipeline of
(hypothetical) Composition Functions then updates that RDS instance (before it's
applied to the API server) with a randomly generated password, and composes an
RDS security group.

```yaml
apiVersion: apiextensions.crossplane.io/v2alpha1
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
  - name: create-dbsecuritygroup
    type: Container
    container:
      image: xpkg.upbound.io/example-org/create-rds-securitygroup:v0.9.0
```

{{< hint "tip" >}}
Use `kubectl describe <xr-kind> <xr-name>` to debug Composition Functions. Most
functions will emit events associated with the XR if they experience issues.
{{< /hint >}}

You can use `kubectl explain` to explore the configuration options available
when using Composition Functions.

```console
$ kubectl explain composition.spec.functions
KIND:     Composition
VERSION:  apiextensions.crossplane.io/v1

RESOURCE: functions <[]Object>

DESCRIPTION:
     Functions is list of Composition Functions that will be used when a
     composite resource referring to this composition is created. At least one
     of resources and functions must be specified. If both are specified the
     resources will be rendered first, then passed to the functions for further
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
     Container configuration of this function.

   name <string> -required-
     Name of this function. Must be unique within its Composition.

   type <string> -required-
     Type of this function.
```

{{< expand "A Composition that demonstrates most Composition Function options" >}}
```yaml
apiVersion: apiextensions.crossplane.io/v2alpha1
kind: Composition
metadata:
  name: example
spec:
  compositeTypeRef:
    apiVersion: database.example.org/v1alpha1
    kind: XPostgreSQLInstance
  functions:
  - name: my-cool-function
    # Currently only Container is supported. Other types may be added in future.
    type: Container
    # Configuration specific to type: Container.
    container:
      # The OCI image to pull and run.
      image: xkpg.io/my-cool-function:0.1.0
      # Whether to pull the function image Never, Always, or IfNotPresent.
      imagePullPolicy: IfNotPresent
      # Note that only resource limits are supported - not requests.
      # The function will be run with the specified resource limits, specified
      # in Kubernetes-style resource.Quantity form.
      resources:
        limits:
          # Defaults to 128Mi
          memory: 64Mi
          # Defaults to 100m (a 10th of a core)
          cpu: 250m
      # Defaults to 'Isolated' - i.e an isolated network namespace with no
      # network access. Use 'Runner' to allow a function access to the runner's
      # (e.g. the xfn container's) network namespace.
      network:
        policy: Runner
      # How long the function may run before it's killed. Defaults to 20s.
      timeout: 30s
    # An x-kubernetes-embedded-resource RawExtension (i.e. an unschemafied
    # Kubernetes resource). Passed to the function as the config block of its
    # FunctionIO.
    config:
      apiVersion: database.example.org/v1alpha1
      kind: Config
      metadata:
        name: cloudsql
      spec:
        version: POSTGRES_9_6
```
{{< /expand >}}

## Building a Composition Function

 Crossplane is mostly unopinionated about how a Composition Function is built.
 Functions must:

 * Be packaged as an OCI image, where the `ENTRYPOINT` is the function.
 * Accept input in the form of a `FunctionIO` document on stdin.
 * Return the `FunctionIO` they were passed, optionally mutated, on stdout.
 * Run within the constraints specified by the Composition that includes them
   (e.g. timeouts, compute, network access).

```
TODO(negz):

* FunctionIO example - link to Go type def for 'full spec' (for now).
* Example function w/Dockerfile - something single file (quote annotator?)
* Things to keep in mind
    * Handling Observed and desired state.
    * You need to name your resources (we only add owner ref, annotations).
    * How to handle errors.
```

[rootless-containers]: https://rootlesscontaine.rs
[kubernetes-seccomp]: https://kubernetes.io/docs/tutorials/security/seccomp/
[`user_namespaces(7)`]: https://man7.org/linux/man-pages/man7/user_namespaces.7.html