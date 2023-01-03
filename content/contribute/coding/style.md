---
title: "Coding Style"
weight: 10
---
<!-- vale off -->
The Crossplane project prefers not to maintain its own style guide, but we do
enforce the style and best practices established by the Go project and its
community. This means contributors should:

* Follow the guidelines set out by the [Effective Go] document.
* Preempt common Go [code review comments] and [test review comments].
* Follow Crossplane's [Observability Developer Guide].

These coding style guidelines apply to all https://github.com/crossplane and
https://github.com/crossplane-contrib repositories unless stated otherwise.

Below we cover some of the feedback we most frequently leave on pull requests.
Most of these are covered by the documents above, but may be subtle or easily
missed and thus warrant closer attention.

### Explain 'nolint' Directives

We use [golangci-lint] on all our repositories to enforce many style and safety
rules that are not covered here. We prefer to tolerate false positives from our
linter configuration in order to make sure we catch as many issues as possible.
This means it's sometimes necessary to override the linter to make a build pass.

You can override the linter using a `//nolint` comment directive. When you do so
you must:

1. Be specific. Apply `//nolint:nameoflinter` at as tight a scope as possible.
1. Include a comment explaining why you're disabling the linter.

For example:

```go
func hash(s string) string {
        h := fnv.New32()
        _ = h.Write([]byte(s)) //nolint:errcheck // Writing to a hash never returns an error.
        return fmt.Sprintf("%x", h.Sum32())
}
```

Here we only disable the specific linter that would emit a warning (`errcheck`),
for the specific line where that warning would be emitted.

### Use Descriptive Variable Names Sparingly

Quoting the Go [code review comments]:

> Variable names in Go should be short rather than long. This is especially true
> for local variables with limited scope. Prefer `c` to `lineCount`. Prefer `i`
> to `sliceIndex`.
>
> The basic rule: the further from its declaration that a name is used, the more
> descriptive the name must be. For a method receiver, one or two letters is
> sufficient. Common variables such as loop indices and readers can be a single
> letter (`i`, `r`). More unusual things and global variables need more
> descriptive names.

Another way to frame the above is that we prefer to use short variables in all
cases where a (human) reader could easily infer what the variable was from its
source. For example:

```go

// NumberOfGeese might be used outside this package, or many many lines further
// down the file so it needs a descriptive name. It's also just an int, which
// doesn't give the reader much clue about what it's for.
const NumberOfGeese = 42

// w is plenty for the first argument here. Naming it gooseWrangler is redundant
// because readers can tell what it is from its type. looseGeese on the other
// hand warrants a descriptive name. It's short lived (lines wise), and its type
// doesn't give us any context about what it's for.
func capture(w goose.Wrangler, looseGeese int) error {
        // Important goose capturing logic.
        for looseGeese > 0 {
                // It's not obvious from the w.Wrangle method name what the
                // return value is, so a descriptive name names sense here too.
                captured, err := w.Wrangle()
                if err != nil {
                        return errors.Wrap(err, "defeated by geese")
                }
                looseGeese = looseGeese - captured
        }

        // We prefer 'y' to 'yard' here because 'yard' is implied by 'NewYard'.
        y := goose.NewYard(w)
        return y.Secure()
}
```

### Don't Wrap Function Signatures

Quoting again from the Go [code review comments]:

> Most of the time when people wrap lines "unnaturally" (in the middle of
> function calls or function declarations, more or less, say, though some
> exceptions are around), the wrapping would be unnecessary if they had a
> reasonable number of parameters and reasonably short variable names. Long
> lines seem to go with long names, and getting rid of the long names helps a
> lot.

```go
func capture(gooseWrangler goose.Wrangler, looseGeese int, gooseYard goose.Yard,
        duckWrangler duck.Wrangler, looseDucks, duckYard duck.Yard) error {
        // Important fowl wrangling logic.
}
```

If you find the need to wrap a function signature like the above it's almost
always a sign that your argument names are superfluously verbose, or that your
function is doing too much. If your function needs to take many optional
arguments, perhaps to enable dependency injection, use variadic functions as
options. In this case we usually make an exception for wrapped function calls.
For example:

```go
type Wrangler struct {
        fw fowl.Wrangler
        loose int
}

type Option func(w *Wrangler)

func WithFowlWrangler(fw fowl.Wrangler) Option {
        return func(w *Wrangler) {
                w.fw = fw
        }
}

func NewWrangler(looseGeese int, o ...Option) *Wrangler {
        w := &Wrangler{
                fw: fowl.DefaultWrangler{}
                loose: 
        }

        for _, fn := range o {
                fn(w)
        }

        return w
}

func example() {
        w := NewWrangler(42,
                WithFowlWrangler(chicken.NewWrangler()),
                WithSomeOtherOption(),
                WithYetAnotherOption())
        
        w.Wrangle()
}
```

You can read more about this pattern on [Dave Cheney's blog].

### Return Early

We prefer to return early. Another way to think about this is that we prefer to
handle terminal cases (e.g. errors) early. So for example instead of:

```go
func example() error {
        v := fetch()
        if v == 42 {
                // Really important business logic.
                b := embiggen(v)
                for k, v := range lookup(b) {
                        if v == true {
                                store(k)
                        } else {
                                remove(k)
                        }
                }
                return nil
        }
        return errors.New("v was a bad number")
}
```

We prefer:

```go
func example() error {
        v := fetch()
        if v != 42 {
                return errors.New("v was a bad number")
        }
        // Really important business logic.
        b := embiggen(v)
        for k, v := range lookup(b) {
                // "Continue early" is a variant of "return early".
                if v == false {
                        remove(k)
                        continue
                }
                store(k)
        }
        return nil
}
```

This approach gets error handling out of the way first, allowing the 'core' of
the function to follow at the scope of the function, not a conditional. Or put
otherwise, with the least amount of indentation. An interesting side effect of
this approach is that it's rare to find an `else` in Crossplane code (at the
time of writing there are four uses of `else` in `crossplane/crossplane`).
Quoting [Effective Go]:

