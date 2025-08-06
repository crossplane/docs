---
title: Get Started With Operations
weight: 300
state: alpha
alphaVersion: 2.0
---

This guide shows how to use Crossplane Operations to automate day-two
operational tasks. You create an Operation that checks SSL certificate
expiry for a website.

**Crossplane calls this _Operations_.** Operations run function pipelines to
perform tasks that don't fit the typical resource creation pattern - like
certificate monitoring, rolling upgrades, or scheduled maintenance.

An Operation looks like this:

```yaml
apiVersion: ops.crossplane.io/v1alpha1
kind: Operation
metadata:
  name: check-cert-expiry
spec:
  mode: Pipeline
  pipeline:
  - step: check-certificate
    functionRef:
      name: crossplane-contrib-function-python
    input:
      apiVersion: python.fn.crossplane.io/v1beta1
      kind: Script
      script: |
        import ssl
        import socket
        from datetime import datetime

        from crossplane.function import request, response

        def operate(req, rsp):
            hostname = "google.com"
            port = 443

            # Get SSL certificate info
            context = ssl.create_default_context()
            with socket.create_connection((hostname, port)) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()

            # Parse expiration date
            expiry_date = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
            days_until_expiry = (expiry_date - datetime.now()).days

            # Return results in operation output
            response.set_output(rsp, {
                "hostname": hostname,
                "certificateExpires": cert['notAfter'],
                "daysUntilExpiry": days_until_expiry,
                "status": "warning" if days_until_expiry < 30 else "ok"
            })
```

<!-- vale Crossplane.Spelling = NO -->
**The Operation runs once to completion, like a Kubernetes Job.**
<!-- vale Crossplane.Spelling = YES -->

When you create the Operation, Crossplane runs the function pipeline. The
function checks SSL certificate expiry for google.com and returns the results
in the operation's output.

This basic example shows the concept. In the walkthrough below, you create
a more realistic Operation that reads Kubernetes Ingress resources and
annotates them with certificate expiry information for monitoring tools.

## Prerequisites

This guide requires:

* A Kubernetes cluster with at least 2 GB of RAM
* The Crossplane v2 preview [installed on the Kubernetes cluster]({{<ref "install">}}) with Operations enabled

{{<hint "tip">}}
Enable Operations by adding `--enable-operations` to Crossplane's startup
arguments. If using Helm:

```shell
helm upgrade --install crossplane crossplane-stable/crossplane \
  --namespace crossplane-system \
  --set args='{"--enable-operations"}'
```
{{</hint>}}

## Create an operation

Follow these steps to create your first Operation:

