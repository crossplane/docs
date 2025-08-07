---
title: Get Started with Managed Resource Definitions
weight: 220
description: Learn how to use MRDs and activation policies to optimize your Crossplane installation
---

This guide shows how to use Managed Resource Definitions (MRDs) and activation 
policies to control which managed resources are available in your cluster. 
You install a provider, examine its MRDs, and use policies to activate only 
the resources you need.

{{< hint "tip" >}}
This guide demonstrates the performance and discovery benefits of MRDs by 
working with a subset of AWS resources rather than installing hundreds of CRDs.
{{< /hint >}}

By the end of this guide, you understand how to:
* Examine MRDs created by provider packages
* Use activation policies to control resource availability
* Discover connection details through MRD schemas
* Optimize cluster performance by activating only needed resources

## Prerequisites

This guide requires:

* A Kubernetes cluster with at least 2 GB of RAM
* Crossplane v2.0+ [installed on the cluster]({{< ref "install" >}})
* `kubectl` configured to access your cluster

## Understand the default activation policy

Before installing providers, it's important to understand Crossplane's default 
activation behavior. Crossplane creates a default ManagedResourceActivationPolicy 
that, by default, activates **all** managed resources with a `"*"` pattern.

{{< hint "important" >}}
The default `"*"` activation pattern defeats the performance benefits of 
safe-start by activating all resources. For this tutorial, the guide works with the 
default behavior, but production setups should use more selective activation.
{{< /hint >}}

Check if you have a default activation policy:

```shell
kubectl get mrap crossplane-default-activation-policy -o yaml
```

You can edit the default activation policy directly:

{{< tabs >}}
{{< tab "Edit Existing Policy" >}}
```shell
# Permanently disable by using a non-matching pattern
kubectl patch mrap crossplane-default-activation-policy --type='merge' \
  -p='{"spec":{"activations":["nonexistent.example.com"]}}'

# Or remove all activations entirely
kubectl patch mrap crossplane-default-activation-policy --type='merge' \
  -p='{"spec":{"activations":[]}}'
```

{{< hint "note" >}}
Changes to the default policy are permanent. After the policy exists, Crossplane 
doesn't change it, even if you change Helm values.
{{< /hint >}}
{{< /tab >}}

{{< tab "Reset with Helm Values" >}}
```shell
# Delete the default policy and restart Crossplane to recreate from Helm values
kubectl delete mrap crossplane-default-activation-policy
helm upgrade crossplane crossplane-stable/crossplane \
  --set provider.defaultActivations=null \
  --namespace crossplane-system --reuse-values
kubectl rollout restart deployment/crossplane -n crossplane-system
```

This approach lets you use Helm chart values to control the default policy.
{{< /tab >}}
{{< /tabs >}}

{{< hint "tip" >}}
Learn more about configuring default activation policies during installation 
and best practices in the [MRD activation policies guide]({{< ref "../guides/mrd-activation-policies#default-activation-policy" >}}).
{{< /hint >}}

## Install a provider with safe-start capability

Now install a provider that supports safe-start. This provider creates MRDs 
that activation policies control.

```yaml
apiVersion: pkg.crossplane.io/v1
kind: Provider
metadata:
  name: provider-aws
spec:
  package: xpkg.upbound.io/crossplane-contrib/provider-aws:v0.45.0
```

Apply this configuration:

```shell
kubectl apply -f - <<EOF
apiVersion: pkg.crossplane.io/v1
kind: Provider
metadata:
  name: provider-aws
spec:
  package: xpkg.upbound.io/crossplane-contrib/provider-aws:v0.45.0
EOF
```

Wait for the provider to become healthy:

```shell
kubectl get providers
```

```shell
NAME           INSTALLED   HEALTHY   PACKAGE                                             AGE
provider-aws   True        True      xpkg.upbound.io/crossplane-contrib/provider-aws   2m
```

## Examine the managed resource definitions

List the MRDs created by the provider:

```shell
kubectl get mrds
```

The MRD states depend on your default activation policy:

{{< tabs >}}
{{< tab "With Default Activation (default)" >}}
If you kept the default `"*"` activation pattern:

```shell
NAME                                    STATE      AGE
buckets.s3.aws.crossplane.io          Active     2m
instances.ec2.aws.crossplane.io       Active     2m  
databases.rds.aws.crossplane.io       Active     2m
clusters.eks.aws.crossplane.io        Active     2m
# ... many more, all Active
```

The default policy activates all MRDs, so safe-start providers behave like 
traditional providers.
{{< /tab >}}

{{< tab "With Disabled Default Activation" >}}
If you disabled default activation:

