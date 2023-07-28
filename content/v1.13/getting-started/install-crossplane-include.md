---
tocHidden: true
---

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
install.go:200: [debug] Original chart version: ""
install.go:217: [debug] CHART PATH: /home/vagrant/.cache/helm/repository/crossplane-1.13.0.tgz

NAME: crossplane
LAST DEPLOYED: Fri Jul 28 13:57:41 2023
NAMESPACE: crossplane-system
STATUS: pending-install
REVISION: 1
TEST SUITE: None
USER-SUPPLIED VALUES:
{}

COMPUTED VALUES:
affinity: {}
args: []
configuration:
  packages: []
customAnnotations: {}
customLabels: {}
deploymentStrategy: RollingUpdate
extraEnvVarsCrossplane: {}
extraEnvVarsRBACManager: {}
extraVolumeMountsCrossplane: {}
extraVolumesCrossplane: {}
hostNetwork: false
image:
  pullPolicy: IfNotPresent
  repository: crossplane/crossplane
  tag: ""
imagePullSecrets: {}
leaderElection: true
metrics:
  enabled: false
nodeSelector: {}
packageCache:
  configMap: ""
  medium: ""
  pvc: ""
  sizeLimit: 20Mi
podSecurityContextCrossplane: {}
podSecurityContextRBACManager: {}
priorityClassName: ""
provider:
  packages: []
rbacManager:
  affinity: {}
  args: []
  deploy: true
  leaderElection: true
  managementPolicy: Basic
  nodeSelector: {}
  replicas: 1
  skipAggregatedClusterRoles: false
  tolerations: []
registryCaBundleConfig:
  key: ""
  name: ""
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
tolerations: []
webhooks:
  enabled: true
xfn:
  args: []
  cache:
    configMap: ""
    medium: ""
    pvc: ""
    sizeLimit: 1Gi
  enabled: false
  extraEnvVars: {}
  image:
    pullPolicy: IfNotPresent
    repository: crossplane/xfn
    tag: ""
  resources:
    limits:
      cpu: 2000m
      memory: 2Gi
    requests:
      cpu: 1000m
      memory: 1Gi
  securityContext:
    allowPrivilegeEscalation: false
    capabilities:
      add:
      - SETUID
      - SETGID
    readOnlyRootFilesystem: true
    runAsGroup: 65532
    runAsUser: 65532
    seccompProfile:
      type: Unconfined

HOOKS:
MANIFEST:
---
# Source: crossplane/templates/rbac-manager-serviceaccount.yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: rbac-manager
  namespace: crossplane-system
  labels:
    app: crossplane
    helm.sh/chart: crossplane-1.13.0
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/component: cloud-infrastructure-controller
    app.kubernetes.io/part-of: crossplane
    app.kubernetes.io/name: crossplane
    app.kubernetes.io/instance: crossplane
    app.kubernetes.io/version: "1.13.0"
---
# Source: crossplane/templates/serviceaccount.yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: crossplane
  namespace: crossplane-system
  labels:
    app: crossplane
    helm.sh/chart: crossplane-1.13.0
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/component: cloud-infrastructure-controller
    app.kubernetes.io/part-of: crossplane
    app.kubernetes.io/name: crossplane
    app.kubernetes.io/instance: crossplane
    app.kubernetes.io/version: "1.13.0"
---
# Source: crossplane/templates/secret.yaml
# The reason this is created empty and filled by the init container is that it's
# mounted by the actual container, so if it wasn't created by Helm, then the
# deployment wouldn't be deployed at all with secret to mount not found error.
# In addition, Helm would delete this secret after uninstallation so the new
# installation of Crossplane would use its own certificate.
apiVersion: v1
kind: Secret
metadata:
  name: webhook-tls-secret
  namespace: crossplane-system
type: Opaque
---
# Source: crossplane/templates/clusterrole.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: crossplane
  labels:
    app: crossplane
    helm.sh/chart: crossplane-1.13.0
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/component: cloud-infrastructure-controller
    app.kubernetes.io/part-of: crossplane
    app.kubernetes.io/name: crossplane
    app.kubernetes.io/instance: crossplane
    app.kubernetes.io/version: "1.13.0"
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
    helm.sh/chart: crossplane-1.13.0
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/component: cloud-infrastructure-controller
    app.kubernetes.io/part-of: crossplane
    app.kubernetes.io/name: crossplane
    app.kubernetes.io/instance: crossplane
    app.kubernetes.io/version: "1.13.0"
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
    helm.sh/chart: crossplane-1.13.0
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/component: cloud-infrastructure-controller
    app.kubernetes.io/part-of: crossplane
    app.kubernetes.io/name: crossplane
    app.kubernetes.io/instance: crossplane
    app.kubernetes.io/version: "1.13.0"
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
    helm.sh/chart: crossplane-1.13.0
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/component: cloud-infrastructure-controller
    app.kubernetes.io/part-of: crossplane
    app.kubernetes.io/name: crossplane
    app.kubernetes.io/instance: crossplane
    app.kubernetes.io/version: "1.13.0"
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
# The RBAC manager creates a series of RBAC roles for each namespace it sees.
# These RBAC roles are controlled (in the owner reference sense) by the namespace.
# The RBAC manager needs permission to set finalizers on Namespaces in order to
# create resources that block their deletion when the
# OwnerReferencesPermissionEnforcement admission controller is enabled.
# See https://kubernetes.io/docs/reference/access-authn-authz/admission-controllers/#ownerreferencespermissionenforcement
- apiGroups:
  - ""
  resources:
  - namespaces/finalizers
  verbs:
  - update
