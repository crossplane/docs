---
title: Connection Details
weight: 20
description: "How to create and manage connection details across Crossplane managed resources, composite resources and Compositions"
---

## Background

When a provider creates a managed resource, the resource may generate
resource-specific details. These details can include usernames, passwords or
connection details like an IP address.  

Crossplane refers to this information as the _connection details_ or 
_connection secrets_.   

The Provider defines what information to present as a _connection detail_ from a
managed resource. 

## Connection secrets in a managed resource

Creating an individual managed resource shows the connection secrets the
resource creates. 

{{<hint "note" >}}
Read the [managed resources]({{<ref "managed-resources">}}) documentation for
more information on configuring resources and storing connection secrets for
individual resources. 
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
    namespace: default
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