```shell
NAME                                    STATE      AGE
buckets.s3.aws.crossplane.io          Inactive   2m
instances.ec2.aws.crossplane.io       Inactive   2m
databases.rds.aws.crossplane.io       Inactive   2m
clusters.eks.aws.crossplane.io        Inactive   2m
# ... many more, all Inactive
```

This demonstrates true safe-start behavior where resources must be explicitly 
activated.
{{< /tab >}}
{{< /tabs >}}

{{< hint "note" >}}
For the rest of this tutorial, the guide assumes you have default activation 
disabled to show selective activation. If you have default activation 
enabled, the MRDs are already active.
{{< /hint >}}

Examine a specific MRD to understand its schema and connection details:

```shell
kubectl get mrd instances.ec2.aws.crossplane.io -o yaml
```

Look for the `connectionDetails` section:

```yaml
spec:
  connectionDetails:
  - description: The public IP address assigned to the instance
    name: public_ip
    type: string
  - description: The private IP address assigned to the instance  
    name: private_ip
    type: string
  - description: The public DNS name assigned to the instance
    name: public_dns
    type: string
```

## Verify resource creation behavior

The presence of CRDs depends on whether MRDs are active:

{{< tabs >}}
{{< tab "With Default Activation (default)" >}}
Because MRDs are active due to the default `"*"` policy, CRDs exist:

```shell
kubectl get crds | grep aws.crossplane.io | wc -l
```

This shows 100+ CRDs, demonstrating that active MRDs 
create CRDs.
{{< /tab >}}

{{< tab "With Disabled Default Activation" >}}
Because the MRDs are inactive, no CRDs should exist for AWS resources:

```shell
kubectl get crds | grep aws.crossplane.io
```

This should return no results, demonstrating that inactive MRDs don't create 
CRDs in your cluster.
{{< /tab >}}
{{< /tabs >}}

## Create an activation policy

Create a ManagedResourceActivationPolicy to activate specific AWS resources:

```yaml
apiVersion: apiextensions.crossplane.io/v1alpha1
kind: ManagedResourceActivationPolicy
metadata:
  name: aws-demo-resources
spec:
  activations:
  - instances.ec2.aws.crossplane.io
  - buckets.s3.aws.crossplane.io
  - "*.rds.aws.crossplane.io"
```

Apply the policy:

```shell
kubectl apply -f - <<EOF
apiVersion: apiextensions.crossplane.io/v1alpha1
kind: ManagedResourceActivationPolicy
metadata:
  name: aws-demo-resources
spec:
  activations:
  - instances.ec2.aws.crossplane.io
  - buckets.s3.aws.crossplane.io
  - "*.rds.aws.crossplane.io"
EOF
```

This policy activates:
* EC2 instances (exact match)
* S3 buckets (exact match)  
* All RDS resources (wildcard match)

## Verify activation

Check that the specified MRDs are now active:

```shell
kubectl get mrds instances.ec2.aws.crossplane.io buckets.s3.aws.crossplane.io
```

```shell
NAME                              STATE    AGE
instances.ec2.aws.crossplane.io   Active   5m
buckets.s3.aws.crossplane.io     Active   5m
```

List all RDS MRDs to see they're also active:

```shell
kubectl get mrds | grep rds
```

```shell
NAME                                      STATE    AGE
clusters.rds.aws.crossplane.io           Active   5m
databases.rds.aws.crossplane.io          Active   5m
dbinstances.rds.aws.crossplane.io        Active   5m
# ... other RDS resources
```

## Verify custom resource definition creation

Now that MRDs are active, CRDs exist:

```shell
kubectl get crds | grep -E "(instances.ec2|buckets.s3|rds)" | head -5
```

```shell
buckets.s3.aws.crossplane.io                    2024-01-15T10:30:00Z
clusters.rds.aws.crossplane.io                  2024-01-15T10:30:00Z
databases.rds.aws.crossplane.io                 2024-01-15T10:30:00Z
dbinstances.rds.aws.crossplane.io               2024-01-15T10:30:00Z
instances.ec2.aws.crossplane.io                 2024-01-15T10:30:00Z
```

## Create a managed resource

Now you can create managed resources using the active MRDs. Create an S3 bucket:

```yaml
apiVersion: s3.aws.crossplane.io/v1alpha1
kind: Bucket
metadata:
  name: my-demo-bucket
spec:
  forProvider:
    region: us-east-1
  providerConfigRef:
    name: default
```

{{< hint "note" >}}
This example assumes you have AWS credentials configured. See 
[ProviderConfig documentation]({{< ref "../managed-resources/managed-resources#providerconfigref" >}}) for 
authentication setup.
{{< /hint >}}

```shell
kubectl apply -f - <<EOF
apiVersion: s3.aws.crossplane.io/v1alpha1
kind: Bucket
metadata:
  name: my-demo-bucket
spec:
  forProvider:
    region: us-east-1
  providerConfigRef:
    name: default
EOF
```

