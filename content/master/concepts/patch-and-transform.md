---
title: Patch and Transforms
weight: 55
---

### Influencing External Names

The `crossplane.io/external-name` annotation has special meaning to Crossplane
managed resources - it specifies the name (or identifier) of the resource in the
external system, for example the actual name of a `CloudSQLInstance` in the GCP
API. Some managed resources don't let you specify an external name - in those
cases Crossplane will set it for you to whatever the external system requires.

If you add the `crossplane.io/external-name` annotation to a claim Crossplane
will automatically propagate it when it creates an XR. It's good practice to
have your `Composition` further propagate the annotation to one or more composed
resources, but it's not required.

where `MyResource` is a Composite Resource Claim kind.
When a Composite Resource or a Claim has the `crossplane.io/paused` annotation
with its value set to `true`, the Composite Resource controller or the Claim
controller pauses reconciliations on the resource until
the annotation is removed or its value set to something other than `true`.
Before temporarily pausing reconciliations, an event with the type `Synced`,
the status `False`, and the reason `ReconcilePaused` is emitted
on the resource.
Please also note that annotations on a Composite Resource Claim are propagated
to the associated Composite Resource but when the
`crossplane.io/paused: "true"` annotation is added to a Claim, because
reconciliations on the Claim are now paused, this newly added annotation
will not be propagated. However, whenever the annotation's value is set to a
non-`true` value, reconciliations on the Claim will now resume, and thus the
annotation will now be propagated to the associated Composite Resource
with a non-`true` value. An implication of the described behavior is that
pausing reconciliations on the Claim will not inherently pause reconciliations
on the associated Composite Resource.

<!-- This also related to XRs -->
### Connection Details

Connection details secret of XR is an aggregated sum of the connection details
of the composed resources. It's recommended that the author of XRD specify
exactly which keys will be allowed in the XR connection secret by listing them
in `spec.connectionSecretKeys` so that consumers of claims and XRs can see what
they can expect in the connection details secret.

If `spec.connectionSecretKeys` is empty, then all keys of the aggregated connection
details secret will be propagated.

You can derive the following types of connection details from a composed
resource to be aggregated:

`FromConnectionSecretKey`. Derives an XR connection detail from a connection
secret key of a composed resource.

```yaml
# Derive the XR's 'user' connection detail from the 'username' key of the
# composed resource's connection secret.
- type: FromConnectionSecretKey
  name: user
  fromConnectionSecretKey: username
```

`FromFieldPath`. Derives an XR connection detail from a field path within the
composed resource.

```yaml
# Derive the XR's 'user' connection detail from the 'adminUser' status field of
# the composed resource.
- type: FromFieldPath
  name: user
  fromFieldPath: status.atProvider.adminUser
```

`FromValue`. Derives an XR connection detail from a fixed value.

```yaml
# Always sets the XR's 'user' connection detail to 'admin'.
- type: FromValue
  name: user
  value: admin
```

<!-- break --> 

You'll encounter a lot of 'field paths' when reading or writing a `Composition`.
Field paths reference a field within a Kubernetes object via a simple string
'path'. [API conventions][field-paths] describe the syntax as:

> Standard JavaScript syntax for accessing that field, assuming the JSON object
> was transformed into a JavaScript object, without the leading dot, such as
> `metadata.name`.

 Valid field paths include:

* `metadata.name` - The `name` field of the `metadata` object.
* `spec.containers[0].name` - The `name` field of the 0th `containers` element.
* `data[.config.yml]` - The `.config.yml` field of the `data` object.
* `apiVersion` - The `apiVersion` field of the root object.

 While the following are invalid:

* `.metadata.name` - Leading period.
* `metadata..name` - Double period.
* `metadata.name.` - Trailing period.
* `spec.containers[]` - Empty brackets.
* `spec.containers.[0].name` - Period before open bracket.

### Patch Types

You can use the following types of patch in a `Composition`:

`FromCompositeFieldPath`. The default if the `type` is omitted. This type
patches from a field within the XR to a field within the composed resource. It's
commonly used to expose a composed resource spec field as an XR spec field.

```yaml
# Patch from the XR's spec.parameters.size field to the composed resource's
# spec.forProvider.settings.tier field.
- type: FromCompositeFieldPath
  fromFieldPath: spec.parameters.size
  toFieldPath: spec.forProvider.settings.tier
```

