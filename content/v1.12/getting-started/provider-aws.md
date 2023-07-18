---
title: AWS Quickstart
weight: 100
---

Connect Crossplane to AWS to create and manage cloud resources from Kubernetes with the [Upbound AWS Provider](https://marketplace.upbound.io/providers/upbound/provider-aws).

This guide is in three parts:
* Part 1 walks through installing Crossplane, configuring the provider to
authenticate to AWS and creating a _Managed Resource_ in AWS directly from your
Kubernetes cluster. This shows Crossplane can communicate with AWS.
* [Part 2]({{< ref "provider-aws-part-2" >}}) creates a 
_Composite Resource Definition_ (XRD), _Composite Resource_ (XR) and a _Claim_
(XC) to show how to create and use custom APIs.
* [Part 3]({{< ref "provider-aws-part-3" >}}) demonstrates how to patch
_Compositions_ with values used in a _Claim_ and how to build a Crossplane
_Package_ to make a Crossplane platform portable and reusable.

## Prerequisites
This quickstart requires:
* a Kubernetes cluster with at least 6 GB of RAM
* permissions to create pods and secrets in the Kubernetes cluster
* [Helm](https://helm.sh/) version `v3.2.0` or later
* an AWS account with permissions to create an S3 storage bucket
* AWS [access keys](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html#cli-configure-quickstart-creds)

## Install Crossplane

Crossplane installs into an existing Kubernetes cluster. 

{{< hint type="tip" >}}
If you don't have a Kubernetes cluster create one locally with [Kind](https://kind.sigs.k8s.io/).
{{< /hint >}}


### Install the Crossplane Helm chart

Helm enables Crossplane to install all its Kubernetes components through a _Helm Chart_.

Enable the Crossplane Helm Chart repository:

```shell
helm repo add \
crossplane-stable https://charts.crossplane.io/stable
helm repo update
```

Run the Helm dry-run to see all the Crossplane components Helm installs.

```shell
helm install crossplane \
crossplane-stable/crossplane \
--dry-run --debug \
--namespace crossplane-system \
--create-namespace
```
{{<expand "View the Helm dry-run" >}}
```shell
helm install crossplane \
crossplane-stable/crossplane \
--dry-run --debug \
--namespace crossplane-system \
--create-namespace
install.go:193: [debug] Original chart version: ""
install.go:210: [debug] CHART PATH: /home/vagrant/.cache/helm/repository/crossplane-1.10.1.tgz

NAME: crossplane
LAST DEPLOYED: Thu Jan 19 15:52:08 2023
NAMESPACE: crossplane-system
STATUS: pending-install
REVISION: 1
TEST SUITE: None
USER-SUPPLIED VALUES:
{}

COMPUTED VALUES:
affinity: {}
args: {}
configuration:
  packages: []
customAnnotations: {}
customLabels: {}
deploymentStrategy: RollingUpdate
extraEnvVarsCrossplane: {}
extraEnvVarsRBACManager: {}
image:
  pullPolicy: IfNotPresent
  repository: crossplane/crossplane
  tag: v1.10.1
imagePullSecrets: {}
leaderElection: true
metrics:
  enabled: false
nodeSelector: {}
packageCache:
  medium: ""
  pvc: ""
  sizeLimit: 5Mi
podSecurityContextCrossplane: {}
podSecurityContextRBACManager: {}
priorityClassName: ""
provider:
  packages: []
rbacManager:
  affinity: {}
  args: {}
  deploy: true
  leaderElection: true
  managementPolicy: All
  nodeSelector: {}
  replicas: 1
  skipAggregatedClusterRoles: false
  tolerations: {}
registryCaBundleConfig: {}
replicas: 1
resourcesCrossplane:
  limits:
    cpu: 100m
    memory: 512Mi
  requests:
    cpu: 100m
    memory: 256Mi
resourcesRBACManager:
  limits:
    cpu: 100m
    memory: 512Mi
  requests:
    cpu: 100m
    memory: 256Mi
securityContextCrossplane:
  allowPrivilegeEscalation: false
  readOnlyRootFilesystem: true
  runAsGroup: 65532
  runAsUser: 65532
securityContextRBACManager:
  allowPrivilegeEscalation: false
  readOnlyRootFilesystem: true
  runAsGroup: 65532
  runAsUser: 65532
serviceAccount:
  customAnnotations: {}
tolerations: {}
webhooks:
  enabled: false

HOOKS:
MANIFEST:
---
# Source: crossplane/templates/rbac-manager-serviceaccount.yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: rbac-manager
  labels:
    app: crossplane
    helm.sh/chart: crossplane-1.10.1
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/component: cloud-infrastructure-controller
    app.kubernetes.io/part-of: crossplane
    app.kubernetes.io/name: crossplane
    app.kubernetes.io/instance: crossplane
    app.kubernetes.io/version: "1.10.1"
---
# Source: crossplane/templates/serviceaccount.yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: crossplane
  labels:
    app: crossplane
    helm.sh/chart: crossplane-1.10.1
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/component: cloud-infrastructure-controller
    app.kubernetes.io/part-of: crossplane
    app.kubernetes.io/name: crossplane
    app.kubernetes.io/instance: crossplane
    app.kubernetes.io/version: "1.10.1"
---
# Source: crossplane/templates/clusterrole.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: crossplane
  labels:
    app: crossplane
    helm.sh/chart: crossplane-1.10.1
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/component: cloud-infrastructure-controller
    app.kubernetes.io/part-of: crossplane
    app.kubernetes.io/name: crossplane
    app.kubernetes.io/instance: crossplane
    app.kubernetes.io/version: "1.10.1"
aggregationRule:
  clusterRoleSelectors:
  - matchLabels:
      rbac.crossplane.io/aggregate-to-crossplane: "true"
---
# Source: crossplane/templates/clusterrole.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: crossplane:system:aggregate-to-crossplane
  labels:
    app: crossplane
    helm.sh/chart: crossplane-1.10.1
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/component: cloud-infrastructure-controller
    app.kubernetes.io/part-of: crossplane
    app.kubernetes.io/name: crossplane
    app.kubernetes.io/instance: crossplane
    app.kubernetes.io/version: "1.10.1"
    crossplane.io/scope: "system"
    rbac.crossplane.io/aggregate-to-crossplane: "true"
rules:
- apiGroups:
  - ""
  resources:
  - events
  verbs:
  - create
  - update
  - patch
  - delete
- apiGroups:
  - apiextensions.k8s.io
  resources:
  - customresourcedefinitions
  verbs:
  - "*"
- apiGroups:
  - ""
  resources:
  - secrets
  verbs:
  - get
  - list
  - watch
  - create
  - update
  - patch
  - delete
- apiGroups:
  - ""
  resources:
  - serviceaccounts
  - services
  verbs:
  - "*"
- apiGroups:
  - apiextensions.crossplane.io
  - pkg.crossplane.io
  - secrets.crossplane.io
  resources:
  - "*"
  verbs:
  - "*"
- apiGroups:
  - extensions
  - apps
  resources:
  - deployments
  verbs:
  - get
  - list
  - create
  - update
  - patch
  - delete
  - watch
- apiGroups:
  - ""
  - coordination.k8s.io
  resources:
  - configmaps
  - leases
  verbs:
  - get
  - list
  - create
  - update
  - patch
  - watch
  - delete
- apiGroups:
  - admissionregistration.k8s.io
  resources:
  - validatingwebhookconfigurations
  - mutatingwebhookconfigurations
  verbs:
  - get
  - list
  - create
  - update
  - patch
  - watch
  - delete
---
# Source: crossplane/templates/rbac-manager-allowed-provider-permissions.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: crossplane:allowed-provider-permissions
  labels:
    app: crossplane
    helm.sh/chart: crossplane-1.10.1
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/component: cloud-infrastructure-controller
    app.kubernetes.io/part-of: crossplane
    app.kubernetes.io/name: crossplane
    app.kubernetes.io/instance: crossplane
    app.kubernetes.io/version: "1.10.1"
aggregationRule:
  clusterRoleSelectors:
  - matchLabels:
      rbac.crossplane.io/aggregate-to-allowed-provider-permissions: "true"
---
# Source: crossplane/templates/rbac-manager-clusterrole.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: crossplane-rbac-manager
  labels:
    app: crossplane
    helm.sh/chart: crossplane-1.10.1
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/component: cloud-infrastructure-controller
    app.kubernetes.io/part-of: crossplane
    app.kubernetes.io/name: crossplane
    app.kubernetes.io/instance: crossplane
    app.kubernetes.io/version: "1.10.1"
rules:
- apiGroups:
  - ""
  resources:
  - events
  verbs:
  - create
  - update
  - patch
  - delete
- apiGroups:
  - ""
  resources:
  - namespaces
  - serviceaccounts
  verbs:
  - get
  - list
  - watch
- apiGroups:
  - apiextensions.crossplane.io
  resources:
  - compositeresourcedefinitions
  verbs:
  - get
  - list
  - watch
- apiGroups:
  - pkg.crossplane.io
  resources:
  - providerrevisions
  verbs:
  - get
  - list
  - watch
- apiGroups:
  - apiextensions.k8s.io
  resources:
  - customresourcedefinitions
  verbs:
  - get
  - list
  - watch
- apiGroups:
  - rbac.authorization.k8s.io
  resources:
  - clusterroles
  - roles
  verbs:
  - get
  - list
  - watch
  - create
  - update
  - patch
  # The RBAC manager may grant access it does not have.
  - escalate
- apiGroups:
  - rbac.authorization.k8s.io
  resources:
  - clusterroles
  verbs:
  - bind
- apiGroups:
  - rbac.authorization.k8s.io
  resources:
  - clusterrolebindings
  verbs:
  - "*"
- apiGroups:
  - ""
  - coordination.k8s.io
  resources:
  - configmaps
  - leases
  verbs:
  - get
  - list
  - create
  - update
  - patch
  - watch
  - delete
---
# Source: crossplane/templates/rbac-manager-managed-clusterroles.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: crossplane-admin
  labels:
    app: crossplane
    helm.sh/chart: crossplane-1.10.1
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/component: cloud-infrastructure-controller
    app.kubernetes.io/part-of: crossplane
    app.kubernetes.io/name: crossplane
    app.kubernetes.io/instance: crossplane
    app.kubernetes.io/version: "1.10.1"
aggregationRule:
  clusterRoleSelectors:
  - matchLabels:
      rbac.crossplane.io/aggregate-to-admin: "true"
---
# Source: crossplane/templates/rbac-manager-managed-clusterroles.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: crossplane-edit
  labels:
    app: crossplane
    helm.sh/chart: crossplane-1.10.1
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/component: cloud-infrastructure-controller
    app.kubernetes.io/part-of: crossplane
    app.kubernetes.io/name: crossplane
    app.kubernetes.io/instance: crossplane
    app.kubernetes.io/version: "1.10.1"
aggregationRule:
  clusterRoleSelectors:
  - matchLabels:
      rbac.crossplane.io/aggregate-to-edit: "true"
---
# Source: crossplane/templates/rbac-manager-managed-clusterroles.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: crossplane-view
  labels:
    app: crossplane
    helm.sh/chart: crossplane-1.10.1
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/component: cloud-infrastructure-controller
    app.kubernetes.io/part-of: crossplane
    app.kubernetes.io/name: crossplane
    app.kubernetes.io/instance: crossplane
    app.kubernetes.io/version: "1.10.1"
aggregationRule:
  clusterRoleSelectors:
  - matchLabels:
      rbac.crossplane.io/aggregate-to-view: "true"
---
# Source: crossplane/templates/rbac-manager-managed-clusterroles.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: crossplane-browse
  labels:
    app: crossplane
    helm.sh/chart: crossplane-1.10.1
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/component: cloud-infrastructure-controller
    app.kubernetes.io/part-of: crossplane
    app.kubernetes.io/name: crossplane
    app.kubernetes.io/instance: crossplane
    app.kubernetes.io/version: "1.10.1"
aggregationRule:
  clusterRoleSelectors:
  - matchLabels:
      rbac.crossplane.io/aggregate-to-browse: "true"
---
# Source: crossplane/templates/rbac-manager-managed-clusterroles.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: crossplane:aggregate-to-admin
  labels:
    rbac.crossplane.io/aggregate-to-admin: "true"
    app: crossplane
    helm.sh/chart: crossplane-1.10.1
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/component: cloud-infrastructure-controller
    app.kubernetes.io/part-of: crossplane
    app.kubernetes.io/name: crossplane
    app.kubernetes.io/instance: crossplane
    app.kubernetes.io/version: "1.10.1"
rules:
# Crossplane administrators have access to view events.
- apiGroups: [""]
  resources: [events]
  verbs: [get, list, watch]
# Crossplane administrators must create provider credential secrets, and may
# need to read or otherwise interact with connection secrets. They may also need
# to create or annotate namespaces.
- apiGroups: [""]
  resources: [secrets, namespaces]
  verbs: ["*"]
# Crossplane administrators have access to view the roles that they may be able
# to grant to other subjects.
- apiGroups: [rbac.authorization.k8s.io]
  resources: [clusterroles, roles]
  verbs: [get, list, watch]
# Crossplane administrators have access to grant the access they have to other
# subjects.
- apiGroups: [rbac.authorization.k8s.io]
  resources: [clusterrolebindings, rolebindings]
  verbs: ["*"]
# Crossplane administrators have full access to built in Crossplane types.
- apiGroups:
  - apiextensions.crossplane.io
  resources: ["*"]
  verbs: ["*"]
- apiGroups:
  - pkg.crossplane.io
  resources: [providers, configurations, providerrevisions, configurationrevisions]
  verbs: ["*"]
# Crossplane administrators have access to view CRDs in order to debug XRDs.
- apiGroups: [apiextensions.k8s.io]
  resources: [customresourcedefinitions]
  verbs: [get, list, watch]
---
# Source: crossplane/templates/rbac-manager-managed-clusterroles.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: crossplane:aggregate-to-edit
  labels:
    rbac.crossplane.io/aggregate-to-edit: "true"
    app: crossplane
    helm.sh/chart: crossplane-1.10.1
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/component: cloud-infrastructure-controller
    app.kubernetes.io/part-of: crossplane
    app.kubernetes.io/name: crossplane
    app.kubernetes.io/instance: crossplane
    app.kubernetes.io/version: "1.10.1"
rules:
# Crossplane editors have access to view events.
- apiGroups: [""]
  resources: [events]
  verbs: [get, list, watch]
# Crossplane editors must create provider credential secrets, and may need to
# read or otherwise interact with connection secrets.
- apiGroups: [""]
  resources: [secrets]
  verbs: ["*"]
# Crossplane editors may see which namespaces exist, but not edit them.
- apiGroups: [""]
  resources: [namespaces]
  verbs: [get, list, watch]
# Crossplane editors have full access to built in Crossplane types.
- apiGroups:
  - apiextensions.crossplane.io
  resources: ["*"]
  verbs: ["*"]
- apiGroups:
  - pkg.crossplane.io
  resources: [providers, configurations, providerrevisions, configurationrevisions]
  verbs: ["*"]
---
# Source: crossplane/templates/rbac-manager-managed-clusterroles.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: crossplane:aggregate-to-view
  labels:
    rbac.crossplane.io/aggregate-to-view: "true"
    app: crossplane
    helm.sh/chart: crossplane-1.10.1
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/component: cloud-infrastructure-controller
    app.kubernetes.io/part-of: crossplane
    app.kubernetes.io/name: crossplane
    app.kubernetes.io/instance: crossplane
    app.kubernetes.io/version: "1.10.1"
rules:
# Crossplane viewers have access to view events.
- apiGroups: [""]
  resources: [events]
  verbs: [get, list, watch]
# Crossplane viewers may see which namespaces exist.
- apiGroups: [""]
  resources: [namespaces]
  verbs: [get, list, watch]
# Crossplane viewers have read-only access to built in Crossplane types.
- apiGroups:
  - apiextensions.crossplane.io
  resources: ["*"]
  verbs: [get, list, watch]
- apiGroups:
  - pkg.crossplane.io
  resources: [providers, configurations, providerrevisions, configurationrevisions]
  verbs: [get, list, watch]
---
# Source: crossplane/templates/rbac-manager-managed-clusterroles.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: crossplane:aggregate-to-browse
  labels:
    rbac.crossplane.io/aggregate-to-browse: "true"
    app: crossplane
    helm.sh/chart: crossplane-1.10.1
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/component: cloud-infrastructure-controller
    app.kubernetes.io/part-of: crossplane
    app.kubernetes.io/name: crossplane
    app.kubernetes.io/instance: crossplane
    app.kubernetes.io/version: "1.10.1"
rules:
# Crossplane browsers have access to view events.
- apiGroups: [""]
  resources: [events]
  verbs: [get, list, watch]
# Crossplane browsers have read-only access to compositions and XRDs. This
# allows them to discover and select an appropriate composition when creating a
# resource claim.
- apiGroups:
  - apiextensions.crossplane.io
  resources: ["*"]
  verbs: [get, list, watch]
---
# Source: crossplane/templates/rbac-manager-managed-clusterroles.yaml
# The below ClusterRoles are aggregated to the namespaced RBAC roles created by
# the Crossplane RBAC manager when it is running in --manage=All mode.
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: crossplane:aggregate-to-ns-admin
  labels:
    rbac.crossplane.io/aggregate-to-ns-admin: "true"
    rbac.crossplane.io/base-of-ns-admin: "true"
    app: crossplane
    helm.sh/chart: crossplane-1.10.1
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/component: cloud-infrastructure-controller
    app.kubernetes.io/part-of: crossplane
    app.kubernetes.io/name: crossplane
    app.kubernetes.io/instance: crossplane
    app.kubernetes.io/version: "1.10.1"
rules:
# Crossplane namespace admins have access to view events.
- apiGroups: [""]
  resources: [events]
  verbs: [get, list, watch]
# Crossplane namespace admins may need to read or otherwise interact with
# resource claim connection secrets.
- apiGroups: [""]
  resources: [secrets]
  verbs: ["*"]
# Crossplane namespace admins have access to view the roles that they may be
# able to grant to other subjects.
- apiGroups: [rbac.authorization.k8s.io]
  resources: [roles]
  verbs: [get, list, watch]
# Crossplane namespace admins have access to grant the access they have to other
# subjects.
- apiGroups: [rbac.authorization.k8s.io]
  resources: [rolebindings]
  verbs: ["*"]
---
# Source: crossplane/templates/rbac-manager-managed-clusterroles.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: crossplane:aggregate-to-ns-edit
  labels:
    rbac.crossplane.io/aggregate-to-ns-edit: "true"
    rbac.crossplane.io/base-of-ns-edit: "true"
    app: crossplane
    helm.sh/chart: crossplane-1.10.1
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/component: cloud-infrastructure-controller
    app.kubernetes.io/part-of: crossplane
    app.kubernetes.io/name: crossplane
    app.kubernetes.io/instance: crossplane
    app.kubernetes.io/version: "1.10.1"
rules:
# Crossplane namespace editors have access to view events.
- apiGroups: [""]
  resources: [events]
  verbs: [get, list, watch]
# Crossplane namespace editors may need to read or otherwise interact with
# resource claim connection secrets.
- apiGroups: [""]
  resources: [secrets]
  verbs: ["*"]
---
# Source: crossplane/templates/rbac-manager-managed-clusterroles.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: crossplane:aggregate-to-ns-view
  labels:
    rbac.crossplane.io/aggregate-to-ns-view: "true"
    rbac.crossplane.io/base-of-ns-view: "true"
    app: crossplane
    helm.sh/chart: crossplane-1.10.1
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/component: cloud-infrastructure-controller
    app.kubernetes.io/part-of: crossplane
    app.kubernetes.io/name: crossplane
    app.kubernetes.io/instance: crossplane
    app.kubernetes.io/version: "1.10.1"
rules:
# Crossplane namespace viewers have access to view events.
- apiGroups: [""]
  resources: [events]
  verbs: [get, list, watch]
---
# Source: crossplane/templates/clusterrolebinding.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: crossplane
  labels:
    app: crossplane
    helm.sh/chart: crossplane-1.10.1
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/component: cloud-infrastructure-controller
    app.kubernetes.io/part-of: crossplane
    app.kubernetes.io/name: crossplane
    app.kubernetes.io/instance: crossplane
    app.kubernetes.io/version: "1.10.1"
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: crossplane
subjects:
- kind: ServiceAccount
  name: crossplane
  namespace: crossplane-system
---
# Source: crossplane/templates/rbac-manager-clusterrolebinding.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: crossplane-rbac-manager
  labels:
    app: crossplane
    helm.sh/chart: crossplane-1.10.1
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/component: cloud-infrastructure-controller
    app.kubernetes.io/part-of: crossplane
    app.kubernetes.io/name: crossplane
    app.kubernetes.io/instance: crossplane
    app.kubernetes.io/version: "1.10.1"
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: crossplane-rbac-manager
subjects:
- kind: ServiceAccount
  name: rbac-manager
  namespace: crossplane-system
---
# Source: crossplane/templates/rbac-manager-managed-clusterroles.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: crossplane-admin
  labels:
    app: crossplane
    helm.sh/chart: crossplane-1.10.1
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/component: cloud-infrastructure-controller
    app.kubernetes.io/part-of: crossplane
    app.kubernetes.io/name: crossplane
    app.kubernetes.io/instance: crossplane
    app.kubernetes.io/version: "1.10.1"
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: crossplane-admin
subjects:
- apiGroup: rbac.authorization.k8s.io
  kind: Group
  name: crossplane:masters
---
# Source: crossplane/templates/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: crossplane
  labels:
    app: crossplane
    release: crossplane
    helm.sh/chart: crossplane-1.10.1
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/component: cloud-infrastructure-controller
    app.kubernetes.io/part-of: crossplane
    app.kubernetes.io/name: crossplane
    app.kubernetes.io/instance: crossplane
    app.kubernetes.io/version: "1.10.1"
spec:
  replicas: 1
  selector:
    matchLabels:
      app: crossplane
      release: crossplane
  strategy:
    type: RollingUpdate
  template:
    metadata:
      labels:
        app: crossplane
        release: crossplane
        helm.sh/chart: crossplane-1.10.1
        app.kubernetes.io/managed-by: Helm
        app.kubernetes.io/component: cloud-infrastructure-controller
        app.kubernetes.io/part-of: crossplane
        app.kubernetes.io/name: crossplane
        app.kubernetes.io/instance: crossplane
        app.kubernetes.io/version: "1.10.1"
    spec:
      securityContext:
        {}
      serviceAccountName: crossplane
      initContainers:
        - image: crossplane/crossplane:v1.10.1
          args:
          - core
          - init
          imagePullPolicy: IfNotPresent
          name: crossplane-init
          resources:
            limits:
              cpu: 100m
              memory: 512Mi
            requests:
              cpu: 100m
              memory: 256Mi
          securityContext:
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
            runAsGroup: 65532
            runAsUser: 65532
          env:
          - name: POD_NAMESPACE
            valueFrom:
              fieldRef:
                fieldPath: metadata.namespace
          - name: POD_SERVICE_ACCOUNT
            valueFrom:
              fieldRef:
                fieldPath: spec.serviceAccountName
      containers:
      - image: crossplane/crossplane:v1.10.1
        args:
        - core
        - start
        imagePullPolicy: IfNotPresent
        name: crossplane
        resources:
            limits:
              cpu: 100m
              memory: 512Mi
            requests:
              cpu: 100m
              memory: 256Mi
        securityContext:
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
            runAsGroup: 65532
            runAsUser: 65532
        env:
          - name: POD_NAMESPACE
            valueFrom:
              fieldRef:
                fieldPath: metadata.namespace
          - name: LEADER_ELECTION
            value: "true"
        volumeMounts:
          - mountPath: /cache
            name: package-cache
      volumes:
      - name: package-cache
        emptyDir:
          medium:
          sizeLimit: 5Mi
---
# Source: crossplane/templates/rbac-manager-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: crossplane-rbac-manager
  labels:
    app: crossplane-rbac-manager
    release: crossplane
    helm.sh/chart: crossplane-1.10.1
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/component: cloud-infrastructure-controller
    app.kubernetes.io/part-of: crossplane
    app.kubernetes.io/name: crossplane
    app.kubernetes.io/instance: crossplane
    app.kubernetes.io/version: "1.10.1"
spec:
  replicas: 1
  selector:
    matchLabels:
      app: crossplane-rbac-manager
      release: crossplane
  strategy:
    type: RollingUpdate
  template:
    metadata:
      labels:
        app: crossplane-rbac-manager
        release: crossplane
        helm.sh/chart: crossplane-1.10.1
        app.kubernetes.io/managed-by: Helm
        app.kubernetes.io/component: cloud-infrastructure-controller
        app.kubernetes.io/part-of: crossplane
        app.kubernetes.io/name: crossplane
        app.kubernetes.io/instance: crossplane
        app.kubernetes.io/version: "1.10.1"
    spec:
      securityContext:
        {}
      serviceAccountName: rbac-manager
      initContainers:
      - image: crossplane/crossplane:v1.10.1
        args:
        - rbac
        - init
        imagePullPolicy: IfNotPresent
        name: crossplane-init
        resources:
            limits:
              cpu: 100m
              memory: 512Mi
            requests:
              cpu: 100m
              memory: 256Mi
        securityContext:
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
            runAsGroup: 65532
            runAsUser: 65532
      containers:
      - image: crossplane/crossplane:v1.10.1
        args:
        - rbac
        - start
        - --manage=All
        - --provider-clusterrole=crossplane:allowed-provider-permissions
        imagePullPolicy: IfNotPresent
        name: crossplane
        resources:
            limits:
              cpu: 100m
              memory: 512Mi
            requests:
              cpu: 100m
              memory: 256Mi
        securityContext:
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
            runAsGroup: 65532
            runAsUser: 65532
        env:
          - name: LEADER_ELECTION
            value: "true"

NOTES:
Release: crossplane

Chart Name: crossplane
Chart Description: Crossplane is an open source Kubernetes add-on that enables platform teams to assemble infrastructure from multiple vendors, and expose higher level self-service APIs for application teams to consume.
Chart Version: 1.10.1
Chart Application Version: 1.10.1

Kube Version: v1.24.9
```
{{< /expand >}}

Install the Crossplane components using `helm install`.

```shell
helm install crossplane \
crossplane-stable/crossplane \
--namespace crossplane-system \
--create-namespace
```

Verify Crossplane installed with `kubectl get pods`.

```shell {copy-lines="1"}
kubectl get pods -n crossplane-system
NAME                                      READY   STATUS    RESTARTS   AGE
crossplane-d4cd8d784-ldcgb                1/1     Running   0          54s
crossplane-rbac-manager-84769b574-6mw6f   1/1     Running   0          54s
```

Installing Crossplane creates new Kubernetes API end-points. Look at the new API end-points with `kubectl api-resources  | grep crossplane`.

```shell  {label="grep",copy-lines="1"}
kubectl api-resources  | grep crossplane
compositeresourcedefinitions      xrd,xrds     apiextensions.crossplane.io/v1         false        CompositeResourceDefinition
compositionrevisions                           apiextensions.crossplane.io/v1alpha1   false        CompositionRevision
compositions                                   apiextensions.crossplane.io/v1         false        Composition
configurationrevisions                         pkg.crossplane.io/v1                   false        ConfigurationRevision
configurations                                 pkg.crossplane.io/v1                   false        Configuration
controllerconfigs                              pkg.crossplane.io/v1alpha1             false        ControllerConfig
locks                                          pkg.crossplane.io/v1beta1              false        Lock
providerrevisions                              pkg.crossplane.io/v1                   false        ProviderRevision
providers                                      pkg.crossplane.io/v1                   false        Provider
storeconfigs                                   secrets.crossplane.io/v1alpha1         false        StoreConfig
```

## Install the AWS provider

Install the provider into the Kubernetes cluster with a Kubernetes configuration file. 

```yaml {label="provider",copy-lines="all"}
cat <<EOF | kubectl apply -f -
apiVersion: pkg.crossplane.io/v1
kind: Provider
metadata:
  name: upbound-provider-aws
spec:
  package: xpkg.upbound.io/crossplane-contrib/provider-aws:v0.41.1
EOF
```

The Crossplane {{< hover label="provider" line="3" >}}Provider{{</hover>}} Custom Resource Definition tells Kubernetes how to
connect to the provider.

Verify the provider installed with `kubectl get providers`. 

{{< hint type="note" >}}
It may take up to five minutes for the provider to list `HEALTHY` as `True`. 
{{< /hint >}}

```shell {copy-lines="1"}
kubectl get providers
NAME                   INSTALLED   HEALTHY   PACKAGE                                        AGE
upbound-provider-aws   True        True      xpkg.upbound.io/crossplane-contrib/provider-aws:v0.41.1   12m
```

A provider installs their own Kubernetes _Custom Resource Definitions_ (CRDs). These CRDs allow you to create AWS resources directly inside Kubernetes.

You can view the new CRDs with `kubectl get crds`. Every CRD maps to a unique AWS service Crossplane can provision and manage.


{{< hint type="tip" >}}
See details about all the supported CRDs in the [Upbound Marketplace](https://marketplace.upbound.io/providers/upbound/provider-family-aws/).
{{< /hint >}}

## Create a Kubernetes secret for AWS
The provider requires credentials to create and manage AWS resources. Providers use a Kubernetes _Secret_ to connect the credentials to the provider.

First generate a Kubernetes _Secret_ from your AWS key-pair and then configure the Provider to use it.

{{< hint type="note" >}}
Other authentication methods exist and are beyond the scope of this guide. The [Provider documentation](https://marketplace.upbound.io/providers/upbound/provider-aws/latest/docs/configuration) contains information on alternative authentication methods. 
{{< /hint >}}

### Generate an AWS key-pair file
For basic user authentication, use an AWS Access keys key-pair file. 

{{< hint type="tip" >}}
The [AWS documentation](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html#cli-configure-quickstart-creds) provides information on how to generate AWS Access keys.
{{< /hint >}}

Create a text file containing the AWS account `aws_access_key_id` and `aws_secret_access_key`.  

```ini {copy-lines="all"}
[default]
aws_access_key_id = <aws_access_key>
aws_secret_access_key = <aws_secret_key>
```

Save this text file as `aws-credentials.txt`.

{{< hint type="note" >}}
The [Configuration](https://marketplace.upbound.io/providers/upbound/provider-aws/latest/docs/configuration) section of the Provider documentation describes other authentication methods.
{{< /hint >}}

### Create a Kubernetes secret with the AWS credentials
A Kubernetes generic secret has a name and contents. Use {{< hover label="kube-create-secret" line="1">}}kubectl create secret{{< /hover >}} to generate the secret object named {{< hover label="kube-create-secret" line="2">}}aws-secret{{< /hover >}} in the {{< hover label="kube-create-secret" line="3">}}crossplane-system{{</ hover >}} namespace.  
Use the {{< hover label="kube-create-secret" line="4">}}--from-file={{</hover>}} argument to set the value to the contents of the  {{< hover label="kube-create-secret" line="4">}}aws-credentials.txt{{< /hover >}} file.

```shell {label="kube-create-secret",copy-lines="all"}
kubectl create secret \
generic aws-secret \
-n crossplane-system \
--from-file=creds=./aws-credentials.txt
```

View the secret with `kubectl describe secret`

{{< hint type="note" >}}
The size may be larger if there are extra blank spaces in your text file.
{{< /hint >}}

```shell {copy-lines="1"}
kubectl describe secret aws-secret -n crossplane-system
Name:         aws-secret
Namespace:    crossplane-system
Labels:       <none>
Annotations:  <none>

Type:  Opaque

Data
====
creds:  114 bytes
```

## Create a ProviderConfig
A `ProviderConfig` customizes the settings of the AWS Provider.  

Apply the {{< hover label="providerconfig" line="2">}}ProviderConfig{{</ hover >}} with the command:
```yaml {label="providerconfig",copy-lines="all"}
cat <<EOF | kubectl apply -f -
apiVersion: pkg.crossplane.io/v1
kind: ProviderConfig
metadata:
  name: default
spec:
  credentials:
    source: Secret
    secretRef:
      namespace: crossplane-system
      name: aws-secret
      key: creds
EOF
```

This attaches the AWS credentials, saved as a Kubernetes secret, as a {{< hover label="providerconfig" line="9">}}secretRef{{</ hover>}}.

The {{< hover label="providerconfig" line="11">}}spec.credentials.secretRef.name{{< /hover >}} value is the name of the Kubernetes secret containing the AWS credentials in the {{< hover label="providerconfig" line="10">}}spec.credentials.secretRef.namespace{{< /hover >}}.


## Create a managed resource
A _managed resource_ is anything Crossplane creates and manages outside of the Kubernetes cluster. This creates an AWS S3 bucket with Crossplane. The S3 bucket is a _managed resource_.

{{< hint type="note" >}}
AWS S3 bucket names must be globally unique. To generate a unique name the example uses a random hash. 
Any unique name is acceptable.
{{< /hint >}}

```yaml {label="xr"}
bucket=$(echo "crossplane-bucket-"$(head -n 4096 /dev/urandom | openssl sha1 | tail -c 10))
cat <<EOF | kubectl apply -f -
apiVersion: s3.aws.crossplane.io/v1beta1
kind: Bucket
metadata:
  name: $bucket
spec:
  forProvider:
    region: us-east-2
  providerConfigRef:
    name: default
EOF
```

The {{< hover label="xr" line="3">}}apiVersion{{< /hover >}} and {{< hover label="xr" line="4">}}kind{{</hover >}} are from the provider's CRDs.


The {{< hover label="xr" line="6">}}metadata.name{{< /hover >}} value is the name of the created S3 bucket in AWS.  
This example uses the generated name `crossplane-bucket-<hash>` in the {{< hover label="xr" line="6">}}`$bucket`{{</hover >}} variable.

The {{< hover label="xr" line="9">}}spec.forProvider.region{{< /hover >}} tells AWS which AWS region to use when deploying resources. The region can be any [AWS Regional endpoint](https://docs.aws.amazon.com/general/latest/gr/rande.html#regional-endpoints) code.

Use `kubectl get buckets` to verify Crossplane created the bucket.

{{< hint type="tip" >}}
Crossplane created the bucket when the values `READY` and `SYNCED` are `True`.  
This may take up to 5 minutes.  
{{< /hint >}}

```shell {copy-lines="1"}
kubectl get buckets
NAME                          READY   SYNCED   EXTERNAL-NAME                 AGE
crossplane-bucket-45eed4ae0   True    True     crossplane-bucket-45eed4ae0   61s
```

## Delete the managed resource
Before shutting down your Kubernetes cluster, delete the S3 bucket just created.

Use `kubectl delete bucket <bucketname>` to remove the bucket.

```shell {copy-lines="1"}
kubectl delete bucket $bucket
bucket.s3.aws.crossplane.io "crossplane-bucket-45eed4ae0" deleted
```

## Next steps
* **[Continue to part 2]({{< ref "provider-aws-part-2">}})** to create a Crossplane _Composite Resource_ and _Claim_.
* Explore AWS resources that Crossplane can configure in the [Provider CRD reference](https://marketplace.upbound.io/providers/upbound/provider-family-aws/).
* Join the [Crossplane Slack](https://slack.crossplane.io/) and connect with Crossplane users and contributors.