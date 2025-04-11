---
title: Self-Signed CA Certs
weight: 270
---

# Crossplane
>  Using self-signed certificates isn't advised in production, it's recommended
to only use self-signed certificates for testing.

When Crossplane loads Configuration and Provider Packages from private
registries, it must be configured to trust the CA and Intermediate certs.

Crossplane needs to be installed via the Helm chart with the
`registryCaBundleConfig.name` and `registryCaBundleConfig.key` parameters
defined. See [Install Crossplane]({{<ref "../../master/software/install" >}}).

## Configure

1. Create a CA Bundle (A file containing your Root and Intermediate certificates
in a specific order). This can be done with any text editor or from the command
line, so long as the resulting file contains all required crt files in the
proper order. In many cases, this will be either a single self-signed Root CA
crt file, or an Intermediate crt and Root crt file. The order of the crt files
should be from lowest to highest in signing order. For example, if you have a
chain of two certificates below your Root certificate, you place the bottom
level Intermediate cert at the beginning of the file, then the Intermediate cert
that singed that cert, then the Root cert that signed that cert.

2. Save the files as `[yourdomain].ca-bundle`.

3. Create a Kubernetes ConfigMap in your Crossplane system namespace:

```bash
kubectl -n [Crossplane system namespace] create cm ca-bundle-config \
--from-file=ca-bundle=./[yourdomain].ca-bundle
```

4. Set the `registryCaBundleConfig.name` Helm chart parameter to
`ca-bundle-config` and the `registryCaBundleConfig.key` parameter to
`ca-bundle`.

> Providing Helm with parameter values is covered in the Helm docs,
[Helm install](https://helm.sh/docs/helm/helm_install/). An example block
in an `override.yaml` file would look like this:
```yaml
  registryCaBundleConfig:
    name: ca-bundle-config
    key: ca-bundle
```

# Providers

When operating behind a corporate firewall with injected CAs for every endpoint,
you can use your own managed CA for providers. This guide explains how to
achieve this by creating a Kubernetes ConfigMap to mount a custom certificate
bundle.

## Configure

1. Create a ConfigMap for the Certificate Bundle. To use an internal CA
   certificate file instead of the default one in the provider container, create
   a Kubernetes ConfigMap from the certificate bundle file.

Run the following command to create the ConfigMap:

```bash
kubectl create configmap -n upbound-system cert-bundle --from-file=ca-certificates.crt=/tmp/ca-certificates.crt
```

2. Create a `DeploymentRuntimeConfig` that allows customization of a provider
   installation.

```yaml
apiVersion: pkg.crossplane.io/v1beta1
kind: DeploymentRuntimeConfig
metadata:
  name: cert-bundle
spec:
  deploymentTemplate:
    spec:
      selector: {}
      strategy: {}
      template:
        spec:
          containers:
          - name: package-runtime
            resources: {}
            volumeMounts:
            - mountPath: /etc/ssl/certs
              name: cert-bundle
          volumes:
          - configMap:
              name: cert-bundle
            name: cert-bundle
```

3. Install a Provider and ensure the `runtimeConfigRef` points to the
   `DeploymentRuntimeConfig` created in the previous step.

```yaml
apiVersion: pkg.crossplane.io/v1
kind: Provider
metadata:
  name: provider-helm
spec:
  package: xpkg.upbound.io/upbound/provider-helm:v0.20.2
  runtimeConfigRef:
    apiVersion: pkg.crossplane.io/v1beta1
    kind: DeploymentRuntimeConfig
    name: cert-bundle
```

4. Confirm the Provider Installation and verify healthy by running:

```bash
kubectl get provider.pkg
```

Expected output:

```
NAME            INSTALLED   HEALTHY   PACKAGE                                                    AGE
provider-helm   True        True      xpkg.upbound.io/upbound/provider-helm:v0.20.2              13h
```

To confirm the Provider pod is running in the `crossplane-system` namespace:

```bash
kubectl get pods -n crossplane-system -l pkg.crossplane.io/provider=provider-helm
```

Expected output:

```
NAME                                          READY   STATUS    RESTARTS   AGE
provider-helm-503c3591121b-54bfdb769c-rhg8w   1/1     Running   0          13h
```

5. Verify the volume is mounted, doescribe the Provider pod:

```bash
kubectl describe pod -n crossplane-system -l pkg.crossplane.io/provider=provider-helm
```

Look for the following details in the output:
```bash
/etc/ssl/certs from cert-bundle (rw)
```

```bash
cert-bundle:
  Type:      ConfigMap (a volume populated by a ConfigMap)
  Name:      cert-bundle
  Optional:  false
```

This confirms the custom certificate bundle is properly mounted and in use.