`ToCompositeFieldPath`. The inverse of `FromCompositeFieldPath`. This type
patches from a field within the composed resource to a field within the XR. It's
commonly used to derive an XR status field from a composed resource status
field.

```yaml
# Patch from the composed resource's status.atProvider.zone field to the XR's
# status.zone field.
- type: ToCompositeFieldPath
  fromFieldPath: status.atProvider.zone
  toFieldPath: status.zone
```

`FromCompositeFieldPath` and `ToCompositeFieldPath` patches can also take a wildcarded
field path in the `toFieldPath` parameter and patch each array element in the `toFieldPath`
with the singular value provided in the `fromFieldPath`.

```yaml
# Patch from the XR's spec.parameters.allowedIPs to the CIDRBlock elements
# inside the array spec.forProvider.firewallRules on the composed resource.
resources:
- name: exampleFirewall
  base:
    apiVersion: firewall.example.crossplane.io/v1beta1
    kind: Firewall
    spec:
      forProvider:
        firewallRules:
        - Action: "Allow"
          Destination: "example1"
          CIDRBlock: ""
        - Action: "Allow"
          Destination: "example2"
          CIDRBlock: ""
- type: FromCompositeFieldPath
  fromFieldPath: spec.parameters.allowedIP
  toFieldPath: spec.forProvider.firewallRules[*].CIDRBlock
```

`FromEnvironmentFieldPath`. This type patches from a field within the in-memory
environment to a field within the composed resource. It's commonly used to
expose a composed resource spec field as an XR spec field.
Note that EnvironmentConfigs are an alpha feature and need to be enabled with 
the `--enable-environment-configs` flag on startup.

```yaml
# Patch from the environment's tier.name field to the composed resource's
# spec.forProvider.settings.tier field.
- type: FromEnvironmentFieldPath
  fromFieldPath: tier.name
  toFieldPath: spec.forProvider.settings.tier
```

`ToEnvironmentFieldPath`. This type patches from a composed field to the
in-memory environment. Note that, unlike `ToCompositeFieldPath` patches, this
is executed before the composed resource is applied on the cluster which means
that the `status` is not available.
Note that EnvironmentConfigs are an alpha feature and need to be enabled with 
the `--enable-environment-configs` flag on startup.

```yaml
# Patch from the environment's tier.name field to the composed resource's
# spec.forProvider.settings.tier field.
- type: ToEnvironmentFieldPath
  fromFieldPath: spec.forProvider.settings.tier
  toFieldPath: tier.name
```

Note that the field to be patched requires some initial value to be set.

`CombineFromComposite`. Combines multiple fields from the XR to produce one
composed resource field.

```yaml
# Patch from the XR's spec.parameters.location field and the
# metadata.labels[crossplane.io/claim-name] label to the composed
# resource's spec.forProvider.administratorLogin field.
- type: CombineFromComposite
  combine:
    # The patch will only be applied when all variables have non-zero values.
    variables:
    - fromFieldPath: spec.parameters.location
    - fromFieldPath: metadata.labels[crossplane.io/claim-name]
    strategy: string
    string:
      fmt: "%s-%s"
  toFieldPath: spec.forProvider.administratorLogin
  # By default Crossplane will skip the patch until all of the variables to be
  # combined have values. Set the fromFieldPath policy to 'Required' to instead
  # abort composition and return an error if a variable has no value.
  policy:
    fromFieldPath: Required
```

`CombineFromEnvironment`. Combines multiple fields from the in-memory
environment to produce one composed resource field.
Note that EnvironmentConfigs are an alpha feature and need to be enabled with 
the `--enable-environment-configs` flag on startup.

```yaml
# Patch from the environments's location field and region to the composed
# resource's spec.forProvider.administratorLogin field.
- type: CombineFromEnvironment
  combine:
    # The patch will only be applied when all variables have non-zero values.
    variables:
    - fromFieldPath: location
    - fromFieldPath: region
    strategy: string
    string:
      fmt: "%s-%s"
  toFieldPath: spec.forProvider.administratorLogin
```

At the time of writing only the `string` combine strategy is supported. It uses
[Go string formatting][pkg/fmt] to combine values, so if the XR's location was
`us-west` and its claim name was `db` the composed resource's administratorLogin
would be set to `us-west-db`.

`CombineToComposite` is the inverse of `CombineFromComposite`.

