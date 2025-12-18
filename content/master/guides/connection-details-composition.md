---
title: Connection Details Composition
weight: 83
description: "Expose connection details for composite resources aggregated from their composed resources"
---

This guide shows how to expose connection details for composite resources (XRs).
Because composite resources can compose multiple resources, the connection
details they expose are often an aggregate of the connection details from their
composed resources.

The recommended approach to do this is to simply include a Kubernetes `Secret`
resource in your Composition that aggregates the connection details from other
resources and exposes them for the XR.

{{<hint "note">}}
Crossplane v1 included functionality that automatically created connection details
for XRs.

To learn more about how to specify XR connection details in Crossplane v1, please see the
[v1 connection details]({{<ref "../../v1.20/concepts/connection-details">}}) docs page.
{{</hint>}}

## Example overview

To demonstrate how composite resources can expose connection details, this guide
creates a `UserAccessKey` composite resource. This XR represents an AWS IAM user
with multiple access keys.

When a user creates a `UserAccessKey`, Crossplane provisions an IAM User and two
AccessKeys in AWS. Each AccessKey produces their own connection details like a
username and password. The `UserAccessKey` also composes a `Secret` resource
that exposes the aggregated connection details of its composed resources, allowing
users and applications to easily consume them.

An example `UserAccessKey` XR looks like this:

```yaml
apiVersion: example.org/v1alpha1
kind: UserAccessKey
metadata:
  namespace: default
  name: my-keys
```

**Behind the scenes, Crossplane:**

1. Creates an AWS IAM `User` and two `AccessKeys` (the composed resources)
2. Collects connection details from both `AccessKeys`
3. Exposes them as the `UserAccessKey`'s connection details in a `Secret`

The composite resource's connection details `Secret` looks like this:

```yaml
apiVersion: v1
kind: Secret
metadata:
  namespace: default
  name: my-keys-connection-details
data:
  user-0: <base64-encoded-username>
  password-0: <base64-encoded-password>
  user-1: <base64-encoded-username>
  password-1: <base64-encoded-password>
```

Users and applications can consume the `UserAccessKey` connection details by
reading this Secret.

{{<hint "tip">}}
The pattern in this guide applies to any composite resource that needs to expose connection
details, for example:

* Database connection strings and credentials
* Cluster client certificate and key data
* Application endpoints from services and ingress
{{</hint>}}

## Prerequisites

This guide requires:

* A Kubernetes cluster
* Crossplane [installed on the Kubernetes cluster]({{<ref "../get-started/install">}})
* `provider-aws-iam` installed and configured with credentials

{{<hint "tip">}}
To set up the AWS provider, follow the [Get Started with Managed Resources]({{<ref "../get-started/get-started-with-managed-resources">}}) guide,
but use provider `provider-aws-iam:v2.3.0` instead.

Complete the steps to install the provider and configure credentials, then
return to this guide.
{{</hint>}}

## Build the composite resource

Follow these steps to create a composite resource that exposes connection
details:

