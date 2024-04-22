---
title: Write a Composition Function in Python
state: beta
alphaVersion: "1.11"
betaVersion: "1.14"
weight: 81
description: "Composition functions allow you to template resources using Python"
---

Composition functions (or just functions, for short) are custom programs that
template Crossplane resources. Crossplane calls composition functions to
determine what resources it should create when you create a composite resource
(XR). Read the
[concepts]{{<ref "../concepts/composition-functions" >}}
page to learn more about composition functions.

You can write a function to template resources using a general purpose
programming language. Using a general purpose programming language allows a
function to use advanced logic to template resources, like loops and
conditionals. This guide explains how to write a composition function in
[Python](https://python.org).

{{< hint "important" >}}
It helps to be familiar with
[how composition functions work]{{<ref "../concepts/composition-functions#how-composition-functions-work" >}}
before following this guide.
{{< /hint >}}

## Understand the steps

This guide covers writing a composition function for an
{{<hover label="xr" line="2">}}XBuckets{{</hover>}} composite resource (XR).

```yaml {label="xr"}
apiVersion: example.crossplane.io/v1
kind: XBuckets
metadata:
  name: example-buckets
spec:
  region: us-east-2
  names:
  - crossplane-functions-example-a
  - crossplane-functions-example-b
  - crossplane-functions-example-c
```

<!-- vale gitlab.FutureTense = NO -->
<!--
This section is setting the stage for future sections. It doesn't make sense to
refer to the function in the present tense, because it doesn't exist yet.
-->
An `XBuckets` XR has a region and an array of bucket names. The function will
create an Amazon Web Services (AWS) S3 bucket for each entry in the names array.
<!-- vale gitlab.FutureTense = YES -->

To write a function in Python:

1. [Install the tools you need to write the function](#install-the-tools-you-need-to-write-the-function)
1. [Initialize the function from a template](#initialize-the-function-from-a-template)
1. [Edit the template to add the function's logic](#edit-the-template-to-add-the-functions-logic)
1. [Test the function end-to-end](#test-the-function-end-to-end)
1. [Build and push the function to a package repository](#build-and-push-the-function-to-a-package-registry)

This guide covers each of these steps in detail.

## Install the tools you need to write the function

To write a function in Python you need:

* [Python](https://www.python.org/downloads/) v3.11.
* [Hatch](https://hatch.pypa.io/), a Python build tool. This guide uses v1.7.
* [Docker Engine](https://docs.docker.com/engine/). This guide uses Engine v24.
* The [Crossplane CLI]({{<ref "../cli" >}}) v1.14 or newer. This guide uses Crossplane
  CLI v1.14.

{{<hint "note">}}
You don't need access to a Kubernetes cluster or a Crossplane control plane to
build or test a composition function.
{{</hint>}}

## Initialize the function from a template

Use the `crossplane beta xpkg init` command to initialize a new function. When
you run this command it initializes your function using
[a GitHub repository](https://github.com/crossplane/function-template-python)
as a template.

```shell {copy-lines=1}
crossplane beta xpkg init function-xbuckets https://github.com/crossplane/function-template-python -d function-xbuckets
Initialized package "function-xbuckets" in directory "/home/negz/control/negz/function-xbuckets" from https://github.com/crossplane/function-template-python/tree/bfed6923ab4c8e7adeed70f41138645fc7d38111 (main)
```

The `crossplane beta init xpkg` command creates a directory named
`function-xbuckets`. When you run the command the new directory should look like
this:

```shell {copy-lines=1}
ls function-xbuckets
Dockerfile  example/  function/  LICENSE  package/  pyproject.toml  README.md  renovate.json  tests/
```

Your function's code lives in the `function` directory:

```shell {copy-lines=1}
ls function/
__version__.py  fn.py  main.py
```

The `function/fn.py` file is where you add the function's code. It's useful to
know about some other files in the template:

* `function/main.py` runs the function. You don't need to edit `main.py`.
* `Dockerfile` builds the function runtime. You don't need to edit `Dockerfile`.
* The `package` directory contains metadata used to build the function package.

{{<hint "tip">}}
<!-- vale gitlab.FutureTense = NO -->
<!--
This tip talks about future plans for Crossplane.
-->
In v1.14 of the Crossplane CLI `crossplane beta xpkg init` just clones a
template GitHub repository. A future CLI release will automate tasks like
replacing the template name with the new function's name. See Crossplane issue
[#4941](https://github.com/crossplane/crossplane/issues/4941) for details.
<!-- vale gitlab.FutureTense = YES -->
{{</hint>}}

Edit `package/crossplane.yaml` to change the package's name before you start
adding code. Name your package `function-xbuckets`.

The `package/input` directory defines the OpenAPI schema for the a function's
input. The function in this guide doesn't accept an input. Delete the
`package/input` directory.   

The [composition functions]{{<ref "../concepts/composition-functions" >}}
documentation explains composition function inputs.

{{<hint "tip">}}
If you're writing a function that uses an input, edit the input YAML file to
meet your function's requirements.

Change the input's kind and API group. Don't use `Input` and
`template.fn.crossplane.io`. Instead use something meaningful to your function.
{{</hint>}}

## Edit the template to add the function's logic

You add your function's logic to the
{{<hover label="hello-world" line="1">}}RunFunction{{</hover>}}
method in `function/fn.py`. When you first open the file it contains a "hello
world" function.

```python {label="hello-world"}
async def RunFunction(self, req: fnv1beta1.RunFunctionRequest, _: grpc.aio.ServicerContext) -> fnv1beta1.RunFunctionResponse:
    log = self.log.bind(tag=req.meta.tag)
    log.info("Running function")

    rsp = response.to(req)

    example = ""
    if "example" in req.input:
        example = req.input["example"]

    # TODO: Add your function logic here!
    response.normal(rsp, f"I was run with input {example}!")
    log.info("I was run!", input=example)

    return rsp
```

All Python composition functions have a `RunFunction` method. Crossplane passes
everything the function needs to run in a
{{<hover label="hello-world" line="1">}}RunFunctionRequest{{</hover>}} object.

The function tells Crossplane what resources it should compose by returning a
{{<hover label="hello-world" line="15">}}RunFunctionResponse{{</hover>}} object.

Edit the `RunFunction` method to replace it with this code.

```python {hl_lines="7-28"}
async def RunFunction(self, req: fnv1beta1.RunFunctionRequest, _: grpc.aio.ServicerContext) -> fnv1beta1.RunFunctionResponse:
    log = self.log.bind(tag=req.meta.tag)
    log.info("Running function")

    rsp = response.to(req)

    region = req.observed.composite.resource["spec"]["region"]
    names = req.observed.composite.resource["spec"]["names"]

    for name in names:
        rsp.desired.resources[f"xbuckets-{name}"].resource.update(
            {
                "apiVersion": "s3.aws.upbound.io/v1beta1",
                "kind": "Bucket",
                "metadata": {
                    "annotations": {
                        "crossplane.io/external-name": name,
                    },
                },
                "spec": {
                    "forProvider": {
                        "region": region,
                    },
                },
            }
        )

    log.info("Added desired buckets", region=region, count=len(names))

    return rsp
```

Expand the below block to view the full `fn.py`, including imports and
commentary explaining the function's logic.

{{<expand "The full fn.py file" >}}
```python
"""A Crossplane composition function."""

import grpc
from crossplane.function import logging, response
from crossplane.function.proto.v1beta1 import run_function_pb2 as fnv1beta1
from crossplane.function.proto.v1beta1 import run_function_pb2_grpc as grpcv1beta1


class FunctionRunner(grpcv1beta1.FunctionRunnerService):
    """A FunctionRunner handles gRPC RunFunctionRequests."""

    def __init__(self):
        """Create a new FunctionRunner."""
        self.log = logging.get_logger()

    async def RunFunction(
        self, req: fnv1beta1.RunFunctionRequest, _: grpc.aio.ServicerContext
    ) -> fnv1beta1.RunFunctionResponse:
        """Run the function."""
        # Create a logger for this request.
        log = self.log.bind(tag=req.meta.tag)
        log.info("Running function")

        # Create a response to the request. This copies the desired state and
        # pipeline context from the request to the response.
        rsp = response.to(req)

        # Get the region and a list of bucket names from the observed composite
        # resource (XR). Crossplane represents resources using the Struct
        # well-known protobuf type. The Struct Python object can be accessed
        # like a dictionary.
        region = req.observed.composite.resource["spec"]["region"]
        names = req.observed.composite.resource["spec"]["names"]

        # Add a desired S3 bucket for each name.
        for name in names:
            # Crossplane represents desired composed resources using a protobuf
            # map of messages. This works a little like a Python defaultdict.
            # Instead of assigning to a new key in the dict-like map, you access
            # the key and mutate its value as if it did exist.
            #
            # The below code works because accessing the xbuckets-{name} key
            # automatically creates a new, empty fnv1beta1.Resource message. The
            # Resource message has a resource field containing an empty Struct
            # object that can be populated from a dictionary by calling update.
            #
            # https://protobuf.dev/reference/python/python-generated/#map-fields
            rsp.desired.resources[f"xbuckets-{name}"].resource.update(
                {
                    "apiVersion": "s3.aws.upbound.io/v1beta1",
                    "kind": "Bucket",
                    "metadata": {
                        "annotations": {
                            "crossplane.io/external-name": name,
                        },
                    },
                    "spec": {
                        "forProvider": {
                            "region": region,
                        },
                    },
                }
            )

        # Log what the function did. This will only appear in the function's pod
        # logs. A function can use response.normal() and response.warning() to
        # emit Kubernetes events associated with the XR it's operating on.
        log.info("Added desired buckets", region=region, count=len(names))

        return rsp
```
{{</expand>}}

This code:

1. Gets the observed composite resource from the `RunFunctionRequest`.
1. Gets the region and bucket names from the observed composite resource.
1. Adds one desired S3 bucket for each bucket name.
1. Returns the desired S3 buckets in a `RunFunctionResponse`.

Crossplane provides a
[software development kit](https://github.com/crossplane/function-sdk-python)
(SDK) for writing composition functions in Python. This function uses utilities
from the SDK.

{{<hint "tip">}}
Read [the Python Function SDK documentation](https://crossplane.github.io/function-sdk-python).
{{</hint>}}

{{<hint "important">}}
The Python SDK automatically generates the `RunFunctionRequest` and
`RunFunctionResponse` Python objects from a
[Protocol Buffers](https://protobuf.dev) schema. You can see the schema in the
[Buf Schema Registry](https://buf.build/crossplane/crossplane/docs/main:apiextensions.fn.proto.v1beta1).

The fields of the generated Python objects behave similarly to builtin Python
types like dictionaries and lists. Be aware that there are some differences.

Notably, you access the map of observed and desired resources like a dictionary
but you can't add a new desired resource by assigning to a map key. Instead,
access and mutate the map key as if it already exists.

Instead of adding a new resource like this:

```python
resource = {"apiVersion": "example.org/v1", "kind": "Composed", ...}
rsp.desired.resources["new-resource"] = fnv1beta1.Resource(resource=resource)
```

Pretend it already exists and mutate it, like this:

```python
resource = {"apiVersion": "example.org/v1", "kind": "Composed", ...}
rsp.desired.resources["new-resource"].resource.update(resource)
```

Refer to the Protocol Buffers
[Python Generated Code Guide](https://protobuf.dev/reference/python/python-generated/#fields)
for further details.
{{</hint>}}

## Test the function end-to-end

Test your function by adding unit tests, and by using the `crossplane beta
render` command.

When you initialize a function from the
template it adds some unit tests to `tests/test_fn.py`. These tests use the
[`unittest`](https://docs.python.org/3/library/unittest.html) module from the
Python standard library.

To add test cases, update the `cases` list in `test_run_function`. Expand the
below block to view the full `tests/test_fn.py` file for the function.

{{<expand "The full test_fn.py file" >}}
```python
import dataclasses
import unittest

from crossplane.function import logging, resource
from crossplane.function.proto.v1beta1 import run_function_pb2 as fnv1beta1
from google.protobuf import duration_pb2 as durationpb
from google.protobuf import json_format
from google.protobuf import struct_pb2 as structpb

from function import fn


class TestFunctionRunner(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        logging.configure(level=logging.Level.DISABLED)
        self.maxDiff = 2000

    async def test_run_function(self) -> None:
        @dataclasses.dataclass
        class TestCase:
            reason: str
            req: fnv1beta1.RunFunctionRequest
            want: fnv1beta1.RunFunctionResponse

        cases = [
            TestCase(
                reason="The function should compose two S3 buckets.",
                req=fnv1beta1.RunFunctionRequest(
                    observed=fnv1beta1.State(
                        composite=fnv1beta1.Resource(
                            resource=resource.dict_to_struct(
                                {
                                    "apiVersion": "example.crossplane.io/v1alpha1",
                                    "kind": "XBuckets",
                                    "metadata": {"name": "test"},
                                    "spec": {
                                        "region": "us-east-2",
                                        "names": ["test-bucket-a", "test-bucket-b"],
                                    },
                                }
                            )
                        )
                    )
                ),
                want=fnv1beta1.RunFunctionResponse(
                    meta=fnv1beta1.ResponseMeta(ttl=durationpb.Duration(seconds=60)),
                    desired=fnv1beta1.State(
                        resources={
                            "xbuckets-test-bucket-a": fnv1beta1.Resource(
                                resource=resource.dict_to_struct(
                                    {
                                        "apiVersion": "s3.aws.upbound.io/v1beta1",
                                        "kind": "Bucket",
                                        "metadata": {
                                            "annotations": {
                                                "crossplane.io/external-name": "test-bucket-a"
                                            },
                                        },
                                        "spec": {
                                            "forProvider": {"region": "us-east-2"}
                                        },
                                    }
                                )
                            ),
                            "xbuckets-test-bucket-b": fnv1beta1.Resource(
                                resource=resource.dict_to_struct(
                                    {
                                        "apiVersion": "s3.aws.upbound.io/v1beta1",
                                        "kind": "Bucket",
                                        "metadata": {
                                            "annotations": {
                                                "crossplane.io/external-name": "test-bucket-b"
                                            },
                                        },
                                        "spec": {
                                            "forProvider": {"region": "us-east-2"}
                                        },
                                    }
                                )
                            ),
                        },
                    ),
                    context=structpb.Struct(),
                ),
            ),
        ]

        runner = fn.FunctionRunner()

        for case in cases:
            got = await runner.RunFunction(case.req, None)
            self.assertEqual(
                json_format.MessageToDict(got),
                json_format.MessageToDict(case.want),
                "-want, +got",
            )


if __name__ == "__main__":
    unittest.main()
```
{{</expand>}}

Run the unit tests using `hatch run`:

```shell {copy-lines="1"}
hatch run test:unit
.
----------------------------------------------------------------------
Ran 1 test in 0.003s

OK
```

{{<hint "tip">}}
[Hatch](https://hatch.pypa.io/) is a Python build tool. It builds Python
artifacts like wheels. It also manages virtual environments, similar
to `virtualenv` or `venv`. The `hatch run` command creates a virtual environment
and runs a command in that environment.
{{</hint>}}

You can preview the output of a Composition that uses this function using
the Crossplane CLI. You don't need a Crossplane control plane to do this.

Create a directory under `function-xbuckets` named `example` and create
Composite Resource, Composition and Function YAML files.

Expand the following block to see example files.

{{<expand "The xr.yaml, composition.yaml and function.yaml files">}}

You can recreate the output below using by running `crossplane beta render` with
these files.

The `xr.yaml` file contains the composite resource to render:

```yaml
apiVersion: example.crossplane.io/v1
kind: XBuckets
metadata:
  name: example-buckets
spec:
  region: us-east-2
  names:
  - crossplane-functions-example-a
  - crossplane-functions-example-b
  - crossplane-functions-example-c
```

<br />

The `composition.yaml` file contains the Composition to use to render the
composite resource:

```yaml
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
metadata:
  name: create-buckets
spec:
  compositeTypeRef:
    apiVersion: example.crossplane.io/v1
    kind: XBuckets
  mode: Pipeline
  pipeline:
  - step: create-buckets
    functionRef:
      name: function-xbuckets
```

<br />

The `functions.yaml` file contains the Functions the Composition references in
its pipeline steps:

```yaml
apiVersion: pkg.crossplane.io/v1beta1
kind: Function
metadata:
  name: function-xbuckets
  annotations:
    render.crossplane.io/runtime: Development
spec:
  # The CLI ignores this package when using the Development runtime.
  # You can set it to any value.
  package: xpkg.upbound.io/negz/function-xbuckets:v0.1.0
```
{{</expand>}}

The Function in `functions.yaml` uses the
{{<hover label="development" line="6">}}Development{{</hover>}}
runtime. This tells `crossplane beta render` that your function is running
locally. It connects to your locally running function instead of using Docker to
pull and run the function.

```yaml {label="development"}
apiVersion: pkg.crossplane.io/v1beta1
kind: Function
metadata:
  name: function-xbuckets
  annotations:
    render.crossplane.io/runtime: Development
```

Use `hatch run development` to run your function locally.

```shell {label="run"}
hatch run development
```

{{<hint "warning">}}
`hatch run development` runs the function without encryption or authentication.
Only use it during testing and development.
{{</hint>}}

In a separate terminal, run `crossplane beta render`. 

```shell
crossplane beta render xr.yaml composition.yaml functions.yaml
```

This command calls your function. In the terminal where your function is running
you should now see log output:

```shell
hatch run development
2024-01-11T22:12:58.153572Z [info     ] Running function               filename=fn.py lineno=22 tag=
2024-01-11T22:12:58.153792Z [info     ] Added desired buckets          count=3 filename=fn.py lineno=68 region=us-east-2 tag=
```

The `crossplane beta render` command prints the desired resources the function
returns.

```yaml
---
apiVersion: example.crossplane.io/v1
kind: XBuckets
metadata:
  name: example-buckets
---
apiVersion: s3.aws.upbound.io/v1beta1
kind: Bucket
metadata:
  annotations:
    crossplane.io/composition-resource-name: xbuckets-crossplane-functions-example-b
    crossplane.io/external-name: crossplane-functions-example-b
  generateName: example-buckets-
  labels:
    crossplane.io/composite: example-buckets
  ownerReferences:
    # Omitted for brevity
spec:
  forProvider:
    region: us-east-2
---
apiVersion: s3.aws.upbound.io/v1beta1
kind: Bucket
metadata:
  annotations:
    crossplane.io/composition-resource-name: xbuckets-crossplane-functions-example-c
    crossplane.io/external-name: crossplane-functions-example-c
  generateName: example-buckets-
  labels:
    crossplane.io/composite: example-buckets
  ownerReferences:
    # Omitted for brevity
spec:
  forProvider:
    region: us-east-2
---
apiVersion: s3.aws.upbound.io/v1beta1
kind: Bucket
metadata:
  annotations:
    crossplane.io/composition-resource-name: xbuckets-crossplane-functions-example-a
    crossplane.io/external-name: crossplane-functions-example-a
  generateName: example-buckets-
  labels:
    crossplane.io/composite: example-buckets
  ownerReferences:
    # Omitted for brevity
spec:
  forProvider:
    region: us-east-2
```

{{<hint "tip">}}
Read the composition functions documentation to learn more about
[testing composition functions]({{< ref "../concepts/composition-functions#test-a-composition-that-uses-functions" >}}).
{{</hint>}}

## Build and push the function to a package registry

You build a function in two stages. First you build the function's runtime. This
is the Open Container Initiative (OCI) image Crossplane uses to run your
function. You then embed that runtime in a package, and push it to a package
registry. The Crossplane CLI uses `xpkg.upbound.io` as its default package
registry.

A function supports a single platform, like `linux/amd64`, by default. You can
support multiple platforms by building a runtime and package for each platform,
then pushing all the packages to a single tag in the registry.

Pushing your function to a registry allows you to use your function in a
Crossplane control plane. See the
[composition functions documentation]{{<ref "../concepts/composition-functions" >}}.
to learn how to use a function in a control plane.

Use Docker to build a runtime for each platform.

```shell {copy-lines="1"}
docker build . --quiet --platform=linux/amd64 --tag runtime-amd64
sha256:fdf40374cc6f0b46191499fbc1dbbb05ddb76aca854f69f2912e580cfe624b4b
```

```shell {copy-lines="1"}
docker build . --quiet --platform=linux/arm64 --tag runtime-arm64
sha256:cb015ceabf46d2a55ccaeebb11db5659a2fb5e93de36713364efcf6d699069af
```

{{<hint "tip">}}
You can use whatever tag you want. There's no need to push the runtime images to
a registry. The tag is only used to tell `crossplane xpkg build` what runtime to
embed.
{{</hint>}}

{{<hint "important">}}
Docker uses emulation to create images for different platforms. If building an
image for a different platform fails, make sure you have installed `binfmt`. See
the
[Docker documentation](https://docs.docker.com/build/building/multi-platform/#qemu)
for instructions.
{{</hint>}}

Use the Crossplane CLI to build a package for each platform. Each package embeds
a runtime image. 

The {{<hover label="build" line="2">}}--package-root{{</hover>}} flag specifies
the `package` directory, which contains `crossplane.yaml`. This includes
metadata about the package.

The {{<hover label="build" line="3">}}--embed-runtime-image{{</hover>}} flag
specifies the runtime image tag built using Docker.

The {{<hover label="build" line="4">}}--package-file{{</hover>}} flag specifies
specifies where to write the package file to disk. Crossplane package files use
the extension `.xpkg`.

```shell {label="build"}
crossplane xpkg build \
    --package-root=package \
    --embed-runtime-image=runtime-amd64 \
    --package-file=function-amd64.xpkg
```

```shell
crossplane xpkg build \
    --package-root=package \
    --embed-runtime-image=runtime-arm64 \
    --package-file=function-arm64.xpkg
```

{{<hint "tip">}}
Crossplane packages are special OCI images. Read more about packages in the
[packages documentation]({{< ref "../concepts/packages" >}}).
{{</hint>}}

Push both package files to a registry. Pushing both files to one tag in the
registry creates a
[multi-platform](https://docs.docker.com/build/building/multi-platform/)
package that runs on both `linux/arm64` and `linux/amd64` hosts.

```shell
crossplane xpkg push \
  --package-files=function-amd64.xpkg,function-arm64.xpkg \
  negz/function-xbuckets:v0.1.0
```

{{<hint "tip">}}
If you push the function to a GitHub repository the template automatically sets
up continuous integration (CI) using
[GitHub Actions](https://github.com/features/actions). The CI workflow will
lint, test, and build your function. You can see how the template configures CI
by reading `.github/workflows/ci.yaml`.

The CI workflow can automatically push packages to `xpkg.upbound.io`. For this
to work you must create a repository at https://marketplace.upbound.io. Give the
CI workflow access to push to the Marketplace by creating an API token and
[adding it to your repository](https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions#creating-secrets-for-a-repository).
Save your API token access ID as a secret named `XPKG_ACCESS_ID` and your API
token as a secret named `XPKG_TOKEN`.
{{</hint>}}