```yaml
# Patch from the composed resource's spec.parameters.administratorLogin and
# status.atProvider.fullyQualifiedDomainName fields back to the XR's
# status.adminDSN field.
- type: CombineToComposite
  combine:
    variables:
      - fromFieldPath: spec.parameters.administratorLogin
      - fromFieldPath: status.atProvider.fullyQualifiedDomainName
    strategy: string
    # Here, our administratorLogin parameter and fullyQualifiedDomainName
    # status are formatted to a single output string representing a DSN.
    string:
      fmt: "mysql://%s@%s:3306/my-database-name"
  toFieldPath: status.adminDSN
```

`CombineToEnvironment` is the inverse of `CombineFromEnvironment`.
Note that EnvironmentConfigs are an alpha feature and need to be enabled with 
the `--enable-environment-configs` flag on startup.

```yaml
# Patch from the composed resource's spec.parameters.administratorLogin and
# spec.forProvider.domainName fields back to the environment's adminDSN field.
- type: CombineToEnvironment
  combine:
    variables:
      - fromFieldPath: spec.parameters.administratorLogin
      - fromFieldPath: spec.forProvider.domainName
    strategy: string
    # Here, our administratorLogin parameter and fullyQualifiedDomainName
    # status are formatted to a single output string representing a DSN.
    string:
      fmt: "mysql://%s@%s:3306/my-database-name"
  toFieldPath: adminDSN
```

`PatchSet`. References a named set of patches defined in the `spec.patchSets`
array of a `Composition`.

```yaml
# This is equivalent to specifying all of the patches included in the 'metadata'
# PatchSet.
- type: PatchSet
  patchSetName: metadata
```

The `patchSets` array may not contain patches of `type: PatchSet`. The
`transforms` and `patchPolicy` fields are ignored by `type: PatchSet`.

### Transform Types

You can use the following types of transform on a value being patched:

`map`. Transforms values using a map.

```yaml
# If the value of the 'from' field is 'us-west', the value of the 'to' field
# will be set to 'West US'.
- type: map
  map:
    us-west: West US
    us-east: East US
    au-east: Australia East
```

`match`. A more complex version of `map` that can match different kinds of
patterns. It should be used if more advanced pattern matchings than a simple
string equality check are required.
The result of the first matching pattern is used as the output of this
transform.
If no pattern matches, you can either fallback to a given `fallbackValue` or
fallback to the input value by setting the `fallbackTo` field to `Input`.

```yaml
# In the example below, if the value in the 'from' field is 'us-west', the
# value in the 'to' field will be set to 'West US'.
# If the value in the 'from' field is 'eu-west', the value in the 'to' field
# will be set to 'Unknown' because no pattern matches.
- type: match
  match:
    patterns:
      - type: literal # Not needed. This is the default.
        literal: us-west
        result: West US
      - type: regexp
        regexp: '^af-.*'
        result: Somewhere in Africa
    fallbackTo: Value # Not needed. This is the default.
    fallbackValue: Unknown

# If fallbackTo is set to Input, the output will be the input value if no
# pattern matches.
# In the example below, if the value in the 'from' field is 'us-west', the
# value in the 'to' field will be set to 'West US'.
# If the value in the 'from' field is 'eu-west', the value in the 'to' field
# will be set to 'eu-west' because no pattern matches.
- type: match
  match:
    patterns:
      - type: literal
        literal: us-west
        result: West US
      - type: regexp
        regexp: '^af-.*'
        result: Somewhere in Africa
    fallbackTo: Input
```

`math`. Transforms values using math. The input value must be an integer.
* math transform type `Multiply`, multiplies the input by the given value.
* math transform type `ClampMin`, sets a minimum value for the output.
* math transform type `ClampMax`, sets a maximum value for the output.

```yaml
# If you omit the field type, by default type is set to `Multiply`
# If the value of the 'from' field is 2, the value of the 'to' field will be set
# to 4.
- type: math
  math:
    multiply: 2
    
# This is the same as above
# If the value of the 'from' field is 2, the value of the 'to' field will be set
# to 4.
- type: math
  math:
    type: Multiply
    multiply: 2

# If the value of the 'from' field is 3, the value of the 'to' field will
# be set to 4.
- type: math
  math:
    type: ClampMin
    clampMin: 4

# If the value of the 'from' field is 3, the value of the 'to' field will
# be set to 2.
- type: math
  math:
    type: ClampMax
    clampMax: 2
```

