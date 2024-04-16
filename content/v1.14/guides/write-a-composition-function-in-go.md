---
title: Write a Composition Function in Go
state: beta
alphaVersion: "1.11"
betaVersion: "1.14"
weight: 80
description: "Composition functions allow you to template resources using Go"
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
[Go](https://go.dev).

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

To write a function in Go:

1. [Install the tools you need to write the function](#install-the-tools-you-need-to-write-the-function)
1. [Initialize the function from a template](#initialize-the-function-from-a-template)
1. [Edit the template to add the function's logic](#edit-the-template-to-add-the-functions-logic)
1. [Test the function end-to-end](#test-the-function-end-to-end)
1. [Build and push the function to a package repository](#build-and-push-the-function-to-a-package-registry)

This guide covers each of these steps in detail.

## Install the tools you need to write the function

To write a function in Go you need:

* [Go](https://go.dev/dl/) v1.21 or newer. The guide uses Go v1.21.
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
[a GitHub repository](https://github.com/crossplane/function-template-go)
as a template.

```shell {copy-lines=1}
crossplane beta xpkg init function-xbuckets function-template-go -d function-xbuckets 
Initialized package "function-xbuckets" in directory "/home/negz/control/negz/function-xbuckets" from https://github.com/crossplane/function-template-go/tree/91a1a5eed21964ff98966d72cc6db6f089ad63f4 (main)
```

The `crossplane beta init xpkg` command creates a directory named
`function-xbuckets`. When you run the command the new directory should look like
this:

```shell {copy-lines=1}
ls function-xbuckets
Dockerfile  fn.go  fn_test.go  go.mod  go.sum  input/  LICENSE  main.go  package/  README.md  renovate.json
```

The `fn.go` file is where you add the function's code. It's useful to know about
some other files in the template:

* `main.go` runs the function. You don't need to edit `main.go`.
* `Dockerfile` builds the function runtime. You don't need to edit `Dockerfile`.
* The `input` directory defines the function's input type.
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

You must make some changes before you start adding code:

* Edit `package/crossplane.yaml` to change the package's name.
* Edit `go.mod` to change the Go module's name.

Name your package `function-xbuckets`.

The name of your module depends on where you want to keep your function code. If
you push Go code to GitHub, you can use your GitHub username. For example
`module github.com/negz/function-xbuckets`.

The function in this guide doesn't use an input type. For this function you
should delete the `input` and `package/input` directories.

The `input` directory defines a Go struct that a function can use to take input,
using the `input` field from a Composition. The
[composition functions]{{<ref "../concepts/composition-functions" >}}
documentation explains how to pass an input to a composition function.

The `package/input` directory contains an OpenAPI schema generated from the
structs in the `input` directory.

{{<hint "tip">}}
If you're writing a function that uses an input, edit the input to meet your
function's requirements.

Change the input's kind and API group. Don't use `Input` and
`template.fn.crossplane.io`. Instead use something meaningful to your function.

When you edit files under the `input` directory you must update some generated
files by running `go generate`. See `input/generate.go` for details.

```shell
go generate ./...
```
{{</hint>}}

## Edit the template to add the function's logic

You add your function's logic to the
{{<hover label="hello-world" line="1">}}RunFunction{{</hover>}}
method in `fn.go`. When you first open the file it contains a "hello world"
function.

```go {label="hello-world"}
func (f *Function) RunFunction(_ context.Context, req *fnv1beta1.RunFunctionRequest) (*fnv1beta1.RunFunctionResponse, error) {
	f.log.Info("Running Function", "tag", req.GetMeta().GetTag())

	rsp := response.To(req, response.DefaultTTL)

	in := &v1beta1.Input{}
	if err := request.GetInput(req, in); err != nil {
		response.Fatal(rsp, errors.Wrapf(err, "cannot get Function input from %T", req))
		return rsp, nil
	}

	response.Normalf(rsp, "I was run with input %q", in.Example)
	return rsp, nil
}
```

All Go composition functions have a `RunFunction` method. Crossplane passes
everything the function needs to run in a
{{<hover label="hello-world" line="1">}}RunFunctionRequest{{</hover>}} struct.

The function tells Crossplane what resources it should compose by returning a
{{<hover label="hello-world" line="13">}}RunFunctionResponse{{</hover>}} struct.

{{<hint "tip">}}
Crossplane generates the `RunFunctionRequest` and `RunFunctionResponse` structs
using [Protocol Buffers](http://protobuf.dev). You can find detailed schemas for
`RunFunctionRequest` and `RunFunctionResponse` in the
[Buf Schema Registry](https://buf.build/crossplane/crossplane/docs/main:apiextensions.fn.proto.v1beta1).
{{</hint>}}

Edit the `RunFunction` method to replace it with this code.

```go {hl_lines="4-56"}
func (f *Function) RunFunction(_ context.Context, req *fnv1beta1.RunFunctionRequest) (*fnv1beta1.RunFunctionResponse, error) {
	rsp := response.To(req, response.DefaultTTL)

	xr, err := request.GetObservedCompositeResource(req)
	if err != nil {
		response.Fatal(rsp, errors.Wrapf(err, "cannot get observed composite resource from %T", req))
		return rsp, nil
	}

	region, err := xr.Resource.GetString("spec.region")
	if err != nil {
		response.Fatal(rsp, errors.Wrapf(err, "cannot read spec.region field of %s", xr.Resource.GetKind()))
		return rsp, nil
	}

	names, err := xr.Resource.GetStringArray("spec.names")
	if err != nil {
		response.Fatal(rsp, errors.Wrapf(err, "cannot read spec.names field of %s", xr.Resource.GetKind()))
		return rsp, nil
	}

	desired, err := request.GetDesiredComposedResources(req)
	if err != nil {
		response.Fatal(rsp, errors.Wrapf(err, "cannot get desired resources from %T", req))
		return rsp, nil
	}

	_ = v1beta1.AddToScheme(composed.Scheme)

	for _, name := range names {
		b := &v1beta1.Bucket{
			ObjectMeta: metav1.ObjectMeta{
				Annotations: map[string]string{
					"crossplane.io/external-name": name,
				},
			},
			Spec: v1beta1.BucketSpec{
				ForProvider: v1beta1.BucketParameters{
					Region: ptr.To[string](region),
				},
			},
		}

		cd, err := composed.From(b)
		if err != nil {
			response.Fatal(rsp, errors.Wrapf(err, "cannot convert %T to %T", b, &composed.Unstructured{}))
			return rsp, nil
		}

		desired[resource.Name("xbuckets-"+name)] = &resource.DesiredComposed{Resource: cd}
	}

	if err := response.SetDesiredComposedResources(rsp, desired); err != nil {
		response.Fatal(rsp, errors.Wrapf(err, "cannot set desired composed resources in %T", rsp))
		return rsp, nil
	}

	return rsp, nil
}
```

Expand the below block to view the full `fn.go`, including imports and
commentary explaining the function's logic.

{{<expand "The full fn.go file" >}}
```go
package main

import (
	"context"

	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/utils/ptr"

	"github.com/upbound/provider-aws/apis/s3/v1beta1"

	"github.com/crossplane/function-sdk-go/errors"
	"github.com/crossplane/function-sdk-go/logging"
	fnv1beta1 "github.com/crossplane/function-sdk-go/proto/v1beta1"
	"github.com/crossplane/function-sdk-go/request"
	"github.com/crossplane/function-sdk-go/resource"
	"github.com/crossplane/function-sdk-go/resource/composed"
	"github.com/crossplane/function-sdk-go/response"
)

// Function returns whatever response you ask it to.
type Function struct {
	fnv1beta1.UnimplementedFunctionRunnerServiceServer

	log logging.Logger
}

// RunFunction observes an XBuckets composite resource (XR). It adds an S3
// bucket to the desired state for every entry in the XR's spec.names array.
func (f *Function) RunFunction(_ context.Context, req *fnv1beta1.RunFunctionRequest) (*fnv1beta1.RunFunctionResponse, error) {
	f.log.Info("Running Function", "tag", req.GetMeta().GetTag())

	// Create a response to the request. This copies the desired state and
	// pipeline context from the request to the response.
	rsp := response.To(req, response.DefaultTTL)

	// Read the observed XR from the request. Most functions use the observed XR
	// to add desired managed resources.
	xr, err := request.GetObservedCompositeResource(req)
	if err != nil {
		// If the function can't read the XR, the request is malformed. This
		// should never happen. The function returns a fatal result. This tells
		// Crossplane to stop running functions and return an error.
		response.Fatal(rsp, errors.Wrapf(err, "cannot get observed composite resource from %T", req))
		return rsp, nil
	}

	// Create an updated logger with useful information about the XR.
	log := f.log.WithValues(
		"xr-version", xr.Resource.GetAPIVersion(),
		"xr-kind", xr.Resource.GetKind(),
		"xr-name", xr.Resource.GetName(),
	)

	// Get the region from the XR. The XR has getter methods like GetString,
	// GetBool, etc. You can use them to get values by their field path.
	region, err := xr.Resource.GetString("spec.region")
	if err != nil {
		response.Fatal(rsp, errors.Wrapf(err, "cannot read spec.region field of %s", xr.Resource.GetKind()))
		return rsp, nil
	}

	// Get the array of bucket names from the XR.
	names, err := xr.Resource.GetStringArray("spec.names")
	if err != nil {
		response.Fatal(rsp, errors.Wrapf(err, "cannot read spec.names field of %s", xr.Resource.GetKind()))
		return rsp, nil
	}

	// Get all desired composed resources from the request. The function will
	// update this map of resources, then save it. This get, update, set pattern
	// ensures the function keeps any resources added by other functions.
	desired, err := request.GetDesiredComposedResources(req)
	if err != nil {
		response.Fatal(rsp, errors.Wrapf(err, "cannot get desired resources from %T", req))
		return rsp, nil
	}

	// Add v1beta1 types (including Bucket) to the composed resource scheme.
	// composed.From uses this to automatically set apiVersion and kind.
	_ = v1beta1.AddToScheme(composed.Scheme)

	// Add a desired S3 bucket for each name.
	for _, name := range names {
		// One advantage of writing a function in Go is strong typing. The
		// function can import and use managed resource types from the provider.
		b := &v1beta1.Bucket{
			ObjectMeta: metav1.ObjectMeta{
				// Set the external name annotation to the desired bucket name.
				// This controls what the bucket will be named in AWS.
				Annotations: map[string]string{
					"crossplane.io/external-name": name,
				},
			},
			Spec: v1beta1.BucketSpec{
				ForProvider: v1beta1.BucketParameters{
					// Set the bucket's region to the value read from the XR.
					Region: ptr.To[string](region),
				},
			},
		}

		// Convert the bucket to the unstructured resource data format the SDK
		// uses to store desired composed resources.
		cd, err := composed.From(b)
		if err != nil {
			response.Fatal(rsp, errors.Wrapf(err, "cannot convert %T to %T", b, &composed.Unstructured{}))
			return rsp, nil
		}

		// Add the bucket to the map of desired composed resources. It's
		// important that the function adds the same bucket every time it's
		// called. It's also important that the bucket is added with the same
		// resource.Name every time it's called. The function prefixes the name
		// with "xbuckets-" to avoid collisions with any other composed
		// resources that might be in the desired resources map.
		desired[resource.Name("xbuckets-"+name)] = &resource.DesiredComposed{Resource: cd}
	}

	// Finally, save the updated desired composed resources to the response.
	if err := response.SetDesiredComposedResources(rsp, desired); err != nil {
		response.Fatal(rsp, errors.Wrapf(err, "cannot set desired composed resources in %T", rsp))
		return rsp, nil
	}

	// Log what the function did. This will only appear in the function's pod
	// logs. A function can use response.Normal and response.Warning to emit
	// Kubernetes events associated with the XR it's operating on.
	log.Info("Added desired buckets", "region", region, "count", len(names))

	return rsp, nil
}
```
{{</expand>}}

This code:

1. Gets the observed composite resource from the `RunFunctionRequest`.
1. Gets the region and bucket names from the observed composite resource.
1. Adds one desired S3 bucket for each bucket name.
1. Returns the desired S3 buckets in a `RunFunctionResponse`.

The code uses the `v1beta1.Bucket` type from
[Upbound's AWS S3 provider](https://github.com/upbound/provider-aws). One
advantage of writing a function in Go is that you can compose resources using
the same strongly typed structs Crossplane uses in its providers.

You must get the AWS Provider Go module to use this type:

```shell
go get github.com/upbound/provider-aws@v0.43.0
```

Crossplane provides a
[software development kit](https://github.com/crossplane/function-sdk-go) (SDK)
for writing composition functions in [Go](https://go.dev). This function uses
utilities from the SDK. In particular the `request` and `response` packages make
working with the `RunFunctionRequest` and `RunFunctionResponse` types easier.

{{<hint "tip">}}
Read the
[Go package documentation](https://pkg.go.dev/github.com/crossplane/function-sdk-go)
for the SDK.
{{</hint>}}

## Test the function end-to-end

Test your function by adding unit tests, and by using the `crossplane beta
render` command.

Go has rich support for unit testing. When you initialize a function from the
template it adds some unit tests to `fn_test.go`. These tests follow Go's
[recommendations](https://github.com/golang/go/wiki/TestComments). They use only
[`pkg/testing`](https://pkg.go.dev/testing) from the Go standard library and
[`google/go-cmp`](https://pkg.go.dev/github.com/google/go-cmp/cmp).

To add test cases, update the `cases` map in `TestRunFunction`. Expand the below
block to view the full `fn_test.go` file for the function.

{{<expand "The full fn_test.go file" >}}
```go
package main

import (
	"context"
	"testing"
	"time"

	"github.com/google/go-cmp/cmp"
	"github.com/google/go-cmp/cmp/cmpopts"
	"google.golang.org/protobuf/testing/protocmp"
	"google.golang.org/protobuf/types/known/durationpb"

	"github.com/crossplane/crossplane-runtime/pkg/logging"

	fnv1beta1 "github.com/crossplane/function-sdk-go/proto/v1beta1"
	"github.com/crossplane/function-sdk-go/resource"
)

func TestRunFunction(t *testing.T) {
	type args struct {
		ctx context.Context
		req *fnv1beta1.RunFunctionRequest
	}
	type want struct {
		rsp *fnv1beta1.RunFunctionResponse
		err error
	}

	cases := map[string]struct {
		reason string
		args   args
		want   want
	}{
		"AddTwoBuckets": {
			reason: "The Function should add two buckets to the desired composed resources",
			args: args{
				req: &fnv1beta1.RunFunctionRequest{
					Observed: &fnv1beta1.State{
						Composite: &fnv1beta1.Resource{
							// MustStructJSON is a handy way to provide mock
							// resources.
							Resource: resource.MustStructJSON(`{
								"apiVersion": "example.crossplane.io/v1alpha1",
								"kind": "XBuckets",
								"metadata": {
									"name": "test"
								},
								"spec": {
									"region": "us-east-2",
									"names": [
										"test-bucket-a",
										"test-bucket-b"
									]
								}
							}`),
						},
					},
				},
			},
			want: want{
				rsp: &fnv1beta1.RunFunctionResponse{
					Meta: &fnv1beta1.ResponseMeta{Ttl: durationpb.New(60 * time.Second)},
					Desired: &fnv1beta1.State{
						Resources: map[string]*fnv1beta1.Resource{
							"xbuckets-test-bucket-a": {Resource: resource.MustStructJSON(`{
								"apiVersion": "s3.aws.upbound.io/v1beta1",
								"kind": "Bucket",
								"metadata": {
									"annotations": {
										"crossplane.io/external-name": "test-bucket-a"
									}
								},
								"spec": {
									"forProvider": {
										"region": "us-east-2"
									}
								}
							}`)},
							"xbuckets-test-bucket-b": {Resource: resource.MustStructJSON(`{
								"apiVersion": "s3.aws.upbound.io/v1beta1",
								"kind": "Bucket",
								"metadata": {
									"annotations": {
										"crossplane.io/external-name": "test-bucket-b"
									}
								},
								"spec": {
									"forProvider": {
										"region": "us-east-2"
									}
								}
							}`)},
						},
					},
				},
			},
		},
	}

	for name, tc := range cases {
		t.Run(name, func(t *testing.T) {
			f := &Function{log: logging.NewNopLogger()}
			rsp, err := f.RunFunction(tc.args.ctx, tc.args.req)

			if diff := cmp.Diff(tc.want.rsp, rsp, protocmp.Transform()); diff != "" {
				t.Errorf("%s\nf.RunFunction(...): -want rsp, +got rsp:\n%s", tc.reason, diff)
			}

			if diff := cmp.Diff(tc.want.err, err, cmpopts.EquateErrors()); diff != "" {
				t.Errorf("%s\nf.RunFunction(...): -want err, +got err:\n%s", tc.reason, diff)
			}
		})
	}
}
```
{{</expand>}}

Run the unit tests using the `go test` command:

```shell
go test -v -cover .
=== RUN   TestRunFunction
=== RUN   TestRunFunction/AddTwoBuckets
--- PASS: TestRunFunction (0.00s)
    --- PASS: TestRunFunction/AddTwoBuckets (0.00s)
PASS
coverage: 52.6% of statements
ok      github.com/negz/function-xbuckets       0.016s  coverage: 52.6% of statements
```

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

Use `go run` to run your function locally.

```shell {label="run"}
go run . --insecure --debug
```

{{<hint "warning">}}
The {{<hover label="run" line="1">}}insecure{{</hover>}} flag tells the function
to run without encryption or authentication. Only use it during testing and
development.
{{</hint>}}

In a separate terminal, run `crossplane beta render`. 

```shell
crossplane beta render xr.yaml composition.yaml functions.yaml
```

This command calls your function. In the terminal where your function is running
you should now see log output:

```shell
go run . --insecure --debug
2023-10-31T16:17:32.158-0700    INFO    function-xbuckets/fn.go:29      Running Function        {"tag": ""}
2023-10-31T16:17:32.159-0700    INFO    function-xbuckets/fn.go:125     Added desired buckets   {"xr-version": "example.crossplane.io/v1", "xr-kind": "XBuckets", "xr-name": "example-buckets", "region": "us-east-2", "count": 3}
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
