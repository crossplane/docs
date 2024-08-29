---
tocHidden: true
searchExclude: true
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
install.go:214: [debug] Original chart version: ""
install.go:216: [debug] setting version to >0.0.0-0
install.go:231: [debug] CHART PATH: /Users/plumbis/Library/Caches/helm/repository/crossplane-1.15.0.tgz

NAME: crossplane
LAST DEPLOYED: Mon Feb 12 14:46:15 2024
NAMESPACE: default
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
extraObjects: []
extraVolumeMountsCrossplane: {}
extraVolumesCrossplane: {}
function:
  packages: []
hostNetwork: false
image:
  pullPolicy: IfNotPresent
  repository: xpkg.upbound.io/crossplane/crossplane
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

HOOKS:
MANIFEST:
---
# Source: crossplane/templates/rbac-manager-serviceaccount.yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: rbac-manager
  namespace: default
  labels:
    app: crossplane
    helm.sh/chart: crossplane-1.15.0
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/component: cloud-infrastructure-controller
    app.kubernetes.io/part-of: crossplane
    app.kubernetes.io/name: crossplane
    app.kubernetes.io/instance: crossplane
    app.kubernetes.io/version: "1.15.0"
---
# Source: crossplane/templates/serviceaccount.yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: crossplane
  namespace: default
  labels:
    app: crossplane
    helm.sh/chart: crossplane-1.15.0
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/component: cloud-infrastructure-controller
    app.kubernetes.io/part-of: crossplane
    app.kubernetes.io/name: crossplane
    app.kubernetes.io/instance: crossplane
    app.kubernetes.io/version: "1.15.0"
---
# Source: crossplane/templates/secret.yaml
# The reason this is created empty and filled by the init container is we want
# to manage the lifecycle of the secret via Helm. This way whenever Crossplane
# is deleted, the secret is deleted as well.
apiVersion: v1
kind: Secret
metadata:
  name: crossplane-root-ca
  namespace: default
type: Opaque
---
# Source: crossplane/templates/secret.yaml
# The reason this is created empty and filled by the init container is we want
# to manage the lifecycle of the secret via Helm. This way whenever Crossplane
# is deleted, the secret is deleted as well.
apiVersion: v1
kind: Secret
metadata:
  name: crossplane-tls-server
  namespace: default
type: Opaque
---
# Source: crossplane/templates/secret.yaml
# The reason this is created empty and filled by the init container is we want
# to manage the lifecycle of the secret via Helm. This way whenever Crossplane
# is deleted, the secret is deleted as well.
apiVersion: v1
kind: Secret
metadata:
  name: crossplane-tls-client
  namespace: default
type: Opaque
---
# Source: crossplane/templates/clusterrole.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: crossplane
  labels:
    app: crossplane
    helm.sh/chart: crossplane-1.15.0
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/component: cloud-infrastructure-controller
    app.kubernetes.io/part-of: crossplane
    app.kubernetes.io/name: crossplane
    app.kubernetes.io/instance: crossplane
    app.kubernetes.io/version: "1.15.0"
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
    helm.sh/chart: crossplane-1.15.0
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/component: cloud-infrastructure-controller
    app.kubernetes.io/part-of: crossplane
    app.kubernetes.io/name: crossplane
    app.kubernetes.io/instance: crossplane
    app.kubernetes.io/version: "1.15.0"
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
  - customresourcedefinitions/status
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
    helm.sh/chart: crossplane-1.15.0
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/component: cloud-infrastructure-controller
    app.kubernetes.io/part-of: crossplane
    app.kubernetes.io/name: crossplane
    app.kubernetes.io/instance: crossplane
    app.kubernetes.io/version: "1.15.0"
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
    helm.sh/chart: crossplane-1.15.0
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/component: cloud-infrastructure-controller
    app.kubernetes.io/part-of: crossplane
    app.kubernetes.io/name: crossplane
    app.kubernetes.io/instance: crossplane
    app.kubernetes.io/version: "1.15.0"
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
  verbs:
  - get
  - list
  - watch