## Test inactive resources

Try to create a managed resource for an inactive MRD, like EKS clusters:

```shell
kubectl get mrd clusters.eks.aws.crossplane.io
```

```shell
NAME                              STATE      AGE
clusters.eks.aws.crossplane.io   Inactive   8m
```

Attempting to create an EKS cluster fails because the CRD doesn't exist:

```shell
kubectl apply -f - <<EOF
apiVersion: eks.aws.crossplane.io/v1alpha1
kind: Cluster
metadata:
  name: test-cluster
spec:
  forProvider:
    region: us-east-1
    version: "1.21"
EOF
```

```shell
error validating data: ValidationError(Cluster): unknown field "apiVersion" in io.k8s.api.core.v1.Cluster
```

## Expand activation with wildcards

Add more resources using wildcard patterns. Update your activation policy:

```shell
kubectl patch mrap aws-demo-resources --type merge -p '{
  "spec": {
    "activations": [
      "instances.ec2.aws.crossplane.io",
      "buckets.s3.aws.crossplane.io", 
      "*.rds.aws.crossplane.io",
      "*.eks.aws.crossplane.io"
    ]
  }
}'
```

Verify EKS resources are now active:

```shell
kubectl get mrds | grep eks
```

```shell
NAME                                STATE    AGE
clusters.eks.aws.crossplane.io     Active   10m
nodegroups.eks.aws.crossplane.io   Active   10m
```

## Examine activation policy status

Check which MRDs your policy has activated:

```shell
kubectl get mrap aws-demo-resources -o yaml
```

Look for the `status.activated` field:

```yaml
status:
  activated:
  - buckets.s3.aws.crossplane.io
  - instances.ec2.aws.crossplane.io
  - clusters.rds.aws.crossplane.io
  - databases.rds.aws.crossplane.io
  - clusters.eks.aws.crossplane.io
  - nodegroups.eks.aws.crossplane.io
  # ... other activated MRDs
```

## Performance comparison

Compare the resource usage with traditional provider installation:

**Without MRDs (traditional):**
- All ~200 AWS CRDs created when provider installs
- Higher memory usage in kube-apiserver
- Longer provider installation time

**With MRDs and selective activation:**
- Only activated CRDs created (10 to 20 in this example)
- Lower memory footprint
- Faster resource discovery and management

Check the number of AWS CRDs in your cluster:

```shell
kubectl get crds | grep aws.crossplane.io | wc -l
```

This should be much smaller than the total number of MRDs.

## Multiple activation policies

You can create multiple MRAPs for different use cases. Create a second policy 
for development environments:

```shell
kubectl apply -f - <<EOF
apiVersion: apiextensions.crossplane.io/v1alpha1
kind: ManagedResourceActivationPolicy
metadata:
  name: aws-dev-resources
spec:
  activations:
  - "*.ec2.aws.crossplane.io"
  - "*.iam.aws.crossplane.io"
EOF
```

Both policies combine their activations, giving you fine-grained 
control over resource availability.

## Clean up

Remove the demo resources:

```shell
kubectl delete bucket my-demo-bucket
kubectl delete mrap aws-demo-resources aws-dev-resources
kubectl delete provider provider-aws
```

## Production recommendations

For production Crossplane deployments, follow these best practices:

### 1. Disable default activation

Install Crossplane with selective activation:

```shell
helm install crossplane crossplane-stable/crossplane \
  --set provider.defaultActivations=null \
  --namespace crossplane-system
```

### 2. Use targeted activation policies

Create provider-specific policies rather than using the default `"*"` pattern:

```yaml
apiVersion: apiextensions.crossplane.io/v1alpha1
kind: ManagedResourceActivationPolicy
metadata:
  name: production-aws-resources
spec:
  activations:
  - "instances.ec2.aws.crossplane.io"
  - "*.rds.aws.crossplane.io"
  - "buckets.s3.aws.crossplane.io"
  - "*.iam.aws.crossplane.io"
```

### 3. Environment-specific policies

Use different activation strategies per environment:

* **Development**: Broad activation for experimentation
* **Staging**: Subset of production resources for testing
* **Production**: Minimal, specific activation for performance

## Next steps

Now that you understand MRDs and activation policies, you can:

* **Optimize cluster performance** by using selective activation
* **Improve resource discovery** through MRD connection details documentation
* **Implement environment-specific policies** for different deployment stages
* **Plan provider adoption** using safe-start-capable providers

Learn more about:
* [MRD activation policies best practices]({{< ref "../guides/mrd-activation-policies" >}}) - Comprehensive guide including default policy configuration
* [Managed Resource Definitions concepts]({{< ref "managed-resource-definitions" >}})
* [Provider capabilities and safe-start]({{< ref "../packages/provider-capabilities" >}})