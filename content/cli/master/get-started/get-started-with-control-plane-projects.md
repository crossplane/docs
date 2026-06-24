---
title: Get Started with Control Plane Projects
weight: 100
description: "Build a control plane project with the Crossplane CLI"
---

This guide shows how to use the Crossplane CLI to build a platform API from
scratch. You create a _project_, define a new `WebApp` custom resource, and
configure how Crossplane composes it. When a user creates a `WebApp`, Crossplane
creates a Kubernetes `Deployment` and a `Service`.

The Crossplane CLI scaffolds the project, generates the API and composition, and
runs the project on a local development control plane so you can test it without
deploying to a shared cluster.

{{<hint "tip">}}
This guide shows how to write the composition function in Go, Python, KCL, and
templated YAML. You can pick your preferred language.
{{</hint>}}

A `WebApp` custom resource looks like this:

```yaml {copy-lines="none"}
apiVersion: platform.example.com/v1alpha1
kind: WebApp
metadata:
  name: podinfo
  namespace: default
spec:
  image: docker.io/stefanprodan/podinfo:6.11.0
  replicas: 3
  ports: [9898]
```

**The `WebApp` is the custom API your users use to deploy a containerized
workload.**

When a user creates a `WebApp`, Crossplane creates a `Deployment` and a
`Service`:

```yaml {copy-lines="none"}
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: podinfo
  namespace: default
  labels:
    app.kubernetes.io/name: podinfo  # Copied from the WebApp's name
spec:
  replicas: 3  # Copied from the WebApp's spec
  selector:
    matchLabels:
      app.kubernetes.io/name: podinfo
  template:
    metadata:
      labels:
        app.kubernetes.io/name: podinfo
    spec:
      containers:
      - name: podinfo
        image: docker.io/stefanprodan/podinfo:6.11.0  # Copied from the WebApp's spec
        ports:
        - containerPort: 9898  # Copied from the WebApp's spec
---
apiVersion: v1
kind: Service
metadata:
  name: podinfo
  namespace: default
spec:
  selector:
    app.kubernetes.io/name: podinfo
  ports:
  - protocol: TCP
    port: 9898
    targetPort: 9898
```

## Prerequisites

This guide requires:

* The [Crossplane CLI]({{<ref "../_index.md">}}) installed
* A Docker compatible container runtime