- apiGroups:
  - apiextensions.crossplane.io
  resources:
  - compositeresourcedefinitions
  verbs:
  - get
  - list
  - watch
# The RBAC manager creates a series of RBAC cluster roles for each XRD it sees.
# These cluster roles are controlled (in the owner reference sense) by the XRD.
# The RBAC manager needs permission to set finalizers on XRDs in order to
# create resources that block their deletion when the
# OwnerReferencesPermissionEnforcement admission controller is enabled.
# See https://kubernetes.io/docs/reference/access-authn-authz/admission-controllers/#ownerreferencespermissionenforcement
- apiGroups:
  - apiextensions.crossplane.io
  resources:
  - compositeresourcedefinitions/finalizers
  verbs:
  - update
- apiGroups:
  - pkg.crossplane.io
  resources:
  - providerrevisions
  verbs:
  - get
  - list
  - watch
# The RBAC manager creates a series of RBAC cluster roles for each ProviderRevision
# it sees. These cluster roles are controlled (in the owner reference sense) by the
# ProviderRevision. The RBAC manager needs permission to set finalizers on
# ProviderRevisions in order to create resources that block their deletion when the
# OwnerReferencesPermissionEnforcement admission controller is enabled.
# See https://kubernetes.io/docs/reference/access-authn-authz/admission-controllers/#ownerreferencespermissionenforcement
- apiGroups:
  - pkg.crossplane.io
  resources:
  - providerrevisions/finalizers
  verbs:
  - update
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
    helm.sh/chart: crossplane-1.13.0
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/component: cloud-infrastructure-controller
    app.kubernetes.io/part-of: crossplane
    app.kubernetes.io/name: crossplane
    app.kubernetes.io/instance: crossplane
    app.kubernetes.io/version: "1.13.0"
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
    helm.sh/chart: crossplane-1.13.0
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/component: cloud-infrastructure-controller
    app.kubernetes.io/part-of: crossplane
    app.kubernetes.io/name: crossplane
    app.kubernetes.io/instance: crossplane
    app.kubernetes.io/version: "1.13.0"
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
    helm.sh/chart: crossplane-1.13.0
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/component: cloud-infrastructure-controller
    app.kubernetes.io/part-of: crossplane
    app.kubernetes.io/name: crossplane
    app.kubernetes.io/instance: crossplane
    app.kubernetes.io/version: "1.13.0"
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
    helm.sh/chart: crossplane-1.13.0
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/component: cloud-infrastructure-controller
    app.kubernetes.io/part-of: crossplane
    app.kubernetes.io/name: crossplane
    app.kubernetes.io/instance: crossplane
    app.kubernetes.io/version: "1.13.0"
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
    helm.sh/chart: crossplane-1.13.0
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/component: cloud-infrastructure-controller
    app.kubernetes.io/part-of: crossplane
    app.kubernetes.io/name: crossplane
    app.kubernetes.io/instance: crossplane
    app.kubernetes.io/version: "1.13.0"
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
  resources: [locks, providers, configurations, providerrevisions, configurationrevisions]
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
    helm.sh/chart: crossplane-1.13.0
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/component: cloud-infrastructure-controller
    app.kubernetes.io/part-of: crossplane
    app.kubernetes.io/name: crossplane
    app.kubernetes.io/instance: crossplane
    app.kubernetes.io/version: "1.13.0"
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
  resources: [locks, providers, configurations, providerrevisions, configurationrevisions]
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
    helm.sh/chart: crossplane-1.13.0
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/component: cloud-infrastructure-controller
    app.kubernetes.io/part-of: crossplane
    app.kubernetes.io/name: crossplane
    app.kubernetes.io/instance: crossplane
    app.kubernetes.io/version: "1.13.0"
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
  resources: [locks, providers, configurations, providerrevisions, configurationrevisions]
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
    helm.sh/chart: crossplane-1.13.0
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/component: cloud-infrastructure-controller
    app.kubernetes.io/part-of: crossplane
    app.kubernetes.io/name: crossplane
    app.kubernetes.io/instance: crossplane
    app.kubernetes.io/version: "1.13.0"
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
    helm.sh/chart: crossplane-1.13.0
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/component: cloud-infrastructure-controller
    app.kubernetes.io/part-of: crossplane
    app.kubernetes.io/name: crossplane
    app.kubernetes.io/instance: crossplane
    app.kubernetes.io/version: "1.13.0"
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
    helm.sh/chart: crossplane-1.13.0
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/component: cloud-infrastructure-controller
    app.kubernetes.io/part-of: crossplane
    app.kubernetes.io/name: crossplane
    app.kubernetes.io/instance: crossplane
    app.kubernetes.io/version: "1.13.0"
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
    helm.sh/chart: crossplane-1.13.0
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/component: cloud-infrastructure-controller
    app.kubernetes.io/part-of: crossplane
    app.kubernetes.io/name: crossplane
    app.kubernetes.io/instance: crossplane
    app.kubernetes.io/version: "1.13.0"
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
    helm.sh/chart: crossplane-1.13.0
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/component: cloud-infrastructure-controller
    app.kubernetes.io/part-of: crossplane
    app.kubernetes.io/name: crossplane
    app.kubernetes.io/instance: crossplane
    app.kubernetes.io/version: "1.13.0"
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
    helm.sh/chart: crossplane-1.13.0
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/component: cloud-infrastructure-controller
    app.kubernetes.io/part-of: crossplane
    app.kubernetes.io/name: crossplane
    app.kubernetes.io/instance: crossplane
    app.kubernetes.io/version: "1.13.0"
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
    helm.sh/chart: crossplane-1.13.0
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/component: cloud-infrastructure-controller
    app.kubernetes.io/part-of: crossplane
    app.kubernetes.io/name: crossplane
    app.kubernetes.io/instance: crossplane
    app.kubernetes.io/version: "1.13.0"
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: crossplane-admin
subjects:
- apiGroup: rbac.authorization.k8s.io
  kind: Group
  name: crossplane:masters