`string`. Transforms string values. 
* string transform type `Format`, Currently only Go style fmt is supported. [Go style `fmt`][pkg/fmt] is supported.
* string transform type `Convert`, accepts one of `ToUpper`, `ToLower`, `ToBase64`, `FromBase64`, `ToJson`, `ToSha1`, `ToSha256`, `ToSha512`.
* string transform type `TrimPrefix`, accepts a string to be trimmed from the beginning of the input.
* string transform type `TrimSuffix`, accepts a string to be trimmed from the end of the input.
* string transform type `Regexp`, accepts a string for regexp to be applied to.

```yaml
# If you omit the field type, by default type is set to `Format` 
# If the value of the 'from' field is 'hello', the value of the 'to' field will
# be set to 'hello-world'.
- type: string
  string:
    fmt: "%s-world"

# This is the same as above
# the value of the 'to' field will be set to 'hello-world'.
- type: string
  string:
    type: Format
    fmt: "%s-world"

# If the value of the 'from' field is 'hello', the value of the 'to' field will
# be set to 'HELLO'.
- type: string
  string:
    type: Convert
    convert: ToUpper

# If the value of the 'from' field is 'Hello', the value of the 'to' field will
# be set to 'hello'.
- type: string
  string:
    type: Convert
    convert: ToLower

# If the value of the 'from' field is 'Hello', the value of the 'to' field will
# be set to 'SGVsbG8='.
- type: string
  string:
     type: Convert
     convert: ToBase64

# If the value of the 'from' field is 'SGVsbG8=', the value of the 'to' field will
# be set to 'Hello'.
- type: string
  string:
     type: Convert
     convert: FromBase64

# If the value of the 'from' field is not nil, the value of the 'to' field will be
# set to raw JSON representation of the 'from' field.
- type: string
  string:
     type: Convert
     convert: ToJson

# The output will be the hash of the JSON representation of the 'from' field.
- type: string
  string:
    type: Convert
    convert: ToSha1 # alternatives: 'ToSha256' or 'ToSha512'

# If the value of the 'from' field is https://crossplane.io, the value of the 'to' field will
# be set to crossplane.io
- type: string
  string:
    type: TrimPrefix
    trim: 'https://'

# If the value of the 'from' field is my-string-test, the value of the 'to' field will
# be set to my-string
- type: string
  string:
     type: TrimSuffix
     trim: '-test'

# If the value of the 'from' field is 'arn:aws:iam::42:example, the value of the
# 'to' field will be set to "42". Note that the 'to' field is always a string. 
- type: string
  string:
     type: Regexp
     regexp:
      match: 'arn:aws:iam::(\d+):.*'
      group: 1  # Optional capture group. Omit to match the entire regexp.
```

`convert`. Transforms values of one type to another, for example from a string
to an integer. The following values are supported by the `from` and `to` fields:

* `string`
* `bool`
* `int`
* `int64`
* `float64`

The strings 1, t, T, TRUE, true, and True are considered 'true', while 0, f, F,
FALSE, false, and False are considered 'false'. The integer 1 and float 1.0 are
considered true, while all other values are considered false. Similarly, boolean
true converts to integer 1 and float 1.0, while false converts to 0 and 0.0.

```yaml
# If the value to be converted is "1" (a string), the value of the 'toType'
# field will be set to 1 (an integer).
- type: convert
  convert:
   toType: int
```

Converting `string` to `float64` additionally supports parsing string in
[K8s quantity format](https://pkg.go.dev/k8s.io/apimachinery/pkg/api/resource#Quantity),
such as `1000m` or `500 Mi`:

```yaml
- type: convert
  convert:
   toType: float64
   format: quantity
```

### Patching From One Composed Resource to Another or Itself

It's not possible to patch _directly_ from one composed resource to another -
i.e. from one entry in the `spec.resources` array of a `Composition` to another.
It is however possible to achieve this by using the XR as an intermediary. To do
so:

1. Use a `ToCompositeFieldPath` patch to patch from your source composed
   resource to the XR. Typically you'll want to patch to a status field or an
   annotation.
1. Use a `FromCompositeFieldPath` patch to patch from the 'intermediary' field
   you patched to in step 1 to a field on the destination composed resource.

Note that the source and the target composed resource can be the same.