- apiGroups:
    - apps
  resources:
    - deployments
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
    helm.sh/chart: crossplane-1.15.0
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/component: cloud-infrastructure-controller
    app.kubernetes.io/part-of: crossplane
    app.kubernetes.io/name: crossplane
    app.kubernetes.io/instance: crossplane
    app.kubernetes.io/version: "1.15.0"
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
    helm.sh/chart: crossplane-1.15.0
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/component: cloud-infrastructure-controller
    app.kubernetes.io/part-of: crossplane
    app.kubernetes.io/name: crossplane
    app.kubernetes.io/instance: crossplane
    app.kubernetes.io/version: "1.15.0"
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
    helm.sh/chart: crossplane-1.15.0
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/component: cloud-infrastructure-controller
    app.kubernetes.io/part-of: crossplane
    app.kubernetes.io/name: crossplane
    app.kubernetes.io/instance: crossplane
    app.kubernetes.io/version: "1.15.0"
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
    helm.sh/chart: crossplane-1.15.0
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/component: cloud-infrastructure-controller
    app.kubernetes.io/part-of: crossplane
    app.kubernetes.io/name: crossplane
    app.kubernetes.io/instance: crossplane
    app.kubernetes.io/version: "1.15.0"
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
    helm.sh/chart: crossplane-1.15.0
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/component: cloud-infrastructure-controller
    app.kubernetes.io/part-of: crossplane
    app.kubernetes.io/name: crossplane
    app.kubernetes.io/instance: crossplane
    app.kubernetes.io/version: "1.15.0"
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
  resources: ["*"]
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
    helm.sh/chart: crossplane-1.15.0
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/component: cloud-infrastructure-controller
    app.kubernetes.io/part-of: crossplane
    app.kubernetes.io/name: crossplane
    app.kubernetes.io/instance: crossplane
    app.kubernetes.io/version: "1.15.0"
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
  resources: ["*"]
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
    helm.sh/chart: crossplane-1.15.0
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/component: cloud-infrastructure-controller
    app.kubernetes.io/part-of: crossplane
    app.kubernetes.io/name: crossplane
    app.kubernetes.io/instance: crossplane
    app.kubernetes.io/version: "1.15.0"
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
  resources: ["*"]
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
    helm.sh/chart: crossplane-1.15.0
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/component: cloud-infrastructure-controller
    app.kubernetes.io/part-of: crossplane
    app.kubernetes.io/name: crossplane
    app.kubernetes.io/instance: crossplane
    app.kubernetes.io/version: "1.15.0"
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
# Source: crossplane/templates/clusterrolebinding.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: crossplane
  labels:
    app: crossplane
    helm.sh/chart: crossplane-1.15.0
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/component: cloud-infrastructure-controller
    app.kubernetes.io/part-of: crossplane
    app.kubernetes.io/name: crossplane
    app.kubernetes.io/instance: crossplane
    app.kubernetes.io/version: "1.15.0"
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: crossplane
subjects:
- kind: ServiceAccount
  name: crossplane
  namespace: default
---
# Source: crossplane/templates/rbac-manager-clusterrolebinding.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: crossplane-rbac-manager
  labels:
    app: crossplane
    helm.sh/chart: crossplane-1.15.0
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/component: cloud-infrastructure-controller
    app.kubernetes.io/part-of: crossplane
    app.kubernetes.io/name: crossplane
    app.kubernetes.io/instance: crossplane
    app.kubernetes.io/version: "1.15.0"
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: crossplane-rbac-manager
subjects:
- kind: ServiceAccount
  name: rbac-manager
  namespace: default