---
# Source: crossplane/templates/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: crossplane-webhooks
  namespace: crossplane-system
  labels:
    app: crossplane
    release: crossplane
    helm.sh/chart: crossplane-1.13.0
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/component: cloud-infrastructure-controller
    app.kubernetes.io/part-of: crossplane
    app.kubernetes.io/name: crossplane
    app.kubernetes.io/instance: crossplane
    app.kubernetes.io/version: "1.13.0"
spec:
  selector:
    app: crossplane
    release: crossplane
  ports:
  - protocol: TCP
    port: 9443
    targetPort: 9443
---
# Source: crossplane/templates/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: crossplane
  namespace: crossplane-system
  labels:
    app: crossplane
    release: crossplane
    helm.sh/chart: crossplane-1.13.0
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/component: cloud-infrastructure-controller
    app.kubernetes.io/part-of: crossplane
    app.kubernetes.io/name: crossplane
    app.kubernetes.io/instance: crossplane
    app.kubernetes.io/version: "1.13.0"
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
        helm.sh/chart: crossplane-1.13.0
        app.kubernetes.io/managed-by: Helm
        app.kubernetes.io/component: cloud-infrastructure-controller
        app.kubernetes.io/part-of: crossplane
        app.kubernetes.io/name: crossplane
        app.kubernetes.io/instance: crossplane
        app.kubernetes.io/version: "1.13.0"
    spec:
      securityContext:
        {}
      serviceAccountName: crossplane
      hostNetwork: false
      initContainers:
        - image: "crossplane/crossplane:v1.13.0"
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
          - name: GOMAXPROCS
            valueFrom:
              resourceFieldRef:
                containerName: crossplane-init
                resource: limits.cpu
          - name: GOMEMLIMIT
            valueFrom:
              resourceFieldRef:
                containerName: crossplane-init
                resource: limits.memory
          - name: POD_NAMESPACE
            valueFrom:
              fieldRef:
                fieldPath: metadata.namespace
          - name: POD_SERVICE_ACCOUNT
            valueFrom:
              fieldRef:
                fieldPath: spec.serviceAccountName
          - name: "WEBHOOK_TLS_SECRET_NAME"
            value: webhook-tls-secret
          - name: "WEBHOOK_SERVICE_NAME"
            value: crossplane-webhooks
          - name: "WEBHOOK_SERVICE_NAMESPACE"
            valueFrom:
              fieldRef:
                fieldPath: metadata.namespace
          - name: "WEBHOOK_SERVICE_PORT"
            value: "9443"
      containers:
      - image: "crossplane/crossplane:v1.13.0"
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
        ports:
        - name: webhooks
          containerPort: 9443
        securityContext:
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
            runAsGroup: 65532
            runAsUser: 65532
        env:
          - name: GOMAXPROCS
            valueFrom:
              resourceFieldRef:
                containerName: crossplane
                resource: limits.cpu
          - name: GOMEMLIMIT
            valueFrom:
              resourceFieldRef:
                containerName: crossplane
                resource: limits.memory
          - name: POD_NAMESPACE
            valueFrom:
              fieldRef:
                fieldPath: metadata.namespace
          - name: POD_SERVICE_ACCOUNT
            valueFrom:
              fieldRef:
                fieldPath: spec.serviceAccountName
          - name: LEADER_ELECTION
            value: "true"
          - name: "WEBHOOK_TLS_SECRET_NAME"
            value: webhook-tls-secret
          - name: "WEBHOOK_TLS_CERT_DIR"
            value: /webhook/tls
        volumeMounts:
          - mountPath: /cache
            name: package-cache
          - mountPath: /webhook/tls
            name: webhook-tls-secret
      volumes:
      - name: package-cache
        emptyDir:
          medium:
          sizeLimit: 20Mi
      - name: webhook-tls-secret
        secret:
          # NOTE(muvaf): The tls.crt is used both by the server (requires it to
          # be a single cert) and the caBundle fields of webhook configs and CRDs
          # which can accept a whole bundle of certificates. In order to meet
          # the requirements of both, we require a single certificate instead of
          # a bundle.
          # It's assumed that initializer generates this anyway, so it should be
          # fine.
          secretName: webhook-tls-secret
