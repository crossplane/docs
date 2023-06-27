---
title: Vault as an External Secret Store
weight: 230
---

This guide walks through the steps required to configure Crossplane and
its Providers to use [Vault] as an [External Secret Store] (`ESS`) with [ESS Plugin Vault].

{{<hint "warning" >}}
External Secret Stores are an alpha feature.

They're not recommended for production use. Crossplane disables External Secret
Stores by default.
{{< /hint >}}

Crossplane uses sensitive information including Provider credentials, inputs to
managed resources and connection details.

The [Vault credential injection guide]({{<ref "vault-injection" >}}) details
using Vault and Crossplane for Provider credentials.

Crossplane doesn't support for using Vault for managed resources input.
[Crossplane issue #2985](https://github.com/crossplane/crossplane/issues/2985)
tracks support for this feature.

Supporting connection details with Vault requires a Crossplane external secret
store.

## Prerequisites
This guide requires [Helm](https://helm.sh) version 3.11 or later.

## Install Vault

{{<hint "note" >}}
Detailed instructions on [installing
Vault](https://developer.hashicorp.com/vault/docs/platform/k8s/helm)
are available from the Vault documentation.
{{< /hint >}}

### Add the Vault Helm chart

Add the Helm repository for `hashicorp`.
```shell
helm repo add hashicorp https://helm.releases.hashicorp.com --force-update 
```

Install Vault using Helm.
```shell
helm -n vault-system upgrade --install vault hashicorp/vault --create-namespace
```

### Unseal Vault

If Vault is [sealed](https://developer.hashicorp.com/vault/docs/concepts/seal)
unseal Vault using the unseal keys.

Get the Vault keys.
```shell
kubectl -n vault-system exec vault-0 -- vault operator init -key-shares=1 -key-threshold=1 -format=json > cluster-keys.json
VAULT_UNSEAL_KEY=$(cat cluster-keys.json | jq -r ".unseal_keys_b64[]")
```

Unseal the vault using the keys.
```shell {copy-lines="1"}
kubectl -n vault-system exec vault-0 -- vault operator unseal $VAULT_UNSEAL_KEY
Key             Value
---             -----
Seal Type       shamir
Initialized     true
Sealed          false
Total Shares    1
Threshold       1
Version         1.13.1
Build Date      2023-03-23T12:51:35Z
Storage Type    file
Cluster Name    vault-cluster-df884357
Cluster ID      b3145d26-2c1a-a7f2-a364-81753033c0d9
HA Enabled      false
```

## Configure Vault Kubernetes authentication

Enable the [Kubernetes auth method] for Vault to authenticate requests based on
Kubernetes service accounts.

### Get the Vault root token

The Vault root token is inside the JSON file created when
[unsealing Vault](#unseal-vault).

```shell
cat cluster-keys.json | jq -r ".root_token"
```

### Enable Kubernetes authentication

Connect to a shell in the Vault pod.

```shell {copy-lines="1"}
kubectl -n vault-system exec -it vault-0 -- /bin/sh
/ $
```

From the Vault shell, login to Vault using the _root token_.
```shell {copy-lines="1"}
vault login # use the root token from above
Token (will be hidden):
Success! You are now authenticated. The token information displayed below
is already stored in the token helper. You do NOT need to run "vault login"
again. Future Vault requests will automatically use this token.

Key                  Value
---                  -----
token                hvs.TSN4SssfMBM0HAtwGrxgARgn
token_accessor       qodxHrINVlRXKyrGeeDkxnih
token_duration       ∞
token_renewable      false
token_policies       ["root"]
identity_policies    []
policies             ["root"]
```

Enable the Kubernetes authentication method in Vault.
```shell {copy-lines="1"}
vault auth enable kubernetes
Success! Enabled kubernetes auth method at: kubernetes/
```

Configure Vault to communicate with Kubernetes and exit the Vault shell

```shell {copy-lines="1-4"}
vault write auth/kubernetes/config \
        token_reviewer_jwt="$(cat /var/run/secrets/kubernetes.io/serviceaccount/token)" \
        kubernetes_host="https://$KUBERNETES_PORT_443_TCP_ADDR:443" \
        kubernetes_ca_cert=@/var/run/secrets/kubernetes.io/serviceaccount/ca.crt
Success! Data written to: auth/kubernetes/config
/ $ exit
```

## Configure Vault for Crossplane integration

Crossplane relies on the Vault key-value secrets engine to store information and
Vault requires a permissions policy for the Crossplane service account.

<!-- vale Crossplane.Spelling = NO -->
<!-- allow "kv" -->
### Enable the Vault kv secrets engine
<!-- vale Crossplane.Spelling = YES -->

Enable the [Vault KV Secrets Engine].

{{< hint "important" >}}
Vault has two versions of the
[KV Secrets Engine](https://developer.hashicorp.com/vault/docs/secrets/kv).
This example uses version 2.
{{</hint >}}

```shell {copy-lines="1"}
kubectl -n vault-system exec -it vault-0 -- vault secrets enable -path=secret kv-v2
Success! Enabled the kv-v2 secrets engine at: secret/
```

### Create a Vault policy for Crossplane

Create the Vault policy to allow Crossplane to read and write data from Vault.
```shell {copy-lines="1-8"}
kubectl -n vault-system exec -i vault-0 -- vault policy write crossplane - <<EOF
path "secret/data/*" {
    capabilities = ["create", "read", "update", "delete"]
}
path "secret/metadata/*" {
    capabilities = ["create", "read", "update", "delete"]
}
EOF
Success! Uploaded policy: crossplane
```

Apply the policy to Vault.
```shell {copy-lines="1-5"}
kubectl -n vault-system exec -it vault-0 -- vault write auth/kubernetes/role/crossplane \
    bound_service_account_names="*" \
    bound_service_account_namespaces=crossplane-system \
    policies=crossplane \
    ttl=24h
Success! Data written to: auth/kubernetes/role/crossplane
```

## Install Crossplane

{{<hint "important" >}}
Crossplane v1.12 introduced the plugin support. Make sure your version of Crossplane supports plugins.
{{< /hint >}}

Install the Crossplane with the External Secrets Stores feature enabled.

```shell 
helm upgrade --install crossplane crossplane-stable/crossplane --namespace crossplane-system --create-namespace --set args='{--enable-external-secret-stores}'
```

## Install the Crossplane Vault plugin

The Crossplane Vault plugin isn't part of the default Crossplane install.
The plugin installs as a unique Pod that uses the [Vault Agent Sidecar
Injection] to connect the Vault secret store to Crossplane.

First, configure annotations for the Vault plugin pod.

```yaml
cat > values.yaml <<EOF
podAnnotations:
  vault.hashicorp.com/agent-inject: "true"
  vault.hashicorp.com/agent-inject-token: "true"
  vault.hashicorp.com/role: crossplane
  vault.hashicorp.com/agent-run-as-user: "65532"
EOF
```
Next, install the Crossplane ESS Plugin pod to the `crossplane-system` namespace
and apply the Vault annotations.

```shell
helm upgrade --install ess-plugin-vault oci://xpkg.upbound.io/crossplane-contrib/ess-plugin-vault --namespace crossplane-system -f values.yaml
```

## Configure Crossplane

Using the Vault plugin requires configuration to connect to the Vault
service. The plugin also requires Providers to enable external secret stores.

With the plugin and providers configured, Crossplane requires two `StoreConfig`
objects to describe how Crossplane and the Providers communicate with vault.

### Enable external secret stores in the Provider

{{<hint "note">}}
This example uses Provider GCP, but the
{{<hover label="ControllerConfig" line="2">}}ControllerConfig{{</hover>}} is the
same for all Providers.
{{</hint >}}

Create a `ControllerConfig` object to enable external secret stores.

```yaml {label="ControllerConfig"}
echo "apiVersion: pkg.crossplane.io/v1alpha1
kind: ControllerConfig
metadata:
  name: vault-config
spec:
  args:
    - --enable-external-secret-stores" | kubectl apply -f -
```

Install the Provider and apply the ControllerConfig.
```yaml
echo "apiVersion: pkg.crossplane.io/v1
kind: Provider
metadata:
  name: provider-gcp
spec:
  package: xpkg.upbound.io/crossplane-contrib/provider-gcp:v0.23.0-rc.0.19.ge9b75ee5
  controllerConfigRef:
    name: vault-config" | kubectl apply -f -
```

### Connect the Crossplane plugin to Vault
Create a {{<hover label="VaultConfig" line="2">}}VaultConfig{{</hover>}}
resource for the plugin to connect to the Vault service:

```yaml {label="VaultConfig"}
echo "apiVersion: secrets.crossplane.io/v1alpha1
kind: VaultConfig
metadata:
  name: vault-internal
spec:
  server: http://vault.vault-system:8200
  mountPath: secret/
  version: v2
  auth:
    method: Token
    token:
      source: Filesystem
      fs:
        path: /vault/secrets/token" | kubectl apply -f -
```

### Create a Crossplane StoreConfig

Create a {{<hover label="xp-storeconfig" line="2">}}StoreConfig{{</hover >}}
object from the
{{<hover label="xp-storeconfig" line="1">}}secrets.crossplane.io{{</hover >}}
group. Crossplane uses the StoreConfig to connect to the Vault plugin service.

The {{<hover label="xp-storeconfig" line="10">}}configRef{{</hover >}} connects
the StoreConfig to the specific Vault plugin configuration.

```yaml {label="xp-storeconfig"}
echo "apiVersion: secrets.crossplane.io/v1alpha1
kind: StoreConfig
metadata:
  name: vault
spec:
  type: Plugin
  defaultScope: crossplane-system
  plugin:
    endpoint: ess-plugin-vault.crossplane-system:4040
    configRef:
      apiVersion: secrets.crossplane.io/v1alpha1
      kind: VaultConfig
      name: vault-internal" | kubectl apply -f -
```


### Create a Provider StoreConfig
Create a {{<hover label="gcp-storeconfig" line="2">}}StoreConfig{{</hover >}}
object from the Provider's API group,
{{<hover label="gcp-storeconfig" line="1">}}gcp.crossplane.io{{</hover >}}.
The Provider uses this StoreConfig to communicate with Vault for
Managed Resources.

The {{<hover label="gcp-storeconfig" line="10">}}configRef{{</hover >}} connects
the StoreConfig to the specific Vault plugin configuration.

```yaml {label="gcp-storeconfig"}
echo "apiVersion: gcp.crossplane.io/v1alpha1
kind: StoreConfig
metadata:
  name: vault
spec:
  type: Plugin
  defaultScope: crossplane-system
  plugin:
    endpoint: ess-plugin-vault.crossplane-system:4040
    configRef:
      apiVersion: secrets.crossplane.io/v1alpha1
      kind: VaultConfig
      name: vault-internal" | kubectl apply -f -
```

## Create Provider resources

Check that Crossplane installed the Provider and the Provider is healthy.

```shell {copy-lines="1"}
kubectl get providers
NAME           INSTALLED   HEALTHY   PACKAGE                                                                     AGE
provider-gcp   True        True      xpkg.upbound.io/crossplane-contrib/provider-gcp:v0.23.0-rc.0.19.ge9b75ee5   10m
```

### Create a CompositeResourceDefinition

Create a `CompositeResourceDefinition` to define a custom API endpoint.

```yaml
echo "apiVersion: apiextensions.crossplane.io/v1
kind: CompositeResourceDefinition
metadata:
  name: compositeessinstances.ess.example.org
  annotations:
    feature: ess
spec:
  group: ess.example.org
  names:
    kind: CompositeESSInstance
    plural: compositeessinstances
  claimNames:
    kind: ESSInstance
    plural: essinstances
  connectionSecretKeys:
    - publicKey
    - publicKeyType
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
              parameters:
                type: object
                properties:
                  serviceAccount:
                    type: string
                required:
                  - serviceAccount
            required:
              - parameters" | kubectl apply -f -
```

### Create a Composition
Create a `Composition` to create a Service Account and Service Account Key
inside GCP.

Creating a Service Account Key generates
{{<hover label="comp" line="39" >}}connectionDetails{{</hover>}} that the
Provider stores in Vault using the
{{<hover label="comp" line="31">}}publishConnectionDetailsTo{{</hover>}} details.

```yaml {label="comp"}
echo "apiVersion: apiextensions.crossplane.io/v1
kind: Composition
metadata:
  name: essinstances.ess.example.org
  labels:
    feature: ess
spec:
  publishConnectionDetailsWithStoreConfigRef: 
    name: vault
  compositeTypeRef:
    apiVersion: ess.example.org/v1alpha1
    kind: CompositeESSInstance
  resources:
    - name: serviceaccount
      base:
        apiVersion: iam.gcp.crossplane.io/v1alpha1
        kind: ServiceAccount
        metadata:
          name: ess-test-sa
        spec:
          forProvider:
            displayName: a service account to test ess
    - name: serviceaccountkey
      base:
        apiVersion: iam.gcp.crossplane.io/v1alpha1
        kind: ServiceAccountKey
        spec:
          forProvider:
            serviceAccountSelector:
              matchControllerRef: true
          publishConnectionDetailsTo:
            name: ess-mr-conn
            metadata:
              labels:
                environment: development
                team: backend
            configRef:
              name: vault
      connectionDetails:
        - fromConnectionSecretKey: publicKey
        - fromConnectionSecretKey: publicKeyType" | kubectl apply -f -
```

### Create a Claim
Now create a `Claim` to have Crossplane create the GCP resources and associated
secrets.

Like the Composition, the Claim uses
{{<hover label="claim" line="12">}}publishConnectionDetailsTo{{</hover>}} to
connect to Vault and store the secrets.

```yaml {label="claim"}
echo "apiVersion: ess.example.org/v1alpha1
kind: ESSInstance
metadata:
  name: my-ess
  namespace: default
spec:
  parameters:
    serviceAccount: ess-test-sa
  compositionSelector:
    matchLabels:
      feature: ess
  publishConnectionDetailsTo:
    name: ess-claim-conn
    metadata:
      labels:
        environment: development
        team: backend
    configRef:
      name: vault" | kubectl apply -f -
```

## Verify the resources

Verify all resources are `READY` and `SYNCED`:

```shell {copy-lines="1"}
kubectl get managed
NAME                                                      READY   SYNCED   DISPLAYNAME                     EMAIL                                                            DISABLED
serviceaccount.iam.gcp.crossplane.io/my-ess-zvmkz-vhklg   True    True     a service account to test ess   my-ess-zvmkz-vhklg@testingforbugbounty.iam.gserviceaccount.com

NAME                                                         READY   SYNCED   KEY_ID                                     CREATED_AT             EXPIRES_AT
serviceaccountkey.iam.gcp.crossplane.io/my-ess-zvmkz-bq8pz   True    True     5cda49b7c32393254b5abb121b4adc07e140502c   2022-03-23T10:54:50Z
```

View the claims
```shell {copy-lines="1"}
kubectl -n default get claim
NAME     READY   CONNECTION-SECRET   AGE
my-ess   True                        19s
```

View the composite resources.
```shell {copy-lines="1"}
kubectl get composite
NAME           READY   COMPOSITION                    AGE
my-ess-zvmkz   True    essinstances.ess.example.org   32s
```

## Verify Vault secrets

Look inside Vault to view the secrets from the managed resources.

```shell {copy-lines="1",label="vault-key"}
kubectl -n vault-system exec -i vault-0 -- vault kv list /secret/default
Keys
----
ess-claim-conn
```

The key {{<hover label="vault-key" line="4">}}ess-claim-conn{{</hover>}}
is the name of the Claim's
{{<hover label="claim" line="12">}}publishConnectionDetailsTo{{</hover>}}
configuration.

Check connection secrets in the "crossplane-system" Vault scope.
```shell {copy-lines="1",label="scope-key"}
kubectl -n vault-system exec -i vault-0 -- vault kv list /secret/crossplane-system
Keys
----
d2408335-eb88-4146-927b-8025f405da86
ess-mr-conn
```

The key
{{<hover label="scope-key"line="4">}}d2408335-eb88-4146-927b-8025f405da86{{</hover>}}
comes from

<!-- ## WHERE DOES IT COME FROM? -->

and the key
{{<hover label="scope-key"line="5">}}ess-mr-conn{{</hover>}}
comes from the Composition's
{{<hover label="comp" line="31">}}publishConnectionDetailsTo{{</hover>}}
configuration.


Check contents of Claim's connection secret `ess-claim-conn` to see the key
created by the managed resource.
```shell {copy-lines="1"}
kubectl -n vault-system exec -i vault-0 -- vault kv get /secret/default/ess-claim-conn
======= Metadata =======
Key                Value
---                -----
created_time       2022-03-18T21:24:07.2085726Z
custom_metadata    map[environment:development secret.crossplane.io/ner-uid:881cd9a0-6cc6-418f-8e1d-b36062c1e108 team:backend]
deletion_time      n/a
destroyed          false
version            1

======== Data ========
Key              Value
---              -----
publicKey        -----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAzsEYCokmYEsZJCc9QN/8
Fm1M/kTPp7Gat/MXLTP3zFyCTBFVNLN79MbAKdinWi6ePXEb75vzB79IdZcWj8lo
8trnS64QjNB9Vs4Xk5UvDALwleFN/bZeperxivDPwVPvT9Aqy/U9kohoS/LHyE8w
uWQb5AuMeVQ1gtCTnCqQZ4d2MSVhQXYVvAWax1spJ9LT7mHub5j95xDdYIcOV3VJ
l9CIo4VrWIT8THFN2NnjTrGq9+0TzXY0bV674bjJkfBC6v6yXs5HTetG+Uekq/xf
FCjrrDi1+2UR9Mu2WTuvl8qn50be+mbwdJO5wE32jewxdYrVVmj19+PkaEeAwGTc
vwIDAQAB
-----END PUBLIC KEY-----
publicKeyType    TYPE_RAW_PUBLIC_KEY
```

Check contents of managed resource connection secret `ess-mr-conn`. The public
key is identical to the public key in the Claim since the Claim is using this
managed resource.
```shell {copy-lines="1"}
kubectl -n vault-system exec -i vault-0 -- vault kv get /secret/crossplane-system/ess-mr-conn
======= Metadata =======
Key                Value
---                -----
created_time       2022-03-18T21:21:07.9298076Z
custom_metadata    map[environment:development secret.crossplane.io/ner-uid:4cd973f8-76fc-45d6-ad45-0b27b5e9252a team:backend]
deletion_time      n/a
destroyed          false
version            2

========= Data =========
Key               Value
---               -----
privateKey        {
  "type": "service_account",
  "project_id": "REDACTED",
  "private_key_id": "REDACTED",
  "private_key": "-----BEGIN PRIVATE KEY-----\nREDACTED\n-----END PRIVATE KEY-----\n",
  "client_email": "ess-test-sa@REDACTED.iam.gserviceaccount.com",
  "client_id": "REDACTED",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/ess-test-sa%40REDACTED.iam.gserviceaccount.com"
}
privateKeyType    TYPE_GOOGLE_CREDENTIALS_FILE
publicKey         -----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAzsEYCokmYEsZJCc9QN/8
Fm1M/kTPp7Gat/MXLTP3zFyCTBFVNLN79MbAKdinWi6ePXEb75vzB79IdZcWj8lo
8trnS64QjNB9Vs4Xk5UvDALwleFN/bZeperxivDPwVPvT9Aqy/U9kohoS/LHyE8w
uWQb5AuMeVQ1gtCTnCqQZ4d2MSVhQXYVvAWax1spJ9LT7mHub5j95xDdYIcOV3VJ
l9CIo4VrWIT8THFN2NnjTrGq9+0TzXY0bV674bjJkfBC6v6yXs5HTetG+Uekq/xf
FCjrrDi1+2UR9Mu2WTuvl8qn50be+mbwdJO5wE32jewxdYrVVmj19+PkaEeAwGTc
vwIDAQAB
-----END PUBLIC KEY-----
publicKeyType     TYPE_RAW_PUBLIC_KEY
```

### Remove the resources

Deleting the Claim removes the managed resources and associated keys from Vault.

```shell
kubectl delete claim my-ess
```

<!-- named links -->

[Vault]: https://www.vaultproject.io/
[External Secret Store]: https://github.com/crossplane/crossplane/blob/master/design/design-doc-external-secret-stores.md
[this issue]: https://github.com/crossplane/crossplane/issues/2985
[Kubernetes Auth Method]: https://www.vaultproject.io/docs/auth/kubernetes
[Unseal]: https://www.vaultproject.io/docs/concepts/seal
[Vault KV Secrets Engine]: https://developer.hashicorp.com/vault/docs/secrets/kv
[Vault Agent Sidecar Injection]: https://www.vaultproject.io/docs/platform/k8s/injector
[ESS Plugin Vault]: https://github.com/crossplane-contrib/ess-plugin-vault