> In the Go libraries, you'll find that when an if statement doesn't flow into
> the next statement—that is, the body ends in break, continue, goto, or
> return—the unnecessary else is omitted.

### Wrap Errors

Use [`crossplane-runtime/pkg/errors`] to wrap errors with context. This allows
us to emit logs and events with useful, specific errors that can be related to
deeper parts of the codebase without having to actually plumb loggers and event
sources deep down into the codebase. For example:

```go
import "github.com/crossplane/crossplane-runtime/pkg/errors"

func example() error {
        v, err := fetch()
        if err != nil {
                return errors.Wrap(err, "could not fetch the thing")
        }

        store(embiggen(v))
        return nil
}
```

### Scope Errors

Where possible, keep errors as narrowly scoped as possible. This avoids bugs
that can appear due to 'shadowed' errors, i.e. accidental re-use of an existing
`err` variable, as code is refactored over time. Keeping errors scoped to the
error handling conditional block can help protect against this. So for example
instead of:

```go
func example() error {
        err := enable()
        if err != nil {
                return errors.Wrap(err, "could not enable the thing")
        }

        // 'err' still exists here at the function scope.

        return errors.Wrap(emit(), "could not emit the thing")
}
```

We prefer:

```go
func example() error {
        if err := enable(); err != nil {
                // 'err' exists here inside the conditional block.
                return errors.Wrap(err, "could not enable the thing")
        }

        // 'err' does not exist here at the function scope. It's scoped to the
        // above conditional block.

        return errors.Wrap(emit(), "could not emit the thing")
}
```

Note that the 'return early' advice above trumps this rule - it's okay to
declare errors at the function scope if it lets you keep business logic less
nested. That is, instead of:

```go
func example() error {
        if v, err := fetch(); err != nil {
                return errors.Wrap(err, "could not enable the thing")
        } else {
                store(embiggen(v))
        }
        
        return nil
}
```

We prefer:

```go
func example() error {
        v, err := fetch()
        if err != nil {
                return errors.Wrap(err, "could not enable the thing")
        }

        store(embiggen(v))
        return nil
}
```

### Prefer Table Driven Tests

As mentioned in [Contributing Code](#contributing-code) Crossplane diverges from
common controller-runtime patterns in that it follows the advice laid out in the
Go project's [test review comments] documents. This means we prefer table driven
tests, and avoid test frameworks like Ginkgo. The most common form of Crossplane
test is as follows:

```go
// Example is the function we're testing.
func Example(ctx context.Context, input string) (int, error) {
        // ...
}

// Test function names are always PascalCase. No underscores.
func TestExample(t *testing.T) {
        type args struct {
                ctx   context.Context
                input string
        }

        type want struct {
                output int
                err    error
        }

        cases := map[string]struct{
                reason string
                args   args
                want   want
        }{
                // The summary is always PascalCase. No spaces, hyphens, or underscores.
                "BriefTestCaseSummary": {
                        reason: "A longer summary of what we're testing - printed if the test fails.",
                        args: args{
                                ctx: context.Background(),
                                input: "some input value",
                        }
                        want: want{
                                output: "the expected output",
                                err: nil,
                        }
                },
        }
        
        for name, tc := range cases {
                t.Run(name, func(t *testing.T) {
                        got, err := Example(tc.args.ctx, tc.args.input)

                        // We prefer to use https://github.com/google/go-cmp/
                        // even for simple comparisons to keep test output
                        // consistent. Some Crossplane specific cmp options can
                        // be found in crossplane-runtime/pkg/test.
                        if diff := cmp.Diff(tc.want.err, err, test.EquateErrors()); diff != "" {
                                t.Errorf("%s\nExample(...): -want, +got:\n%s", tc.reason, diff)
                        }

                        if diff := cmp.Diff(tc.want.output, got); diff != "" {
                                t.Errorf("%s\nExample(...): -want, +got:\n%s", tc.reason, diff)
                        }
                })
        }
}
```

<!-- vale on -->
[Slack]: https://slack.crossplane.io/
[code of conduct]: https://github.com/cncf/foundation/blob/master/code-of-conduct.md
[build submodule]: https://github.com/upbound/build/
[`kind`]: https://kind.sigs.k8s.io/
[Crossplane release cycle]: docs/reference/release-cycle.md
[good git commit hygiene]: https://www.futurelearn.com/info/blog/telling-stories-with-your-git-history
[Developer Certificate of Origin]: https://github.com/apps/dco
[code review comments]: https://github.com/golang/go/wiki/CodeReviewComments
[test review comments]: https://github.com/golang/go/wiki/TestComments
[crossplane-runtime]: https://github.com/crossplane/crossplane-runtime
[docs]: docs/
[Effective Go]: https://golang.org/doc/effective_go
[Observability Developer Guide]: docs/contributing/observability_developer_guide.md
[Dave Cheney's blog]: https://dave.cheney.net/2014/10/17/functional-options-for-friendly-apis
[`crossplane-runtime/pkg/errors`]: https://pkg.go.dev/github.com/crossplane/crossplane-runtime/pkg/errors
[golangci-lint]: https://golangci-lint.run/