The CLI builds the project's functions and runs a local development control
plane in a [KIND](https://kind.sigs.k8s.io) cluster. Both require a working
Docker installation. You don't need an existing Kubernetes cluster.

## Create the project

A Crossplane _project_ is a directory that contains everything that makes up a
platform API: the API definitions, compositions, embedded functions, examples,
and a `crossplane-project.yaml` metadata file.

Initialize a new project named `example-project-webapp`:

```shell
crossplane project init example-project-webapp
```

The `init` command creates a directory named after the project, containing a
minimal `crossplane-project.yaml` and the standard project directories:

```shell {copy-lines="1"}
tree example-project-webapp
example-project-webapp
├── apis
├── crossplane-project.yaml
├── examples
├── functions
├── operations
└── tests

6 directories, 1 file
```

Change into the new project directory:

```shell
cd example-project-webapp
```

Run the remaining commands in this guide from the project directory.

## The `crossplane-project.yaml` file

The `crossplane-project.yaml` file contains metadata about your project. This
metadata influences how the Crossplane CLI builds your project into
[Crossplane packages]({{<ref "/latest/packages">}}). For now, the file sets only
the project's name and OCI repository:

```yaml {copy-lines="none"}
apiVersion: dev.crossplane.io/v1alpha1
kind: Project
metadata:
  name: example-project-webapp
spec:
  repository: example.com/my-org/example-project-webapp
```

For the rest of this guide, you can leave the placeholder `repository` as
is. You must update it if you want to push your project to an OCI registry
later.

## Define the API

Crossplane calls a custom resource that's powered by composition a _composite
resource_, or XR. You define the schema of an XR with a _composite resource
definition_, or XRD.

{{<hint "note">}}
Kubernetes calls user-defined API resources _custom resources_.

Crossplane calls user-defined API resources that use composition _composite
resources_.

A composite resource is a kind of custom resource.
{{</hint>}}

Rather than write the XRD by hand, you can write an example XR or describe the
API with [SimpleSchema](https://kro.run/api/specifications/simple-schema/), then
let the CLI generate the XRD.

{{< tabs >}}

{{< tab "Example XR" >}}

Create an example XR at `examples/webapps/podinfo.yaml` showing all the fields
the `WebApp` API should include:

```yaml
apiVersion: platform.example.com/v1alpha1
kind: WebApp
metadata:
  name: podinfo
  namespace: default
spec:
  image: docker.io/stefanprodan/podinfo:6.11.0
  replicas: 3
  ports: [9898]
```

The `crossplane xrd generate` command reads the example XR, infers the field
types from their contents, and generates an appropriate XRD:

```shell
crossplane xrd generate examples/webapps/podinfo.yaml --from xr
```

The command writes the generated XRD to `apis/webapps/definition.yaml`:

```yaml {copy-lines="none"}
apiVersion: apiextensions.crossplane.io/v2
kind: CompositeResourceDefinition
metadata:
  name: webapps.platform.example.com
spec:
  group: platform.example.com
  names:
    categories:
    - crossplane
    kind: WebApp
    plural: webapps
  scope: Namespaced
  versions:
  - name: v1alpha1
    referenceable: true
    schema:
      openAPIV3Schema:
        description: WebApp is the Schema for the WebApp API.
        properties:
          spec:
            description: WebAppSpec defines the desired state of WebApp.
            properties:
              image:
                type: string
              ports:
                items:
                  type: number
                type: array
              replicas:
                type: number
            type: object
          status:
            description: WebAppStatus defines the observed state of WebApp.
            type: object
        required:
        - spec
        type: object
    served: true
```

{{<hint "note">}}
Generating an XRD from an example XR doesn't let you specify field types,
defaults, validation rules, or field descriptions. SimpleSchema provides a more
powerful, but more complex, way to describe your API.
{{</hint>}}

{{< /tab >}}

{{< tab "SimpleSchema" >}}
Create a SimpleSchema document at `apis/webapps/schema.yaml` that describes the
`WebApp` API:

```yaml
apiVersion: platform.example.com/v1alpha1
kind: WebApp
spec:
  image: string | required=true description="OCI image for the webapp"
  replicas: integer | default=1 minimum=1 maximum=100 description="Number of replicas to run"
  ports: "[]integer | default=[80] description=\"Ports to expose from the application container\""
```

The SimpleSchema document lists each field of the API's `spec` along with its
type, validation rules, and description.

Generate the XRD from the SimpleSchema document:

```shell
crossplane xrd generate apis/webapps/schema.yaml --from simpleschema
```

The command writes the generated XRD to `apis/webapps/definition.yaml`:

```yaml {copy-lines="none"}
apiVersion: apiextensions.crossplane.io/v2
kind: CompositeResourceDefinition
metadata:
  name: webapps.platform.example.com
spec:
  group: platform.example.com
  names:
    categories:
    - crossplane
    kind: WebApp
    plural: webapps
  scope: Namespaced
  versions:
  - name: v1alpha1
    referenceable: true
    schema:
      openAPIV3Schema:
        description: WebApp is the Schema for the WebApp API.
        properties:
          spec:
            properties:
              image:
                description: OCI image for the webapp
                type: string
              ports:
                default:
                - 80
                description: Ports to expose from the application container
                items:
                  type: integer
                type: array
              replicas:
                default: 1
                description: Number of replicas to run
                maximum: 100
                minimum: 1
                type: integer
            required:
            - image
            type: object
          status:
            type: object
        required:
        - spec
        type: object
    served: true
```

{{< /tab >}}
{{< /tabs >}}

The XRD is the contract between your users and your platform. It defines the
fields a user can set on a `WebApp`, the validation Crossplane applies, and the
default values Crossplane fills in.

## Generate the composition

A _composition_ tells Crossplane what to do when a user creates or updates a
`WebApp`. It contains a pipeline of functions that build the resources
Crossplane creates.

Generate a composition from the XRD:

```shell
crossplane composition generate apis/webapps/definition.yaml
```

The command writes the composition to `apis/webapps/composition.yaml`:

```yaml {copy-lines="none"}
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
metadata:
  name: webapps.platform.example.com
spec:
  compositeTypeRef:
    apiVersion: platform.example.com/v1alpha1
    kind: WebApp
  mode: Pipeline
  pipeline:
  - functionRef:
      name: crossplane-contrib-function-auto-ready
    step: crossplane-contrib-function-auto-ready
```

<!-- vale Microsoft.Auto = NO -->
The generated composition contains a single pipeline step that runs
[function-auto-ready](https://github.com/crossplane-contrib/function-auto-ready),
which marks the `WebApp` ready when its composed resources are ready. The
`composition generate` command adds `function-auto-ready` to the project's
dependencies automatically.
<!-- vale Microsoft.Auto = YES -->

The composition doesn't yet create any resources. In the next step you write a
function that turns a `WebApp` into a `Deployment` and a `Service`.

## Add dependencies

Your function creates Kubernetes `Deployment` and `Service` resources, so it
needs the schemas for the Kubernetes core APIs. Add the Kubernetes APIs as a
project dependency:

```shell
crossplane dependency add k8s:v1.35.0
```

The `dependency add` command generates language bindings (schemas) for the
dependency and records it in `crossplane-project.yaml`. The function uses these
schemas for typed access to the `Deployment` and `Service` resources.

{{<hint "note">}}
You don't need to add `function-auto-ready` as a dependency. The
`composition generate` command added it for you in the previous step.
{{</hint>}}

After this step, your project has two dependencies listed in
`crossplane-project.yaml`:

```yaml {copy-lines="none"}
apiVersion: dev.crossplane.io/v1alpha1
kind: Project
metadata:
  name: example-project-webapp
spec:
  dependencies:
  - type: xpkg
    xpkg:
      apiVersion: pkg.crossplane.io/v1
      kind: Function
      package: xpkg.crossplane.io/crossplane-contrib/function-auto-ready
      version: '>=v0.0.0'
  - k8s:
      version: v1.35.0
    type: k8s
  repository: example.com/my-org/example-project-webapp
```

## Write the function

A composition function contains the logic that turns a `WebApp` into the
resources Crossplane creates. The CLI scaffolds an embedded function in the
language you choose and adds it as a step in your composition's pipeline.

Pick a language to write your function in.

{{< tabs >}}

{{< tab "Templated YAML" >}}
Templated YAML is a good choice if you're used to writing
[Helm charts](https://helm.sh). It doesn't require a separate toolchain.

Generate a templated YAML function named `compose-webapp` and add it to the
composition's pipeline:

```shell
crossplane function generate compose-webapp apis/webapps/composition.yaml --language go-templating
```

The command scaffolds the function under `functions/compose-webapp/`, where you
write one or more `.gotmpl` template files. Templates render in alphabetical
order by filename.

The function scaffold includes the file
`functions/compose-webapp/00-prelude.yaml.gotmpl`, which reads the observed XR
into a variable:

```yaml {copy-lines="none"}
# Get the observed composite resource into a variable. This can be used in any
# subsequent templates.
{{ $xr := getCompositeResource . }}
```

You can use the `$xr` variable to access fields from the XR in later templates.

Replace the example contents of
`functions/compose-webapp/01-compose.yaml.gotmpl` with the following:

```yaml
# code: language=yaml
# yaml-language-server: $schema=../../schemas/json/index.schema.json

---
apiVersion: apps/v1
kind: Deployment
metadata:
  annotations:
    gotemplating.fn.crossplane.io/composition-resource-name: deployment
  name: {{ $xr.metadata.name }}
  namespace: {{ $xr.metadata.namespace }}
  labels:
    app.kubernetes.io/name: {{ $xr.metadata.name }}
spec:
  replicas: {{ $xr.spec.replicas }}
  selector:
    matchLabels:
      app.kubernetes.io/name: {{ $xr.metadata.name }}
  template:
    metadata:
      labels:
        app.kubernetes.io/name: {{ $xr.metadata.name }}
    spec:
      containers:
      - name: {{ $xr.metadata.name }}
        image: {{ $xr.spec.image }}
        ports:
#{{- range $p := $xr.spec.ports }}
        - containerPort: {{ $p }}
#{{- end }}

---
apiVersion: v1
kind: Service
metadata:
  annotations:
    gotemplating.fn.crossplane.io/composition-resource-name: service
  name: {{ $xr.metadata.name }}
  namespace: {{ $xr.metadata.namespace }}
  labels:
    app.kubernetes.io/name: {{ $xr.metadata.name }}
spec:
  selector:
    app.kubernetes.io/name: {{ $xr.metadata.name }}
  ports:
#{{- range $p := $xr.spec.ports }}
  - protocol: TCP
    port: {{ $p }}
    targetPort: {{ $p }}
#{{- end }}
```

The comment lines at the top configure the
[YAML language server](https://github.com/redhat-developer/yaml-language-server)
to use the JSON Schema files the CLI generated when you added the Kubernetes
dependency. This lets you use editor features like hover documentation and
autocompletion when writing your templates. Note that the template control flow
can confuse the YAML language server. Making them YAML comments causes the
language server to ignore them, but they're still invoked by the template
engine.

The `composition-resource-name` annotation gives each resource a stable name in
the composition.

{{<hint "tip">}}
Templated YAML functions use
[function-go-templating](https://github.com/crossplane-contrib/function-go-templating)
as their runtime image. You can use any of the features and functions described
in its documentation.
{{</hint>}}

{{< /tab >}}

{{< tab "Python" >}}
Python is a good choice for functions with dynamic logic. You can use the full
[Python standard library](https://docs.python.org/3/library/index.html) and any
other Python library you need.

Generate a Python function named `compose-webapp` and add it to the
composition's pipeline:

```shell
crossplane function generate compose-webapp apis/webapps/composition.yaml --language python
```

The command scaffolds the function under `functions/compose-webapp/` and adds a
pipeline step to `apis/webapps/composition.yaml`.

Replace the contents of `functions/compose-webapp/function/fn.py` with the
following function logic:

```python
"""A Crossplane composition function."""

import grpc
from crossplane.function import logging, response, resource
from crossplane.function.proto.v1 import run_function_pb2 as fnv1
from crossplane.function.proto.v1 import run_function_pb2_grpc as grpcv1

from models.com.example.platform.webapp import v1alpha1
from models.io.k8s.api.apps import v1 as appsv1
from models.io.k8s.api.core import v1 as corev1
from models.io.k8s.apimachinery.pkg.apis.core.meta import v1 as metav1
from models.io.k8s.apimachinery.pkg.util import intstr

class FunctionRunner(grpcv1.FunctionRunnerService):
    """A FunctionRunner handles gRPC RunFunctionRequests."""

    def __init__(self):
        """Create a new FunctionRunner."""
        self.log = logging.get_logger()

    async def RunFunction(
        self, req: fnv1.RunFunctionRequest, _: grpc.aio.ServicerContext
    ) -> fnv1.RunFunctionResponse:
        """Run the function."""
        log = self.log.bind(tag=req.meta.tag)
        log.info("Running function")

        rsp = response.to(req)

        xr = v1alpha1.WebApp(**resource.struct_to_dict(req.observed.composite.resource))

        assert xr.metadata is not None
        assert xr.metadata.name is not None
        assert xr.spec.ports is not None

        labels = {"app.kubernetes.io/name": xr.metadata.name}
        ports = xr.spec.ports

        dply = appsv1.Deployment(
            metadata=metav1.ObjectMeta(
                labels=labels,
            ),
            spec=appsv1.DeploymentSpec(
                selector=metav1.LabelSelector(
                    matchLabels=labels,
                ),
                replicas=xr.spec.replicas,
                template=corev1.PodTemplateSpec(
                    metadata=metav1.ObjectMeta(
                        labels=labels,
                    ),
                    spec=corev1.PodSpec(
                        containers=[
                            corev1.Container(
                                name="app",
                                image=xr.spec.image,
                                ports=[corev1.ContainerPort(containerPort=p) for p in ports],
                            )
                        ]
                    ),
                ),
            ),
        )

        resource.update(rsp.desired.resources["deployment"], dply)

        svc = corev1.Service(
            metadata=metav1.ObjectMeta(
                labels=labels,
            ),
            spec=corev1.ServiceSpec(
                ports=[corev1.ServicePort(port=p, targetPort=intstr.IntOrString(p)) for p in ports],
                selector=labels,
            ),
        )

        resource.update(rsp.desired.resources["service"], svc)

        return rsp
```

The function reads the observed `WebApp` XR, then builds a `Deployment` and a
`Service` from its `spec`. The `models` packages are the type bindings the CLI
generated when you added the Kubernetes dependency, so you build the resources
with typed Python classes instead of raw dictionaries.
{{< /tab >}}

{{< tab "Go" >}}
Go is a good choice if you want a statically typed, compiled function and access
to the full Go ecosystem.

Generate a Go function named `compose-webapp` and add it to the composition's
pipeline:

```shell
crossplane function generate compose-webapp apis/webapps/composition.yaml --language go
```

The command scaffolds the function under `functions/compose-webapp/` and adds a
pipeline step to `apis/webapps/composition.yaml`.

Replace the contents of `functions/compose-webapp/fn.go` with the following
function logic:

```go
package main

import (
	"context"
	"encoding/json"

	"dev.crossplane.io/models/com/example/platform/v1alpha1"
	appsv1 "dev.crossplane.io/models/io/k8s/apps/v1"
	metav1 "dev.crossplane.io/models/io/k8s/core/meta/v1"
	corev1 "dev.crossplane.io/models/io/k8s/core/v1"
	utilv1 "dev.crossplane.io/models/io/k8s/util/v1"
	"github.com/crossplane/crossplane-runtime/v2/pkg/errors"
	"github.com/crossplane/function-sdk-go/logging"
	fnv1 "github.com/crossplane/function-sdk-go/proto/v1"
	"github.com/crossplane/function-sdk-go/request"
	"github.com/crossplane/function-sdk-go/resource"
	"github.com/crossplane/function-sdk-go/resource/composed"
	"github.com/crossplane/function-sdk-go/response"
	"k8s.io/utils/ptr"
)

// Function is your composition function.
type Function struct {
	fnv1.UnimplementedFunctionRunnerServiceServer

	log logging.Logger
}

// RunFunction runs the Function.
func (f *Function) RunFunction(_ context.Context, req *fnv1.RunFunctionRequest) (*fnv1.RunFunctionResponse, error) {
	f.log.Info("Running function", "tag", req.GetMeta().GetTag())
	rsp := response.To(req, response.DefaultTTL)

	observedComposite, err := request.GetObservedCompositeResource(req)
	if err != nil {
		response.Fatal(rsp, errors.Wrap(err, "cannot get xr"))
		return rsp, nil
	}

	var xr v1alpha1.WebApp
	if err := convertViaJSON(&xr, observedComposite.Resource); err != nil {
		response.Fatal(rsp, errors.Wrap(err, "cannot convert xr"))
		return rsp, nil
	}

	// Collect the desired composed resources into this map, then convert them to
	// the SDK's types and set them in the response on return.
	desiredComposed := make(map[resource.Name]any)
	defer func() {
		desiredComposedResources, err := request.GetDesiredComposedResources(req)
		if err != nil {
			response.Fatal(rsp, errors.Wrap(err, "cannot get desired resources"))
			return
		}

		for name, obj := range desiredComposed {
			c := composed.New()
			if err := convertViaJSON(c, obj); err != nil {
				response.Fatal(rsp, errors.Wrapf(err, "cannot convert %s to unstructured", name))
				return
			}
			desiredComposedResources[name] = &resource.DesiredComposed{Resource: c}
		}

		if err := response.SetDesiredComposedResources(rsp, desiredComposedResources); err != nil {
			response.Fatal(rsp, errors.Wrap(err, "cannot set desired resources"))
			return
		}
	}()

	var (
		cports []corev1.ContainerPort
		sports []corev1.ServicePort
	)
	if xr.Spec.Ports != nil {
		cports = make([]corev1.ContainerPort, len(*xr.Spec.Ports))
		sports = make([]corev1.ServicePort, len(*xr.Spec.Ports))

		for i, p := range *xr.Spec.Ports {
			cports[i] = corev1.ContainerPort{
				ContainerPort: ptr.To(int32(p)),
			}
			sports[i] = corev1.ServicePort{
				Port:       ptr.To(int32(p)),
				TargetPort: new(utilv1.IntOrString),
			}
			_ = sports[i].TargetPort.FromInt(int(p))
		}
	}

	labels := map[string]string{"app.kubernetes.io/name": *xr.Metadata.Name}

	deployment := &appsv1.Deployment{
		APIVersion: ptr.To(appsv1.DeploymentAPIVersionAppsV1),
		Kind:       ptr.To(appsv1.DeploymentKindDeployment),
		Metadata: &metav1.ObjectMeta{
			Name:      xr.Metadata.Name,
			Namespace: xr.Metadata.Namespace,
			Labels:    &labels,
		},
		Spec: &appsv1.DeploymentSpec{
			Replicas: ptr.To(int32(*xr.Spec.Replicas)),
			Selector: &metav1.LabelSelector{
				MatchLabels: &labels,
			},
			Template: &corev1.PodTemplateSpec{
				Metadata: &metav1.ObjectMeta{
					Labels: &labels,
				},
				Spec: &corev1.PodSpec{
					Containers: &[]corev1.Container{{
						Name:  xr.Metadata.Name,
						Image: xr.Spec.Image,
						Ports: &cports,
					}},
				},
			},
		},
	}

	desiredComposed["deployment"] = deployment

	service := &corev1.Service{
		APIVersion: ptr.To(corev1.ServiceAPIVersionV1),
		Kind:       ptr.To(corev1.ServiceKindService),
		Metadata: &metav1.ObjectMeta{
			Name:      xr.Metadata.Name,
			Namespace: xr.Metadata.Namespace,
			Labels:    &labels,
		},
		Spec: &corev1.ServiceSpec{
			Selector: &labels,
			Ports:    &sports,
		},
	}

	desiredComposed["service"] = service

	return rsp, nil
}

func convertViaJSON(to, from any) error {
	bs, err := json.Marshal(from)
	if err != nil {
		return err
	}
	return json.Unmarshal(bs, to)
}
```

The function reads the observed `WebApp` XR, then builds a `Deployment` and a
`Service` from its `spec`. The `dev.crossplane.io/models` packages are the
bindings the CLI generated when you added the Kubernetes dependency, so the
compiler checks the resources you create.
{{< /tab >}}

{{< tab "KCL" >}}
[KCL](https://kcl-lang.io) is a good choice for functions with dynamic logic.
It's fast and sandboxed.

Generate a KCL function named `compose-webapp` and add it to the composition's
pipeline:

```shell
crossplane function generate compose-webapp apis/webapps/composition.yaml --language kcl
```

The command scaffolds the function under `functions/compose-webapp/` and adds a
pipeline step to `apis/webapps/composition.yaml`.

Replace the contents of `functions/compose-webapp/main.k` with the following
function logic:

```python
import models.io.k8s.api.core.v1 as corev1
import models.com.example.platform.v1alpha1 as platformv1alpha1
import models.io.k8s.api.apps.v1 as appsv1
import models.io.k8s.apimachinery.pkg.apis.meta.v1 as metav1

oxr = option("params").oxr # observed composite resource
dcds = option("params").dcds # desired composed resources

_xr = platformv1alpha1.WebApp{**oxr}
_replicas = int(_xr.spec.replicas)
_ports = [int(p) for p in _xr.spec.ports]

_labels = {"app.kubernetes.io/name": _xr.metadata.name}
_metadata = lambda name: str -> any {
    {
        annotations = { "krm.kcl.dev/composition-resource-name" = name }
        labels = _labels
    }
}

_items = [
    appsv1.Deployment{
        metadata: _metadata("deployment")
        spec: appsv1.DeploymentSpec{
            replicas: _replicas
            selector: metav1.LabelSelector{
                matchLabels: _labels
            }
            template: corev1.PodTemplateSpec{
                metadata: metav1.ObjectMeta{
                    labels: _labels
                }
                spec: corev1.PodSpec{
                    containers: [
                        corev1.Container{
                            name: _xr.metadata.name
                            image: _xr.spec.image
                            ports: [corev1.ContainerPort{containerPort: p} for p in _ports]
                        }
                    ]
                }
            }
        }
    },
    corev1.Service{
        metadata: _metadata("service")
        spec: corev1.ServiceSpec{
            selector: _labels
            ports: [corev1.ServicePort{
                protocol: "TCP"
                port: p
                targetPort: p
            } for p in _ports]
        }
    }
]
items = _items
```

The function reads the observed `WebApp` XR through `option("params").oxr`, then
builds a `Deployment` and a `Service` from its `spec`. The `models` packages are
the type bindings the CLI generated when you added the Kubernetes dependency.
{{< /tab >}}

{{</ tabs >}}

The composition now has two pipeline steps: your `compose-webapp` function, which
creates the `Deployment` and `Service`, followed by `function-auto-ready`:

```yaml {copy-lines="none"}
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
metadata:
  name: webapps.platform.example.com
spec:
  compositeTypeRef:
    apiVersion: platform.example.com/v1alpha1
    kind: WebApp
  mode: Pipeline
  pipeline:
  - functionRef:
      name: example-project-webappcompose-webapp
    step: compose-webapp
  - functionRef:
      name: crossplane-contrib-function-auto-ready
    step: crossplane-contrib-function-auto-ready
```

## Add an example

If you generated your XRD from SimpleSchema, create an example `WebApp` so you
can render and run the project against a realistic input. If you generated your
XRD from an example XR, you already have the example and can skip this step.

Create `examples/webapps/podinfo.yaml`:

```yaml
apiVersion: platform.example.com/v1alpha1
kind: WebApp
metadata:
  name: podinfo
  namespace: default
spec:
  image: docker.io/stefanprodan/podinfo:6.11.0
  replicas: 3
  ports: [9898]
```

## Render the composition

Before running the project, use `crossplane composition render` to preview what
your composition produces. The `render` command runs your composition pipeline
locally and prints the resources the composition would create.

In a project directory, `render` discovers and builds the composition's
functions automatically, so you only pass the example XR and the composition:

```shell
crossplane composition render examples/webapps/podinfo.yaml apis/webapps/composition.yaml
```

The command prints the rendered `Deployment` and `Service` as well as the
updates Crossplane would make to the `WebApp` XR:

```yaml {copy-lines="none"}
---
apiVersion: platform.example.com/v1alpha1
kind: WebApp
metadata:
  name: podinfo
  namespace: default
spec:
  crossplane:
    resourceRefs:
    - apiVersion: apps/v1
      kind: Deployment
      name: podinfo
    - apiVersion: v1
      kind: Service
      name: podinfo
status:
  conditions:
  - lastTransitionTime: "2024-01-01T00:00:00Z"
    reason: WatchCircuitClosed
    status: "True"
    type: Responsive
  - lastTransitionTime: "2024-01-01T00:00:00Z"
    reason: ReconcileSuccess
    status: "True"
    type: Synced
  - lastTransitionTime: "2024-01-01T00:00:00Z"
    message: 'Unready resources: deployment, service'
    reason: Creating
    status: "False"
    type: Ready
---
apiVersion: apps/v1
kind: Deployment
metadata:
  annotations:
    crossplane.io/composition-resource-name: deployment
  labels:
    app.kubernetes.io/name: podinfo
    crossplane.io/composite: podinfo
  name: podinfo
  namespace: default
  ownerReferences:
  - apiVersion: platform.example.com/v1alpha1
    blockOwnerDeletion: true
    controller: true
    kind: WebApp
    name: podinfo
    uid: 88356664-76da-5ea5-a715-b1bde80fe0a5
spec:
  replicas: 3
  selector:
    matchLabels:
      app.kubernetes.io/name: podinfo
  template:
    metadata:
      labels:
        app.kubernetes.io/name: podinfo
    spec:
      containers:
      - image: docker.io/stefanprodan/podinfo:6.11.0
        name: podinfo
        ports:
        - containerPort: 9898
---
apiVersion: v1
kind: Service
metadata:
  annotations:
    crossplane.io/composition-resource-name: service
  labels:
    crossplane.io/composite: podinfo
  name: podinfo
  namespace: default
  ownerReferences:
  - apiVersion: platform.example.com/v1alpha1
    blockOwnerDeletion: true
    controller: true
    kind: WebApp
    name: podinfo
    uid: 88356664-76da-5ea5-a715-b1bde80fe0a5
spec:
  ports:
  - port: 9898
    protocol: TCP
    targetPort: 9898
  selector:
    app.kubernetes.io/name: podinfo
```

`render` runs the same composition logic as a real Crossplane control plane, so
you can iterate on your function without deploying anything.

## Run the project

When you're happy with the rendered output, run the project on a local
development control plane:

```shell
crossplane project run
```

The `run` command:

* creates a local development control plane in a KIND cluster and a local OCI
  registry
* builds your embedded function into a `Function` xpkg
* builds a `Configuration` xpkg containing your project's XRD and Composition,
  with a dependency on your embedded function and `function-auto-ready`
* pushes your project's packages to the local OCI registry
* installs the `Configuration` package on the control plane
* points your `kubectl` context at the development control plane

The first run takes some time while the CLI creates the cluster and installs
Crossplane. Later runs reuse the cluster and are faster.

After `run` completes, your `kubectl` context points at the development control
plane. Create the example `WebApp`:

```shell
kubectl apply -f examples/webapps/podinfo.yaml
```

Check that the `WebApp` is ready:

```shell {copy-lines="1"}
kubectl get webapp podinfo
NAME      SYNCED   READY   COMPOSITION                    AGE
podinfo   True     True    webapps.platform.example.com   45s
```

Check that Crossplane created the `Deployment` and `Service`:

```shell {copy-lines="1"}
kubectl get deployment,service -l app.kubernetes.io/name=podinfo
NAME                      READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/podinfo   3/3     3            3           45s

NAME              TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)    AGE
service/podinfo   ClusterIP   10.96.142.110   <none>        9898/TCP   45s
```

Crossplane created a `Deployment` with three replicas and a `Service`, just as
your function defined.

{{<hint "tip">}}
Edit the `WebApp`'s `replicas` or `image` and apply it again. Crossplane updates
the `Deployment` to match.
{{</hint>}}

When you're done, delete the `WebApp`:

```shell
kubectl delete -f examples/webapps/podinfo.yaml
```

Crossplane deletes the `Deployment` and `Service` along with the `WebApp`.

Tear down the development control plane:

```shell
crossplane project stop
```

## Next steps

You built a complete platform API with the Crossplane CLI: an API, a
composition, and a function, all running on a local control plane.

To install your API on an existing Crossplane cluster, use
[`crossplane project build`]({{<ref "../command-reference/#crossplane-project-build">}})
and
[`crossplane project push`]({{<ref "../command-reference/#crossplane-project-push">}})
to package it and push it to an OCI registry. Remember to update the OCI
repository in `crossplane-project` before running `build` and `push`.

After pushing your project to an OCI registry, you can install it using
[`crossplane xpkg install configuration`]({{<ref "../command-reference/#crossplane-xpkg-install">}}).

{{<hint "tip">}}

When you install the `Configuration` package built by `crossplane project
build`, the Crossplane package manager automatically installs your project's
dependencies and embedded functions, which are dependencies of the
`Configuration`. To ensure updates work as expected when you make changes to
your functions in the future, configure your Crossplane cluster to
[automatically update dependency versions]({{<ref "/latest/packages/configurations/#automatically-update-dependency-versions">}}).
{{</hint>}}

To extend the `WebApp`, add more fields to the SimpleSchema document or example
and regenerate the XRD, then update your function to use them. You can also add
more dependencies with
[`crossplane dependency add`]({{<ref "../command-reference/#crossplane-dependency-add">}})
to compose managed resources from cloud providers alongside the `Deployment` and
`Service`.

See the [CLI command reference]({{<ref "../command-reference">}}) for the
full set of commands.