1. [Define](#define-the-schema) the schema of the composite resource
1. [Install](#install-the-function) the composition function you want to use
1. [Configure](#configure-the-composition) how the composition exposes
    connection details

After you complete these steps you can
[use the composite resource](#use-the-composite-resource).

### Define the schema

Composite resources are defined using a CompositeResourceDefinition (XRD).

For this example, create an XRD for the `UserAccessKey` composite resource:

```yaml
apiVersion: apiextensions.crossplane.io/v2
kind: CompositeResourceDefinition
metadata:
  name: useraccesskeys.example.org
spec:
  group: example.org
  names:
    kind: UserAccessKey
    plural: useraccesskeys
  scope: Namespaced
  versions:
  - name: v1alpha1
    served: true
    referenceable: true
    schema:
      openAPIV3Schema:
        type: object
        properties:
          spec:
            type: object
            properties:
              writeConnectionSecretToRef:
                type: object
                properties:
                  name:
                    type: string
```

{{<hint "tip">}}
This XRD schema defines a `.spec.writeConnectionSecretToRef.name` field that
allows the user to optionally set the name for the XR connection details secret.

For a `Cluster` scoped XRD, a `.spec.writeConnectionSecretToRef.namespace` field
could also be added to allow the user to specify the namespace of the secret
too.
{{</hint>}}

Save the XRD as `xrd.yaml` and apply it:

```shell
kubectl apply -f xrd.yaml
```

The Kubernetes API is now serving requests for the `UserAccessKey` composite
resource.

### Install the function

Composition functions provide general functionality to help you compose
resources and expose connection details. This guide shows how to compose
connection details with multiple functions. Pick the language you want to use
from the tabs below.

{{< tabs >}}

{{< tab "Templated YAML" >}}
Templated YAML is a good choice if you're used to writing
[Helm charts](https://helm.sh).

Create this composition function to install templated YAML support:

```yaml
apiVersion: pkg.crossplane.io/v1
kind: Function
metadata:
  name: function-go-templating
spec:
  package: xpkg.crossplane.io/crossplane-contrib/function-go-templating:v0.11.2
```

Save the function as `fn.yaml` and apply it:

```shell
kubectl apply -f fn.yaml
```

Check that Crossplane installed the function:

```shell {copy-lines="1"}
kubectl get -f fn.yaml
NAME                     INSTALLED   HEALTHY   PACKAGE                                                                AGE
function-go-templating   True        True      xpkg.crossplane.io/crossplane-contrib/function-go-templating:v0.11.2   15s
```
{{< /tab >}}

{{< tab "Python" >}}

Create this composition function to install Python support:

```yaml
apiVersion: pkg.crossplane.io/v1
kind: Function
metadata:
  name: function-python
spec:
  package: xpkg.crossplane.io/crossplane-contrib/function-python:v0.2.0
```

Save the function as `fn.yaml` and apply it:

```shell
kubectl apply -f fn.yaml
```

Check that Crossplane installed the function:

```shell {copy-lines="1"}
kubectl get -f fn.yaml
NAME                                 INSTALLED   HEALTHY   PACKAGE                                                        AGE
function-python                      True        True      xpkg.crossplane.io/crossplane-contrib/function-python:v0.2.0   12s
```
{{< /tab >}}

{{< tab "KCL" >}}

Create this composition function to install [KCL](https://kcl-lang.io) support:

```yaml
apiVersion: pkg.crossplane.io/v1
kind: Function
metadata:
  name: function-kcl
spec:
  package: xpkg.crossplane.io/crossplane-contrib/function-kcl:v0.11.6
```

Save the function as `fn.yaml` and apply it:

```shell
kubectl apply -f fn.yaml
```

Check that Crossplane installed the function:

```shell {copy-lines="1"}
kubectl get -f fn.yaml
NAME                              INSTALLED   HEALTHY   PACKAGE                                                      AGE
function-kcl                      True        True      xpkg.crossplane.io/crossplane-contrib/function-kcl:v0.11.6   6s
```
{{< /tab >}}

{{< /tabs >}}

This guide also uses `function-auto-ready`. This function automatically
marks composed resources as ready when they're healthy:

```yaml
apiVersion: pkg.crossplane.io/v1
kind: Function
metadata:
  name: function-auto-ready
spec:
  package: xpkg.crossplane.io/crossplane-contrib/function-auto-ready:v0.6.0
```

Save this as `fn-auto-ready.yaml` and apply it:

```shell
kubectl apply -f fn-auto-ready.yaml
```

### Configure the composition

A Composition tells Crossplane how to compose resources for a composite
resource. This guide also includes a composed `Secret` resource to expose the
composite resource's connection details.

The general pattern is:

1. Composed resources write their connection details to individual secrets
2. The Composition reads those connection details during execution
3. The Composition creates a composed `Secret` representing the aggregated connection details for the XR

{{<hint "tip">}}
The composite resource's connection details secret can contain any data you want
and it can be transformed however you need.

You're not limited to connection details from managed resources - you can
include data from any composed resource, including arbitrary Kubernetes
resources like `ConfigMaps` or `Services`.
{{</hint>}}

Create a Composition that exposes connection details for the `UserAccessKey`
composite resource.

In this example, the Composition creates two `AccessKey` managed resources and
exposes their credentials as the composite resource's connection details `Secret`:

{{< tabs >}}

{{< tab "Templated YAML" >}}

```yaml {label="comp-gotmpl"}
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
metadata:
  name: useraccesskeys-go-templating
spec:
  compositeTypeRef:
    apiVersion: example.org/v1alpha1
    kind: UserAccessKey
  mode: Pipeline
  pipeline:
  - step: render-templates
    functionRef:
      name: function-go-templating
    input:
      apiVersion: gotemplating.fn.crossplane.io/v1beta1
      kind: GoTemplate
      source: Inline
      inline:
        template: |
          ---
          apiVersion: iam.aws.m.upbound.io/v1beta1
          kind: User
          metadata:
            annotations:
              {{ setResourceNameAnnotation "user" }}
          spec:
            forProvider: {}
          ---
          apiVersion: iam.aws.m.upbound.io/v1beta1
          kind: AccessKey
          metadata:
            annotations:
              {{ setResourceNameAnnotation "accesskey-0" }}
          spec:
            forProvider:
              userSelector:
                matchControllerRef: true
            writeConnectionSecretToRef:
              name: {{ $.observed.composite.resource.metadata.name }}-accesskey-secret-0
          ---
          apiVersion: iam.aws.m.upbound.io/v1beta1
          kind: AccessKey
          metadata:
            annotations:
              {{ setResourceNameAnnotation "accesskey-1" }}
          spec:
            forProvider:
              userSelector:
                matchControllerRef: true
            writeConnectionSecretToRef:
              name: {{ $.observed.composite.resource.metadata.name }}-accesskey-secret-1
          ---
          apiVersion: v1
          kind: Secret
          metadata:
            name: {{ dig "spec" "writeConnectionSecretToRef" "name" "" $.observed.composite.resource}}
            annotations:
              {{ setResourceNameAnnotation "connection-secret" }}
          {{ if eq $.observed.resources nil }}
          data: {}
          {{ else }}
          data:
            user-0: {{ ( index $.observed.resources "accesskey-0" ).connectionDetails.username }}
            user-1: {{ ( index $.observed.resources "accesskey-1" ).connectionDetails.username }}
            password-0: {{ ( index $.observed.resources "accesskey-0" ).connectionDetails.password }}
            password-1: {{ ( index $.observed.resources "accesskey-1" ).connectionDetails.password }}
          {{ end }}
  - step: ready
    functionRef:
      name: function-auto-ready
```

**How this Composition exposes connection details:**

* Each composed {{<hover label="comp-gotmpl" line="30">}}AccessKey{{</hover>}} has
  {{<hover label="comp-gotmpl" line="38">}}writeConnectionSecretToRef{{</hover>}} set. This
  tells each AccessKey to write its credentials to an individual Secret.
* The Composition creates an explicit
  {{<hover label="comp-gotmpl" line="54">}}Secret{{</hover>}} resource that
  represents the composite resource's connection details.
* The {{<hover label="comp-gotmpl" line="56">}}name{{</hover>}} of the `Secret` is set using the
{{<hover label="comp-gotmpl" line="56">}}dig{{</hover>}} function to safely read the XR's
  `.spec.writeConnectionSecretToRef.name` field if it exists.
* Crossplane observes the connection details from each `AccessKey` and makes them
  available to the composition when the function is executed.
* The Secret reads connection details via
  {{<hover label="comp-gotmpl" line="63">}}$.observed.resources{{</hover>}} from
  the observed composed resources.
* The {{<hover label="comp-gotmpl" line="59">}}{{ if eq $.observed.resources nil }}{{</hover>}}
  check handles the initial phase when composed resources are still being created.
* In `function-go-templating`, connection details are **already base64-encoded**, so you
  use them directly in the Secret's data field.

{{< /tab >}}

{{< tab "Python" >}}

```yaml {label="comp-python"}
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
metadata:
  name: useraccesskeys-python
spec:
  compositeTypeRef:
    apiVersion: example.org/v1alpha1
    kind: UserAccessKey
  mode: Pipeline
  pipeline:
  - step: render-python
    functionRef:
      name: function-python
    input:
      apiVersion: python.fn.crossplane.io/v1beta1
      kind: Script
      script: |
        def compose(req, rsp):
            # Get observed composite resource
            oxr = req.observed.composite.resource
            oxr_name = oxr["metadata"]["name"]

            # IAM User
            rsp.desired.resources["user"].resource.update({
                "apiVersion": "iam.aws.m.upbound.io/v1beta1",
                "kind": "User",
                "spec": {
                    "forProvider": {}
                }
            })

            # Access Key 0
            rsp.desired.resources["accesskey-0"].resource.update({
                "apiVersion": "iam.aws.m.upbound.io/v1beta1",
                "kind": "AccessKey",
                "spec": {
                    "forProvider": {
                        "userSelector": {
                            "matchControllerRef": True
                        }
                    },
                    "writeConnectionSecretToRef": {
                        "name": f"{oxr_name}-accesskey-secret-0"
                    }
                }
            })

            # Access Key 1
            rsp.desired.resources["accesskey-1"].resource.update({
                "apiVersion": "iam.aws.m.upbound.io/v1beta1",
                "kind": "AccessKey",
                "spec": {
                    "forProvider": {
                        "userSelector": {
                            "matchControllerRef": True
                        }
                    },
                    "writeConnectionSecretToRef": {
                        "name": f"{oxr_name}-accesskey-secret-1"
                    }
                }
            })

            # Secret representing the composite resource's connection details
            secret_resource = {
                "apiVersion": "v1",
                "kind": "Secret",
                "metadata": {}
            }

            # If a secret name was provided then use it
            secret_name = ""
            if "writeConnectionSecretToRef" in oxr["spec"] and "name" in oxr["spec"]["writeConnectionSecretToRef"]:
              secret_name = oxr["spec"]["writeConnectionSecretToRef"]["name"]

            secret_resource["metadata"]["name"] = secret_name

            # Only add data if we have connection details to populate
            data = {}
            if "accesskey-0" in req.observed.resources:
                accesskey0_conn = req.observed.resources["accesskey-0"].connection_details
                if "username" in accesskey0_conn:
                    data["user-0"] = accesskey0_conn["username"].decode("utf-8")
                if "password" in accesskey0_conn:
                    data["password-0"] = accesskey0_conn["password"].decode("utf-8")

            if "accesskey-1" in req.observed.resources:
                accesskey1_conn = req.observed.resources["accesskey-1"].connection_details
                if "username" in accesskey1_conn:
                    data["user-1"] = accesskey1_conn["username"].decode("utf-8")
                if "password" in accesskey1_conn:
                    data["password-1"] = accesskey1_conn["password"].decode("utf-8")

            if data:
                secret_resource["stringData"] = data

            rsp.desired.resources["connection-secret"].resource.update(secret_resource)
  - step: ready
    functionRef:
      name: function-auto-ready

```

**How this Composition exposes connection details:**

* Each composed {{<hover label="comp-python" line="51">}}AccessKey{{</hover>}} has
  {{<hover label="comp-python" line="58">}}writeConnectionSecretToRef{{</hover>}} set. This
  tells each AccessKey to write its credentials to an individual Secret.
* The Composition creates an explicit
  {{<hover label="comp-python" line="67">}}Secret{{</hover>}} resource that
  represents the composite resource's connection details.
* The {{<hover label="comp-python" line="74">}}secret_name{{</hover>}} is set only after safely checking that the XR's
  {{<hover label="comp-python" line="73">}}.spec.writeConnectionSecretToRef.name{{</hover>}} field exists.
* Crossplane observes the connection details from each AccessKey and makes them
  available to the composition when the function is executed.
* The Secret reads connection details via
  {{<hover label="comp-python" line="81">}}req.observed.resources["accesskey-0"].connection_details{{</hover>}}
  from the observed composed resources.
* The {{<hover label="comp-python" line="80">}}if "accesskey-0" in req.observed.resources{{</hover>}}
  check handles the initial phase when composed resources are still being created.
* In `function-python`, connection details are **plaintext bytes**. To store them on the `Secret`, first
  convert them to strings with {{<hover label="comp-python" line="83">}}.decode("utf-8"){{</hover>}}
  and then save them using the secret's {{<hover label="comp-python" line="95">}}stringData{{</hover>}} field.

{{< /tab >}}

{{< tab "KCL" >}}

```yaml {label="comp-kcl"}
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
metadata:
  name: useraccesskeys-kcl
spec:
  compositeTypeRef:
    apiVersion: example.org/v1alpha1
    kind: UserAccessKey
  mode: Pipeline
  pipeline:
  - step: render-kcl
    functionRef:
      name: function-kcl
    input:
      apiVersion: krm.kcl.dev/v1alpha1
      kind: KCLInput
      spec:
        source: |
          oxr = option("params").oxr
          ocds = option("params").ocds

          user = {
              apiVersion = "iam.aws.m.upbound.io/v1beta1"
              kind = "User"
              metadata.annotations = {
                  "krm.kcl.dev/composition-resource-name" = "user"
              }
              spec.forProvider = {}
          }

          accesskey0 = {
              apiVersion = "iam.aws.m.upbound.io/v1beta1"
              kind = "AccessKey"
              metadata.annotations = {
                  "krm.kcl.dev/composition-resource-name" = "accesskey-0"
              }
              spec.forProvider.userSelector.matchControllerRef = True
              spec.writeConnectionSecretToRef.name = "${oxr.metadata.name}-accesskey-secret-0"
          }

          accesskey1 = {
              apiVersion = "iam.aws.m.upbound.io/v1beta1"
              kind = "AccessKey"
              metadata.annotations = {
                  "krm.kcl.dev/composition-resource-name" = "accesskey-1"
              }
              spec.forProvider.userSelector.matchControllerRef = True
              spec.writeConnectionSecretToRef.name = "${oxr.metadata.name}-accesskey-secret-1"
          }

          secret = {
              apiVersion = "v1"
              kind = "Secret"
              metadata.name = oxr?.spec?.writeConnectionSecretToRef?.name or ""
              metadata.annotations = {
                  "krm.kcl.dev/composition-resource-name" = "connection-secret"
              }
              data = {
                  "user-0" = ocds["accesskey-0"]?.ConnectionDetails?.username or ""
                  "user-1" = ocds["accesskey-1"]?.ConnectionDetails?.username or ""
                  "password-0" = ocds["accesskey-0"]?.ConnectionDetails?.password or ""
                  "password-1" = ocds["accesskey-1"]?.ConnectionDetails?.password or ""
              } if ocds else {}
          }

          items = [user, accesskey0, accesskey1, secret]
  - step: ready
    functionRef:
      name: function-auto-ready
```

**How this Composition exposes connection details:**

* Each composed {{<hover label="comp-kcl" line="31">}}AccessKey{{</hover>}} has
  {{<hover label="comp-kcl" line="38">}}writeConnectionSecretToRef{{</hover>}} set. This
  tells each AccessKey to write its credentials to an individual Secret.
* The Composition creates an explicit
  {{<hover label="comp-kcl" line="51">}}Secret{{</hover>}} resource that
  represents the composite resource's connection details.
* The {{<hover label="comp-kcl" line="54">}}name{{</hover>}} of the `Secret` is set using
  {{<hover label="comp-kcl" line="54">}}?.{{</hover>}} optional chaining operators to safely read the XR's
  {{<hover label="comp-kcl" line="54">}}.spec.writeConnectionSecretToRef.name{{</hover>}} field if it exists.
* Crossplane observes the connection details from each
  `AccessKey` and makes them available to the composition when the function is executed.
* The Secret reads connection details via
  {{<hover label="comp-kcl" line="59">}}ocds["accesskey-0"]?.ConnectionDetails?.username{{</hover>}}
  from the observed composed resources, safely handling the case where connection details don't exist yet.
* The {{<hover label="comp-kcl" line="63">}}if ocds else {}{{</hover>}} handles
  the phase when composed resources are still being created.
* In `function-kcl`, connection details are **already base64-encoded**, so you use them
  directly in the Secret's data field.

{{< /tab >}}

{{< /tabs >}}

Save the composition as `composition.yaml` and apply it:

```shell
kubectl apply -f composition.yaml
```

## Use the composite resource

The Composition now specifies how to compose connection details for the
`UserAccessKey` composite resource.

Create a `UserAccessKey` to see it in action:

```yaml
apiVersion: example.org/v1alpha1
kind: UserAccessKey
metadata:
  namespace: default
  name: my-keys
spec:
  writeConnectionSecretToRef:
    name: my-keys-connection-details
```

Save the composite resource as `my-keys.yaml` and apply it:

```shell
kubectl apply -f my-keys.yaml
```

Check that the composite resource is ready:

```shell {copy-lines="1"}
kubectl get -f my-keys.yaml
NAME      SYNCED   READY   COMPOSITION                    AGE
my-keys   True     True    useraccesskeys-go-templating   45s
```

{{<hint "note">}}
It may take a minute for AWS to provision the IAM resources. The composite
resource becomes `READY` when all composed resources are healthy.
{{</hint>}}

## Verify the connection details

Composite resources expose their connection details through a `Secret`. Check that
Crossplane created the `Secret`.

View all the composed resources (including the connection details `Secret`)
together using the `crossplane` CLI.

{{<hint "tip">}}
See the [Crossplane CLI docs]({{<ref "../cli">}}) to
learn how to install and use the Crossplane CLI.
{{< /hint >}}

```shell {copy-lines="1"}
crossplane beta trace useraccesskey.example.org/my-keys
NAME                                             SYNCED   READY   STATUS
UserAccessKey/my-keys (default)                  True     True    Available
├─ AccessKey/my-keys-14c0578cad85 (default)      True     True    Available
├─ AccessKey/my-keys-e420789d13a3 (default)      True     True    Available
├─ User/my-keys-c63b530f8e68 (default)           True     True    Available
└─ Secret/my-keys-connection-details (default)   -        -
```

The `my-keys` composite resource created an IAM `User` and two IAM `AccessKeys`,
and a `Secret` was also created that contains the aggregated connection details
for the composite resource.

Check the composite resource's aggregated connection details `Secret`:

```shell {copy-lines="1"}
kubectl get secret -n default -l crossplane.io/composite=my-keys
NAME                   TYPE     DATA   AGE
my-keys-586e2994bda1   Opaque   4      5m37s
```

{{<hint "tip">}}
The composite resource's connection details Secret has a label
`crossplane.io/composite=my-keys` that makes it easy to find.

If `.spec.writeConnectionSecretToRef.name` was set on the XR, then the `Secret`
will have that exact name.
{{</hint>}}

Verify the composite resource's connection details `Secret` contains all the
expected credentials:

```shell
kubectl get secret -n default -l crossplane.io/composite=my-keys -o jsonpath='{.items[0].data}' | jq
```

You should see output like this:

```json {copy-lines="none"}
{
  "password-0": "<base64-encoded-password>",
  "password-1": "<base64-encoded-password>",
  "user-0": "<base64-encoded-username>",
  "user-1": "<base64-encoded-username>"
}
```

Decode one of the values to verify it contains the expected data:

```shell
kubectl get secret -n default -l crossplane.io/composite=my-keys -o jsonpath='{.items[0].data.user-0}' | base64 -d
```

## Understanding how composing connection details works

Let's review the basic steps to expose connection details for a composite resource:

1. **Compose resources**: Create composed resources as usual in your
   composition, such as IAM `User` and `AccessKeys`. These resources will expose
   their connection details in a `Secret`.

2. **Set `writeConnectionSecretToRef`**: Each composed resource that should have
   connection details stored in their own individual `Secret` should have their
   `writeConnectionSecretToRef` set in the composition.

3. **Observed connection details**: Crossplane will observe the actual state of
   each composed resource, including its connection details, and make this data
   available when it calls the function.

4. **Compose the aggregate `Secret`**: With the observed connection details of
   your composed resources in hand, compose a `Secret` resource that combines
   the important connection details you want to expose for the XR.

5. **Safely handle transient state**: When your XR is first created, the
   composed resources and/or their connection details may not exist yet. Your
   Composition should safely handle these cases by checking if resources and
   their connection details exist before accessing them.


## Troubleshooting

### Composite resource's connection details Secret is empty

**Causes:**

* Composed resources don't have `writeConnectionSecretToRef` set
* Composed resources aren't ready/healthy yet
* Not handling initial nil state correctly in the Composition

**Solutions**:

* Verify `writeConnectionSecretToRef` is set on all composed managed resources
* Wait for composed resources to become ready (`kubectl get` and check `READY` column)
* Verify the composed resource is actually producing connection details:
  `kubectl get secret <composed-resource-secret-name> -o yaml`
* Add nil/empty checks in your Composition logic to safeguard access to data that may not exist yet

### Connection details are not encoded properly

**Cause:** Not encoding the aggregate secret data properly in your Composition logic

**Solution:** Ensure that your connection details data is properly encoded for
the function you're using. For example, `function-python` requires you to
convert connection details to base64-encoded strings, while connection details
in `function-go-templating` and `function-kcl` are already encoded this way and
require no conversion logic.

## Clean up

Delete the composite resource to clean-up:

```shell
kubectl delete -f my-keys.yaml
```

When you delete the composite resource, Crossplane deletes:

* The composed IAM `User` and `AccessKeys` from AWS
* The individual `Secrets` from composed resources
* The composite resource's connection details `Secret`

{{<hint "important">}}
Make sure to delete your composite resources before uninstalling the provider
or shutting down your control plane. If those are no longer running, they can't
clean up composed resources and you would need to delete them manually.
{{</hint>}}

## Learn more

* [Composite resources]({{<ref "../composition/composite-resources">}})
* [Compositions]({{<ref "../composition/compositions">}})
* [Write a composition function in Go]({{<ref "write-a-composition-function-in-go">}})
* [Write a composition function in Python]({{<ref "write-a-composition-function-in-python">}})