1. [Create a sample Ingress](#create-a-sample-ingress) for certificate checking
1. [Install the function](#install-the-function) you want to use for the
   operation
1. [Create the Operation](#create-the-operation) that checks the Ingress
1. [Check the Operation](#check-the-operation) as it runs

### Create a sample Ingress

Create an Ingress that references a real hostname but doesn't route actual
traffic:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: example-app
  namespace: default
spec:
  rules:
  - host: google.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: nonexistent-service
            port:
              number: 80
```

Save as `ingress.yaml` and apply it:

```shell
kubectl apply -f ingress.yaml
```

### Grant Ingress permissions

Operations need permission to access and change Ingresses. Create a ClusterRole
that grants Crossplane access to Ingresses:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: operations-ingress-access
  labels:
    rbac.crossplane.io/aggregate-to-crossplane: "true"
rules:
- apiGroups: ["networking.k8s.io"]
  resources: ["ingresses"]
  verbs: ["get", "list", "watch", "patch", "update"]
```

Save as `ingress-rbac.yaml` and apply it:

```shell
kubectl apply -f ingress-rbac.yaml
```

### Install the function

Operations use operation functions to implement their logic. Use the Python
function, which supports both composition and operations.

Create this function to install Python support:

```yaml
apiVersion: pkg.crossplane.io/v1
kind: Function
metadata:
  name: crossplane-contrib-function-python
spec:
  package: xpkg.crossplane.io/crossplane-contrib/function-python:v0.2.0
```

Save the function as `function.yaml` and apply it:

```shell
kubectl apply -f function.yaml
```

Check that Crossplane installed the function:

```shell {copy-lines="1"}
kubectl get -f function.yaml
NAME                                 INSTALLED   HEALTHY   PACKAGE                                                        AGE
crossplane-contrib-function-python   True        True      xpkg.crossplane.io/crossplane-contrib/function-python:v0.2.0   12s
```

### Create the operation

Create this Operation that monitors the Ingress certificate:

```yaml
apiVersion: ops.crossplane.io/v1alpha1
kind: Operation
metadata:
  name: ingress-cert-monitor
spec:
  mode: Pipeline
  pipeline:
  - step: check-ingress-certificate
    functionRef:
      name: crossplane-contrib-function-python
    requirements:
      requiredResources:
      - requirementName: ingress
        apiVersion: networking.k8s.io/v1
        kind: Ingress
        name: example-app
        namespace: default
    input:
      apiVersion: python.fn.crossplane.io/v1beta1
      kind: Script
      script: |
        import ssl
        import socket
        from datetime import datetime

        from crossplane.function import request, response

        def operate(req, rsp):
            # Get the Ingress resource
            ingress = request.get_required_resource(req, "ingress")
            if not ingress:
                response.set_output(rsp, {"error": "No ingress resource found"})
                return

            # Extract hostname from Ingress rules
            hostname = ingress["spec"]["rules"][0]["host"]
            port = 443

            # Get SSL certificate info
            context = ssl.create_default_context()
            with socket.create_connection((hostname, port)) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()

            # Parse expiration date
            expiry_date = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
            days_until_expiry = (expiry_date - datetime.now()).days

            # Add warning if certificate expires soon
            if days_until_expiry < 30:
                response.warning(rsp, f"Certificate for {hostname} expires in {days_until_expiry} days")

            # Annotate the Ingress with certificate expiry info
            rsp.desired.resources["ingress"].resource.update({
                "apiVersion": "networking.k8s.io/v1",
                "kind": "Ingress",
                "metadata": {
                    "name": ingress["metadata"]["name"],
                    "namespace": ingress["metadata"]["namespace"],
                    "annotations": {
                        "cert-monitor.crossplane.io/expires": cert['notAfter'],
                        "cert-monitor.crossplane.io/days-until-expiry": str(days_until_expiry),
                        "cert-monitor.crossplane.io/status": "warning" if days_until_expiry < 30 else "ok"
                    }
                }
            })

            # Return results in operation output for monitoring
            response.set_output(rsp, {
                "ingressName": ingress["metadata"]["name"],
                "hostname": hostname,
                "certificateExpires": cert['notAfter'],
                "daysUntilExpiry": days_until_expiry,
                "status": "warning" if days_until_expiry < 30 else "ok"
            })
```


Save the operation as `operation.yaml` and apply it:

```shell
kubectl apply -f operation.yaml
```

### Check the operation

Check that the Operation runs successfully:

```shell {copy-lines="1"}
kubectl get -f operation.yaml
NAME                   SYNCED   SUCCEEDED   AGE
ingress-cert-monitor   True     True        15s
```

{{<hint "tip">}}
Operations show `SUCCEEDED=True` when they complete successfully.
{{</hint>}}

Check the Operation's detailed status:

```shell {copy-lines="1"}
kubectl describe operation ingress-cert-monitor
# ... metadata ...
Status:
  Conditions:
    Last Transition Time:  2024-01-15T10:30:15Z
    Reason:                PipelineSuccess
    Status:                True
    Type:                  Succeeded
    Last Transition Time:  2024-01-15T10:30:15Z
    Reason:                ValidPipeline
    Status:                True
    Type:                  ValidPipeline
  Pipeline:
    Output:
      Certificate Expires:   Sep 29 08:34:02 2025 GMT
      Days Until Expiry:     54
      Hostname:              google.com
      Ingress Name:          example-app
      Status:                ok
    Step:                    check-ingress-certificate
```

{{<hint "tip">}}
The `status.pipeline` field shows the output returned by each function step.
Use this field for tracking what the operation accomplished.
{{</hint>}}

Check that the Operation annotated the Ingress with certificate information:

```shell {copy-lines="1"}
kubectl get ingress example-app -o yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  annotations:
    cert-monitor.crossplane.io/days-until-expiry: "54"
    cert-monitor.crossplane.io/expires: Sep 29 08:34:02 2025 GMT
    cert-monitor.crossplane.io/status: ok
  name: example-app
  namespace: default
spec:
  # ... ingress spec ...
```

{{<hint "tip">}}
This pattern shows how Operations can both read and change existing Kubernetes
resources. The Operation annotated the Ingress with certificate expiry
information that other tools can use for monitoring and alerting.
{{</hint>}}

## Clean up

Delete the resources you created:

```shell
kubectl delete -f operation.yaml
kubectl delete -f ingress.yaml
kubectl delete -f ingress-rbac.yaml
kubectl delete -f function.yaml
```

## Next steps

Operations are powerful building blocks for operational workflows. Learn more
about:

* [**Operation concepts**]({{<ref "../operations/operation">}}) - Core
  Operation features and best practices
* [**CronOperation**]({{<ref "../operations/cronoperation">}}) - Schedule
  operations to run automatically
* [**WatchOperation**]({{<ref "../operations/watchoperation">}}) - Trigger
  operations when resources change

Explore the complete [Operations documentation]({{<ref "../operations">}}) for
advanced features and examples.