---
# Source: crossplane/templates/rbac-manager-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: crossplane-rbac-manager
  namespace: crossplane-system
  labels:
    app: crossplane-rbac-manager
    release: crossplane
    helm.sh/chart: crossplane-1.13.0
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/component: cloud-infrastructure-controller
    app.kubernetes.io/part-of: crossplane
    app.kubernetes.io/name: crossplane
    app.kubernetes.io/instance: crossplane
    app.kubernetes.io/version: "1.13.0"
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
        helm.sh/chart: crossplane-1.13.0
        app.kubernetes.io/managed-by: Helm
        app.kubernetes.io/component: cloud-infrastructure-controller
        app.kubernetes.io/part-of: crossplane
        app.kubernetes.io/name: crossplane
        app.kubernetes.io/instance: crossplane
        app.kubernetes.io/version: "1.13.0"
    spec:
      securityContext:
        {}
      serviceAccountName: rbac-manager
      initContainers:
      - image: "crossplane/crossplane:v1.13.0"
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
        env:
          - name: GOMAXPROCS
            valueFrom:
              resourceFieldRef:
                containerName: crossplane-init
                resource: limits.cpu
          - name: GOMEMLIMIT
            valueFrom:
              resourceFieldRef:
                containerName: crossplane-init
                resource: limits.memory
      containers:
      - image: "crossplane/crossplane:v1.13.0"
        args:
        - rbac
        - start
        - --manage=Basic
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
          - name: GOMAXPROCS
            valueFrom:
              resourceFieldRef:
                containerName: crossplane
                resource: limits.cpu
          - name: GOMEMLIMIT
            valueFrom:
              resourceFieldRef:
                containerName: crossplane
                resource: limits.memory
          - name: LEADER_ELECTION
            value: "true"

NOTES:
Release: crossplane

Chart Name: crossplane
Chart Description: Crossplane is an open source Kubernetes add-on that enables platform teams to assemble infrastructure from multiple vendors, and expose higher level self-service APIs for application teams to consume.
Chart Version: 1.13.0
Chart Application Version: 1.13.0

Kube Version: v1.27.4
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

Installing Crossplane creates new Kubernetes API end-points.  
Look at the new API end-points with `kubectl api-resources  | grep crossplane`.

```shell  {label="grep",copy-lines="1"}
kubectl api-resources  | grep crossplane
compositeresourcedefinitions      xrd,xrds     apiextensions.crossplane.io/v1         false        CompositeResourceDefinition
compositionrevisions              comprev      apiextensions.crossplane.io/v1         false        CompositionRevision
compositions                      comp         apiextensions.crossplane.io/v1         false        Composition
environmentconfigs                envcfg       apiextensions.crossplane.io/v1alpha1   false        EnvironmentConfig
configurationrevisions                         pkg.crossplane.io/v1                   false        ConfigurationRevision
configurations                                 pkg.crossplane.io/v1                   false        Configuration
controllerconfigs                              pkg.crossplane.io/v1alpha1             false        ControllerConfig
locks                                          pkg.crossplane.io/v1beta1              false        Lock
providerrevisions                              pkg.crossplane.io/v1                   false        ProviderRevision
providers                                      pkg.crossplane.io/v1                   false        Provider
storeconfigs                                   secrets.crossplane.io/v1alpha1         false        StoreConfig
```