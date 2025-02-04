---
title: Working without RBAC Manager
weight: 280
---

RBAC Manager is responsible for granting appropriate permissions to components.

In cases, where administrators are not allowing permissive cluster wide-permissions,you can turn off RBAC Manager
with argument `--set rbacManager.deploy=false` in [helm chart](https://github.com/crossplane/crossplane/blob/main/cluster/charts/crossplane/README.md#configuration).
```yaml {label="value",copy-lines="none"}
rbacManager:
  enabled: false
```

Once done, you need to configure custom permissions for each provider and custom resource definition. Below guides
will instruct you step by step the additional work needed for each provider and XRD.

## Provider RBAC

> Note: Please keep in mind this guide doesn't show manual steps for installing providers. If you want to control Crossplane Core pod permissions even further, you can manually install the provider service.

For the prpose of this guide, let's assume you want to deploy a `provider-kubernetes` to the cluster and control its
permissions. You create a resource provider as usual
```yaml
apiVersion: pkg.crossplane.io/v1
kind: Provider
metadata:
  name: provider-kubernetes
spec:
  package: xpkg.upbound.io/crossplane-contrib/provider-kubernetes:v0.15.1
```
Once installed, save provider service account name
```sh
SA=$(kubectl -n crossplane-system get sa -o name | grep provider-kubernetes | sed -e 's|serviceaccount\/||g')
```

### ClusterRole for provider

Then, create a ClusterRole, that will have necessary rules for resources that are to be managed by a provider:
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: provider-kubernetes-aggregate
rules:
- apiGroups:
  - kubernetes.crossplane.io
  resources:
  - objects
  - objects/status
  - observedobjectcollections
  - observedobjectcollections/status
  - providerconfigs
  - providerconfigs/status
  - providerconfigusages
  - providerconfigusages/status
  verbs:
  - get
  - list
  - watch
  - update
  - patch
  - create
- apiGroups:
  - kubernetes.crossplane.io
  resources:
  - '*/finalizers'
  verbs:
  - update
- apiGroups:
  - ""
  - coordination.k8s.io
  resources:
  - secrets
  - configmaps
  - events
  - leases
  verbs:
  - '*'
```

With the role, now create a binding to the service account:
> Note: make sure that the `SA` environment variable that was defined earlier is still set correctly.
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: provider-kubernetes-binding
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: provider-kubernetes-aggregate
subjects:
- kind: ServiceAccount
  name: ${SA}
  namespace: crossplane-system
```

### ClusterRole for core Crossplane

Now, create a new ClusterRole, for core Crossplane service
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: provider-kubernetes-aggregate
rules:
- apiGroups:
  - kubernetes.crossplane.io
  resources:
  - objects
  - objects/status
  - observedobjectcollections
  - observedobjectcollections/status
  - providerconfigs
  - providerconfigs/status
  - providerconfigusages
  - providerconfigusages/status
  verbs:
  - '*'
```

With the cluster role in place, create a binding to the core Crossplane service:
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: crossplane-provider-kubernetes-binding
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: crossplane-aggregate-provider-access
subjects:
- kind: ServiceAccount
  name: crossplane
  namespace: crossplane-system
```

### Verification
With the previous steps applied, you can now verify the configuration by adding a provider config:
```yaml
apiVersion: kubernetes.crossplane.io/v1alpha1
kind: ProviderConfig
metadata:
  name: kubernetes-provider-config
spec:
  credentials:
    source: InjectedIdentity
```
And add a binding, so that it's possible to manage local cluster by a provider:
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: provider-kubernetes-admin-binding
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: cluster-admin
subjects:
- kind: ServiceAccount
  name: ${SA}
  namespace: crossplane-system
```

With the configuration in place, you can add a test resource:
```yaml
apiVersion: kubernetes.crossplane.io/v1alpha2
kind: Object
metadata:
  name: test-namespace
spec:
  forProvider:
    manifest:
      apiVersion: v1
      kind: Namespace
      metadata:
        name: test-namespace
        labels:
          example: 'true'
  providerConfigRef:
    name: kubernetes-provider-config
```

## Compositions
If you want to add a CompositionResourceDefinition in a system without RBAC Manager, you need to create the
necessary XRD definition as well as assign permissions to the defined type to Core Crossplane ServiceAccount.

For the purpose of the example, let's create a sample XRD:
```yaml
apiVersion: apiextensions.crossplane.io/v1
kind: CompositeResourceDefinition
metadata:
  name: compositenamespaces.k8s.crossplane.io
spec:
  group: k8s.crossplane.io
  names:
    kind: CompositeNamespace
    plural: compositenamespaces
  claimNames:
    kind: NamespaceClaim
    plural: namespaceclaims
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
                name:
                  type: string
                  description: "The name of the Kubernetes namespace to be created."
            status:
              type: object
              properties:
                ready:
                  type: boolean
                  description: "Indicates if the namespace is ready."
```

After that, create a ClusterRole:
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: compositenamespace:aggregate-to-crossplane
rules:
- apiGroups:
  - k8s.crossplane.io
  resources:
  - compositenamespaces
  - compositenamespaces/status
  verbs:
  - '*'
- apiGroups:
  - k8s.crossplane.io
  resources:
  - compositenamespaces/finalizers
  verbs:
  - update
- apiGroups:
  - k8s.crossplane.io
  resources:
  - namespaceclaims
  - namespaceclaims/status
  verbs:
  - '*'
- apiGroups:
  - k8s.crossplane.io
  resources:
  - namespaceclaims/finalizers
  verbs:
  - update
```

If the ServiceAccount for your Core Crossplane service is default `crossplane`, apply below binding:
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: crossplane-provider-kubernetes-binding-CRD
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: compositenamespace:aggregate-to-crossplane
subjects:
- kind: ServiceAccount
  name: crossplane
  namespace: crossplane-system
```

### Verification

Once proper permissions are applied, you can create a composition:
```yaml
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
metadata:
  name: compositenamespace.k8s.crossplane.io
spec:
  compositeTypeRef:
    apiVersion: k8s.crossplane.io/v1alpha1
    kind: CompositeNamespace
  resources:
    - name: namespace
      base:
        apiVersion: kubernetes.crossplane.io/v1alpha2
        kind: Object
        spec:
          providerConfigRef:
            name: kubernetes-provider-config
          forProvider:
            manifest:
              apiVersion: v1
              kind: Namespace
      patches:
        - fromFieldPath: "spec.name"
          toFieldPath: "metadata.name"
          type: FromCompositeFieldPath
```

Followed by a Claim creation
```yaml
apiVersion: k8s.crossplane.io/v1alpha1
kind: NamespaceClaim
metadata:
  name: example-namespace-claim
spec:
  name: testing-no-rbac
```
