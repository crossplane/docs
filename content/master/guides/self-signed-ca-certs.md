---
title: Self-signed CA certs
weight: 270
description: "Configure Crossplane with self-signed certificates"
---

{{<hint "important">}}
Using self-signed certificates isn't advised in production, it's
recommended to only use self-signed certificates for testing.
{{</hint>}}

When Crossplane loads Configuration and Provider Packages from private
registries, you must configure it to trust the CA and Intermediate certs.

You need to install Crossplane via the Helm chart with the
`registryCaBundleConfig.name` and `registryCaBundleConfig.key` parameters
defined. See [Install Crossplane]({{<ref "../get-started/install" >}}).

## Configure

1. Create a CA Bundle (a file containing your Root and Intermediate
certificates in a specific order). You can do this with any text editor or
from the command line, so long as the resulting file contains all required crt
files in the proper order. Often, this is either a single
self-signed Root CA crt file, or an Intermediate crt and Root crt file. The
order of the crt files should be from lowest to highest in signing order.
For example, if you have a chain of two certificates below your Root
certificate, you place the bottom level Intermediate cert at the beginning of
the file, then the Intermediate cert that singed that cert, then the Root cert
that signed that cert.

2. Save the files as `[yourdomain].ca-bundle`.

3. Create a Kubernetes ConfigMap in your Crossplane system namespace:

```shell
kubectl -n [Crossplane system namespace] create cm ca-bundle-config \
  --from-file=ca-bundle=./[yourdomain].ca-bundle
```

4. Set the `registryCaBundleConfig.name` Helm chart parameter to
`ca-bundle-config` and the `registryCaBundleConfig.key` parameter to
`ca-bundle`.

{{<hint "note">}}
The Helm docs cover providing Helm with parameter values during
[`helm install`](https://helm.sh/docs/helm/helm_install/). An example block
in an `override.yaml` file would look like this:
```yaml
  registryCaBundleConfig:
    name: ca-bundle-config
    key: ca-bundle
```
{{</hint>}}