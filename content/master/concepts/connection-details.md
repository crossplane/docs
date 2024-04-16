---
title: Connection Details
weight: 110
description: "How to create and manage connection details across Crossplane managed resources, composite resources, Compositions and Claims"
---

Using connection details in Crossplane requires the following components:
* Defining the `writeConnectionSecretToRef.name` in a [Claim]({{<ref "/master/concepts/claims#claim-connection-secrets">}}).
* Defining the `writeConnectionSecretsToNamespace` value in the [Composition]({{<ref "/master/concepts/compositions#composite-resource-combined-secret">}}).
* Define the `writeConnectionSecretToRef` name and namespace for each resource in the
  [Composition]({{<ref "/master/concepts/compositions#composed-resource-secrets">}}).
* Define the list of secret keys produced by each composed resource with `connectionDetails` in the
  [Composition]({{<ref "/master/concepts/compositions#define-secret-keys">}}).
* Optionally, define the `connectionSecretKeys` in a 
  [CompositeResourceDefinition]({{<ref "/master/concepts/composite-resource-definitions#manage-connection-secrets">}}).

{{<hint "note">}}
This guide discusses creating Kubernetes secrets.  
Crossplane also supports using external secret stores like [HashiCorp Vault](https://www.vaultproject.io/). 

Read the [external secrets store guide]({{<ref "../guides/vault-as-secret-store">}}) for more information on using Crossplane
with an external secret store. 
{{</hint >}}

## Background
When a [Provider]({{<ref "/master/concepts/providers">}}) creates a managed
resource, the resource may generate resource-specific details. These details can include 
usernames, passwords or connection details like an IP address.  

Crossplane refers to this information as the _connection details_ or 
_connection secrets_.   

The Provider
defines what information to present as a _connection
detail_ from a managed resource. 

<!-- vale gitlab.SentenceLength = NO -->
<!-- wordy because of type names -->
When a managed resource is part of a 
[Composition]({{<ref "/master/concepts/compositions">}}), the Composition, 
[Composite Resource Definition]({{<ref "/master/concepts/composite-resource-definitions">}}) 
and optionally, the 
[Claim]({{<ref "/master/concepts/claims">}}) define what details are visible
and where they're stored. 
<!-- vale gitlab.SentenceLength = YES -->

{{<hint "note">}}
All the following examples use the same set of Compositions,
CompositeResourceDefinitions and Claims.

All examples rely on 
[Upbound provider-aws-iam](https://marketplace.upbound.io/providers/upbound/provider-aws-iam/)
to create resources.

{{<expand "Reference Composition" >}}
```yaml
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
metadata:
  name: xsecrettest.example.org
spec:
  writeConnectionSecretsToNamespace: other-namespace
  compositeTypeRef:
    apiVersion: example.org/v1alpha1
    kind: XSecretTest
  resources:
    - name: key
      base:
        apiVersion: iam.aws.upbound.io/v1beta1
        kind: AccessKey
        spec:
          forProvider:
            userSelector:
              matchControllerRef: true
          writeConnectionSecretToRef:
            namespace: docs
            name: key1
      connectionDetails:
        - fromConnectionSecretKey: username
        - fromConnectionSecretKey: password
        - fromConnectionSecretKey: attribute.secret
        - fromConnectionSecretKey: attribute.ses_smtp_password_v4
      patches:
        - fromFieldPath: "metadata.uid"
          toFieldPath: "spec.writeConnectionSecretToRef.name"
          transforms:
            - type: string
              string:
                fmt: "%s-secret1"
    - name: user
      base:
        apiVersion: iam.aws.upbound.io/v1beta1
        kind: User
        spec:
          forProvider: {}
    - name: user2
      base:
        apiVersion: iam.aws.upbound.io/v1beta1
        kind: User
        metadata:
          labels:
            docs.crossplane.io: user
        spec:
          forProvider: {}
    - name: key2
      base:
        apiVersion: iam.aws.upbound.io/v1beta1
        kind: AccessKey
        spec:
          forProvider:
            userSelector:
              matchLabels:
                docs.crossplane.io: user
          writeConnectionSecretToRef:
            namespace: docs
            name: key2
      connectionDetails:
        - name: key2-user
          fromConnectionSecretKey: username
        - name: key2-password
          fromConnectionSecretKey: password
        - name: key2-secret
          fromConnectionSecretKey: attribute.secret
        - name: key2-smtp
          fromConnectionSecretKey: attribute.ses_smtp_password_v4
      patches:
        - fromFieldPath: "metadata.uid"
          toFieldPath: "spec.writeConnectionSecretToRef.name"
          transforms:
            - type: string
              string:
                fmt: "%s-secret2"
```
{{</expand >}}

{{<expand "Reference CompositeResourceDefinition" >}}

```yaml
apiVersion: apiextensions.crossplane.io/v1
kind: CompositeResourceDefinition
metadata:
  name: xsecrettests.example.org
spec:
  group: example.org
  connectionSecretKeys:
    - username
    - password
    - attribute.secret
    - attribute.ses_smtp_password_v4
    - key2-user
    - key2-pass
    - key2-secret
    - key2-smtp
  names:
    kind: XSecretTest
    plural: xsecrettests
  claimNames:
    kind: SecretTest
    plural: secrettests
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
```
{{</ expand >}}

{{<expand "Reference Claim" >}}
```yaml
apiVersion: example.org/v1alpha1
kind: SecretTest
metadata:
  name: test-secrets
  namespace: default
spec:
  writeConnectionSecretToRef:
    name: my-access-key-secret
```
{{</expand >}}
{{</hint >}}

## Connection secrets in a managed resource

<!-- vale gitlab.Substitutions = NO -->
<!-- vale gitlab.SentenceLength = NO -->
<!-- under 25 words -->
When a managed resource creates connection secrets, Crossplane can write the 
secrets to a 
[Kubernetes secret]({{<ref "/master/concepts/managed-resources#publish-secrets-to-kubernetes">}})
or an 
[external secret store]({{<ref "/master/concepts/managed-resources#publish-secrets-to-an-external-secrets-store">}}).
<!-- vale gitlab.SentenceLength = YES -->
<!-- vale gitlab.Substitutions = YES -->

Creating an individual managed resource shows the connection secrets the
resource creates. 

{{<hint "note" >}}
Read the [managed resources]({{<ref "/master/concepts/managed-resources">}})
documentation for more information on configuring resources and storing
connection secrets for individual resources. 
{{< /hint >}}


For example, create an
{{<hover label="mr" line="2">}}AccessKey{{</hover>}} resource and save the
connection secrets in a Kubernetes secret named 
{{<hover label="mr" line="12">}}my-accesskey-secret{{</hover>}}
in the 
{{<hover label="mr" line="11">}}default{{</hover>}} namespace. 

```yaml {label="mr"}
apiVersion: iam.aws.upbound.io/v1beta1
kind: AccessKey
metadata:
    name: test-accesskey
spec:
    forProvider:
        userSelector:
            matchLabels:
                docs.crossplane.io: user
    writeConnectionSecretToRef:
        namespace: default
        name: my-accesskey-secret
```

View the Kubernetes secret to see the connection details from the managed
resource.  
This includes an 
{{<hover label="mrSecret" line="11">}}attribute.secret{{</hover>}},
{{<hover label="mrSecret" line="12">}}attribute.ses_smtp_password_v4{{</hover>}},
{{<hover label="mrSecret" line="13">}}password{{</hover>}} and 
{{<hover label="mrSecret" line="14">}}username{{</hover>}}

```yaml {label="mrSecret",copy-lines="1"}
kubectl describe secret my-accesskey-secret
Name:         my-accesskey-secret
Namespace:    default
Labels:       <none>
Annotations:  <none>

Type:  connection.crossplane.io/v1alpha1

Data
====
attribute.secret:                40 bytes
attribute.ses_smtp_password_v4:  44 bytes
password:                        40 bytes
username:                        20 bytes
```

Compositions and CompositeResourceDefinitions require the exact names of the
secrets generated by a resource. 

## Connection secrets in Compositions

Resources in a Composition that create connection details still create a
secret object containing their connection details.  
Crossplane also generates
another secret object for each composite resource, 
containing the secrets from all the defined resources.

For example, a Composition defines two 
{{<hover label="comp1" line="9">}}AccessKey{{</hover>}}
objects.  
Each {{<hover label="comp1" line="9">}}AccessKey{{</hover>}} writes a
connection secrets to the {{<hover label="comp1" line="15">}}name{{</hover>}}
inside the {{<hover label="comp1" line="14">}}namespace{{</hover>}} defined by
the resource 
{{<hover label="comp1" line="13">}}writeConnectionSecretToRef{{</hover>}}.

Crossplane also creates a secret object for the entire Composition 
saved in the namespace defined by 
{{<hover label="comp1" line="4">}}writeConnectionSecretsToNamespace{{</hover>}}
with a Crossplane generated name. 

```yaml {label="comp1",copy-lines="none"}
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
spec:
  writeConnectionSecretsToNamespace: other-namespace
  resources:
    - name: key1
      base:
        apiVersion: iam.aws.upbound.io/v1beta1
        kind: AccessKey
        spec:
          forProvider:
            # Removed for brevity
          writeConnectionSecretToRef:
            namespace: docs
            name: key1-secret
    - name: key2
      base:
        apiVersion: iam.aws.upbound.io/v1beta1
        kind: AccessKey
        spec:
          forProvider:
            # Removed for brevity
          writeConnectionSecretToRef:
            namespace: docs
            name: key2-secret
    # Removed for brevity
```

After applying a Claim, view the Kubernetes secrets to see three secret objects
created. 

The secret 
{{<hover label="compGetSec" line="3">}}key1-secret{{</hover>}} is from the resource 
{{<hover label="comp1" line="6">}}key1{{</hover>}}, 
{{<hover label="compGetSec" line="4">}}key2-secret{{</hover>}} is from the resource 
{{<hover label="comp1" line="16">}}key2{{</hover>}}.

Crossplane creates another secret in the namespace 
{{<hover label="compGetSec" line="5">}}other-namespace{{</hover>}} with the
secrets from resource in the Composition. 


```shell {label="compGetSec",copy-lines="1"}
kubectl get secrets -A
NAMESPACE           NAME                                   TYPE                                DATA   AGE
docs                key1-secret                            connection.crossplane.io/v1alpha1   4      4s
docs                key2-secret                            connection.crossplane.io/v1alpha1   4      4s
other-namespace     70975471-c44f-4f6d-bde6-6bbdc9de1eb8   connection.crossplane.io/v1alpha1   0      6s
```

Although Crossplane creates a secret object, by default, Crossplane doesn't add
any data to the object. 

```yaml {copy-lines="none"}
kubectl describe secret 70975471-c44f-4f6d-bde6-6bbdc9de1eb8 -n other-namespace
Name:         70975471-c44f-4f6d-bde6-6bbdc9de1eb8
Namespace:    other-namespace

Type:  connection.crossplane.io/v1alpha1

Data
====
```

The Composition must list the connection secrets to store for each resource.  
Use the 
{{<hover label="comp2" line="16">}}connectionDetails{{</hover>}} object under
each resource and define the secret keys the resource creates.  


{{<hint "warning">}}
You can't change the 
{{<hover label="comp2" line="16">}}connectionDetails{{</hover>}} 
of a Composition.  
You must delete and
recreate the Composition to change the 
{{<hover label="comp2" line="16">}}connectionDetails{{</hover>}}.  
{{</hint >}}

```yaml {label="comp2",copy-lines="16-20"}
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
spec:
  writeConnectionSecretsToNamespace: other-namespace
  resources:
    - name: key
      base:
        apiVersion: iam.aws.upbound.io/v1beta1
        kind: AccessKey
        spec:
          forProvider:
            # Removed for brevity
          writeConnectionSecretToRef:
            namespace: docs
            name: key1
      connectionDetails:
        - fromConnectionSecretKey: username
        - fromConnectionSecretKey: password
        - fromConnectionSecretKey: attribute.secret
        - fromConnectionSecretKey: attribute.ses_smtp_password_v4
    # Removed for brevity
```

After applying a Claim the composite resource secret object contains the list of
keys listed in the
{{<hover label="comp2" line="16">}}connectionDetails{{</hover>}}.

```shell {copy-lines="1"}
kubectl describe secret -n other-namespace
Name:         b0dc71f8-2688-4ebc-818a-bbad6a2c4f9a
Namespace:    other-namespace

Type:  connection.crossplane.io/v1alpha1

Data
====
username:                        20 bytes
attribute.secret:                40 bytes
attribute.ses_smtp_password_v4:  44 bytes
password:                        40 bytes
```

{{<hint "important">}}
If a key isn't listed in the 
{{<hover label="comp2" line="16">}}connectionDetails{{</hover>}}
it isn't stored in the secret object.
{{< /hint >}}

### Managing conflicting secret keys 
If resources produce conflicting keys, create a unique name with a connection
details
{{<hover label="comp3" line="25">}}name{{</hover>}}.

```yaml {label="comp3",copy-lines="none"}
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
spec:
  writeConnectionSecretsToNamespace: other-namespace
  resources:
    - name: key
      base:
        kind: AccessKey
        spec:
          # Removed for brevity
          writeConnectionSecretToRef:
            namespace: docs
            name: key1
      connectionDetails:
        - fromConnectionSecretKey: username
    - name: key2
      base:
        kind: AccessKey
        spec:
          # Removed for brevity
          writeConnectionSecretToRef:
            namespace: docs
            name: key2
      connectionDetails:
        - name: key2-user
          fromConnectionSecretKey: username
```

The secret object contains both keys, 
{{<hover label="comp3Sec" line="9">}}username{{</hover>}}
and
{{<hover label="comp3Sec" line="10">}}key2-user{{</hover>}}

```shell {label="comp3Sec",copy-lines="1"}
kubectl describe secret -n other-namespace
Name:         b0dc71f8-2688-4ebc-818a-bbad6a2c4f9a
Namespace:    other-namespace

Type:  connection.crossplane.io/v1alpha1

Data
====
username:                        20 bytes
key2-user:                       20 bytes
# Removed for brevity.
```

## Connection secrets in Composite Resource Definitions

The CompositeResourceDefinition (`XRD`), can restrict which secrets keys are 
put in the combined secret and provided to a Claim. 

By default an XRD writes all secret keys listed in the composed resource 
`connectionDetails` to the combined secret object.

Limit the keys passed to the combined secret object and Claims with a
{{<hover label="xrd" line="4">}}connectionSecretKeys{{</hover>}} object.

Inside the {{<hover label="xrd" line="4">}}connectionSecretKeys{{</hover>}} list
the secret key names to create. Crossplane only adds the keys listed to the
combined secret.

{{<hint "warning">}}
You can't change the 
{{<hover label="xrd" line="4">}}connectionSecretKeys{{</hover>}} of an XRD. 
You must delete and
recreate the XRD to change the 
{{<hover label="xrd" line="4">}}connectionSecretKeys{{</hover>}}.
{{</hint >}}

For example, an XRD may restrict the secrets to only the 
{{<hover label="xrd" line="5">}}username{{</hover>}},
{{<hover label="xrd" line="6">}}password{{</hover>}} and custom named
{{<hover label="xrd" line="7">}}key2-user{{</hover>}} keys. 

```yaml {label="xrd",copy-lines="4-12"}
kind: CompositeResourceDefinition
spec:
  # Removed for brevity.
  connectionSecretKeys:
    - username
    - password
    - key2-user
```

The secret from an individual resource contains all the resources detailed in
the Composition's `connectionDetails`. 

```shell {label="xrdSec",copy-lines="1"}
kubectl describe secret key1 -n docs
Name:         key1
Namespace:    docs

Data
====
password:                        40 bytes
username:                        20 bytes
attribute.secret:                40 bytes
attribute.ses_smtp_password_v4:  44 bytes
```

The Claim's secret only contains the
keys allowed by the XRD 
{{<hover label="xrd" line="4">}}connectionSecretKeys{{</hover>}} 
fields. 

```shell {label="xrdSec2",copy-lines="2"}
kubectl describe secret my-access-key-secret
Name:         my-access-key-secret

Data
====
key2-user:  20 bytes
password:   40 bytes
username:   20 bytes
```

## Secret objects
Compositions create a secret object for each resource and an extra secret
containing all the secrets from all resources. 

Crossplane saves the resource secret objects in the location defined by the
resource's 
{{<hover label="comp4" line="11">}}writeConnectionSecretToRef{{</hover>}}.

Crossplane saves the combined secret with a Crossplane generated name in the
namespace defined in the Composition's 
{{<hover label="comp4" line="4">}}writeConnectionSecretsToNamespace{{</hover>}}.

```yaml {label="comp4",copy-lines="none"}
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
spec:
  writeConnectionSecretsToNamespace: other-namespace
  resources:
    - name: key
      base:
        kind: AccessKey
        spec:
          # Removed for brevity
          writeConnectionSecretToRef:
            namespace: docs
            name: key1
      connectionDetails:
        - fromConnectionSecretKey: username
    - name: key2
      base:
        kind: AccessKey
        spec:
          # Removed for brevity
          writeConnectionSecretToRef:
            namespace: docs
            name: key2
      connectionDetails:
        - name: key2-user
          fromConnectionSecretKey: username
```

If a Claim uses a secret, it's stored in the same namespace as the Claim with
the name defined in the Claim's 
{{<hover label="claim3" line="7">}}writeConnectionSecretToRef{{</hover>}}.

```yaml {label="claim3",copy-lines="none"}
apiVersion: example.org/v1alpha1
kind: SecretTest
metadata:
  name: test-secrets
  namespace: default
spec:
  writeConnectionSecretToRef:
    name: my-access-key-secret
```

After applying the Claim Crossplane creates the following secrets:
* The Claim's secret, {{<hover label="allSec" line="3">}}my-access-key-secret{{</hover>}} 
  in the Claim's {{<hover label="claim3" line="5">}}namespace{{</hover>}}.
* The first resource's secret object, {{<hover label="allSec" line="4">}}key1{{</hover>}}.
* The second resource's secret object, {{<hover label="allSec" line="5">}}key2{{</hover>}}.
* The composite resource secret object in the 
  {{<hover label="allSec" line="6">}}other-namespace{{</hover>}} defined by the
  Composition's `writeConnectionSecretsToNamespace`.
  

```shell {label="allSec",copy-lines="none"}
 kubectl get secret -A
NAMESPACE           NAME                                   TYPE                                DATA   AGE
default             my-access-key-secret                   connection.crossplane.io/v1alpha1   8      29m
docs                key1                                   connection.crossplane.io/v1alpha1   4      31m
docs                key2                                   connection.crossplane.io/v1alpha1   4      31m
other-namespace     b0dc71f8-2688-4ebc-818a-bbad6a2c4f9a   connection.crossplane.io/v1alpha1   8      31m
```