---
# Source: crossplane/templates/rbac-manager-managed-clusterroles.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: crossplane-admin
  labels:
    app: crossplane
    helm.sh/chart: crossplane-1.15.0
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/component: cloud-infrastructure-controller
    app.kubernetes.io/part-of: crossplane
    app.kubernetes.io/name: crossplane
    app.kubernetes.io/instance: crossplane
    app.kubernetes.io/version: "1.15.0"
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
  namespace: default
  labels:
    app: crossplane
    release: crossplane
    helm.sh/chart: crossplane-1.15.0
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/component: cloud-infrastructure-controller
    app.kubernetes.io/part-of: crossplane
    app.kubernetes.io/name: crossplane
    app.kubernetes.io/instance: crossplane
    app.kubernetes.io/version: "1.15.0"
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
  namespace: default
  labels:
    app: crossplane
    release: crossplane
    helm.sh/chart: crossplane-1.15.0
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/component: cloud-infrastructure-controller
    app.kubernetes.io/part-of: crossplane
    app.kubernetes.io/name: crossplane
    app.kubernetes.io/instance: crossplane
    app.kubernetes.io/version: "1.15.0"
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
        helm.sh/chart: crossplane-1.15.0
        app.kubernetes.io/managed-by: Helm
        app.kubernetes.io/component: cloud-infrastructure-controller
        app.kubernetes.io/part-of: crossplane
        app.kubernetes.io/name: crossplane
        app.kubernetes.io/instance: crossplane
        app.kubernetes.io/version: "1.15.0"
    spec:
      serviceAccountName: crossplane
      hostNetwork: false
      initContainers:
        - image: "xpkg.upbound.io/crossplane/crossplane:v1.15.0"
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
                divisor: "1"
          - name: GOMEMLIMIT
            valueFrom:
              resourceFieldRef:
                containerName: crossplane-init
                resource: limits.memory
                divisor: "1"
          - name: POD_NAMESPACE
            valueFrom:
              fieldRef:
                fieldPath: metadata.namespace
          - name: POD_SERVICE_ACCOUNT
            valueFrom:
              fieldRef:
                fieldPath: spec.serviceAccountName
          - name: "WEBHOOK_SERVICE_NAME"
            value: crossplane-webhooks
          - name: "WEBHOOK_SERVICE_NAMESPACE"
            valueFrom:
              fieldRef:
                fieldPath: metadata.namespace
          - name: "WEBHOOK_SERVICE_PORT"
            value: "9443"
          - name: "TLS_CA_SECRET_NAME"
            value: crossplane-root-ca
          - name: "TLS_SERVER_SECRET_NAME"
            value: crossplane-tls-server
          - name: "TLS_CLIENT_SECRET_NAME"
            value: crossplane-tls-client
      containers:
      - image: "xpkg.upbound.io/crossplane/crossplane:v1.15.0"
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
        startupProbe:
          failureThreshold: 30
          periodSeconds: 2
          tcpSocket:
            port: readyz
        ports:
        - name: readyz
          containerPort: 8081
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
                divisor: "1"
          - name: GOMEMLIMIT
            valueFrom:
              resourceFieldRef:
                containerName: crossplane
                resource: limits.memory
                divisor: "1"
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
          - name: "TLS_SERVER_SECRET_NAME"
            value: crossplane-tls-server
          - name: "TLS_SERVER_CERTS_DIR"
            value: /tls/server
          - name: "TLS_CLIENT_SECRET_NAME"
            value: crossplane-tls-client
          - name: "TLS_CLIENT_CERTS_DIR"
            value: /tls/client
        volumeMounts:
          - mountPath: /cache
            name: package-cache
          - mountPath: /tls/server
            name: tls-server-certs
          - mountPath: /tls/client
            name: tls-client-certs
      volumes:
      - name: package-cache
        emptyDir:
          medium:
          sizeLimit: 20Mi
      - name: tls-server-certs
        secret:
          secretName: crossplane-tls-server
      - name: tls-client-certs
        secret:
          secretName: crossplane-tls-client
---
# Source: crossplane/templates/rbac-manager-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: crossplane-rbac-manager
  namespace: default
  labels:
    app: crossplane-rbac-manager
    release: crossplane
    helm.sh/chart: crossplane-1.15.0
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/component: cloud-infrastructure-controller
    app.kubernetes.io/part-of: crossplane
    app.kubernetes.io/name: crossplane
    app.kubernetes.io/instance: crossplane
    app.kubernetes.io/version: "1.15.0"
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
        helm.sh/chart: crossplane-1.15.0
        app.kubernetes.io/managed-by: Helm
        app.kubernetes.io/component: cloud-infrastructure-controller
        app.kubernetes.io/part-of: crossplane
        app.kubernetes.io/name: crossplane
        app.kubernetes.io/instance: crossplane
        app.kubernetes.io/version: "1.15.0"
    spec:
      serviceAccountName: rbac-manager
      initContainers:
      - image: "xpkg.upbound.io/crossplane/crossplane:v1.15.0"
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
      - image: "xpkg.upbound.io/crossplane/crossplane:v1.15.0"
        args:
        - rbac
        - start
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
Chart Version: 1.15.0
Chart Application Version: 1.15.0

Kube Version: v1.27.3
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
usages                                         apiextensions.crossplane.io/v1alpha1   false        Usage
configurationrevisions                         pkg.crossplane.io/v1                   false        ConfigurationRevision
configurations                                 pkg.crossplane.io/v1                   false        Configuration
controllerconfigs                              pkg.crossplane.io/v1alpha1             false        ControllerConfig
deploymentruntimeconfigs                       pkg.crossplane.io/v1beta1              false        DeploymentRuntimeConfig
functionrevisions                              pkg.crossplane.io/v1beta1              false        FunctionRevision
functions                                      pkg.crossplane.io/v1beta1              false        Function
locks                                          pkg.crossplane.io/v1beta1              false        Lock
providerrevisions                              pkg.crossplane.io/v1                   false        ProviderRevision
providers                                      pkg.crossplane.io/v1                   false        Provider
storeconfigs                                   secrets.crossplane.io/v1alpha1         false        StoreConfig
```