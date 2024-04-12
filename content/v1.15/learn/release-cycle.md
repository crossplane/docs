---
title: Release Cycle
weight: 308
---

Starting with the v1.10.0 release, Crossplane is released on a quarterly (13
week) cadence. A cycle is comprised of three general stages:

- Weeks 1—11: [Active Development]
- Week 12: [Feature Freeze]
- Week 13: [Code Freeze]

This results in four releases per year, with the most recent three releases
being maintained at any given time. When a new release is cut, the fourth most
recent release reaches end of life (EOL). Users can expect any given release to
be maintained for nine months.

### Definition of maintenance

The Crossplane community defines maintenance in that relevant bug fixes that are
merged to the main development branch will be eligible to be back-ported to the
release branch of any currently maintained version, and patch releases will be
cut appropriately. It's also possible that a fix may be merged directly to the
release branch if no longer applicable on the main development branch.
Maintenance doesn't indicate any SLA on response time for user support in the
form of Slack messages or issues, but problems will be addressed on a best
effort basis by maintainers and contributors for currently maintained releases.

### Patch releases

_This policy is subject to change in the future._

Patch releases are cut for currently maintained minor versions on an as-needed
basis. Any critical back-ported fixes will be included in a patch release as
soon as possible after merge.

### Pre-releases

_This policy is subject to change in the future._

Alpha, Beta, and RC releases are cut for an upcoming release on an as-needed
basis. As a policy, at least one pre-release will be cut prior to any minor
release. Pre-releases won't be made on release branches.

### Provider releases

The Crossplane release cycle isn't required to be adhered to by any other
Crossplane projects, but a similar cadence is encouraged. Maintainers listed in
each repository's `OWNERS.md` file are responsible for determining and
publishing the release cycle for their project.

## Release stages

The following stages are the main milestones in a Crossplane release.

### Active development

During active development, any code that meets the requisite criteria (i.e.
passing appropriate tests, approved by a maintainer, etc.) will be merged into
the main development branch. At present, there is no requirement to formally
submit an enhancement proposal prior to the start of the release cycle, but
contributors are encouraged to open an issue and gather feedback before starting
work on a major implementation (see [CONTRIBUTING.md] for more information).

### Feature freeze

During feature freeze, no new functionality should be merged into the main
development branch. Bug fixes, documentation changes, and non-critical changes
may be made. In the case that a new feature is deemed absolutely necessary for a
release, the Crossplane maintainers will weigh the impact of the change and make
a decision on whether it should be included. 

### Code freeze

During code freeze, there should be no changes merged to the main development
branch with the following exceptions:
- Fixes to a failing test that's deemed to be incorrectly testing
  functionality.
- Documentation only changes. It's possible that a documentation freeze will be
  implemented in the future, but it's not currently enforced.
- Fixes to a critical bug that wasn't previously identified. Merging a bug fix
  during code freeze requires application for and approval of an exception by
  Crossplane maintainers. This process is currently informal, but may be
  formalized in the future.

## Release dates

Crossplane releases once a quarter (every 13 weeks). Typically, the release
happens on the Tuesday of the last week of the quarter, as shown on the
[community calendar][community calendar]. Keep in mind that the specific date is
**approximate**. A lot of factors can alter the date slightly, such as code
reviews, testing, and bug fixing to ensure a quality release.

<!-- Named links -->

[Active Development]: #active-development
[Feature Freeze]: #feature-freeze
[Code Freeze]: #code-freeze
[CONTRIBUTING.md]: https://github.com/crossplane/crossplane/blob/master/CONTRIBUTING.md
[community calendar]: https://calendar.google.com/calendar/embed?src=c_2cdn0hs9e2m05rrv1233cjoj1k%40group.calendar.google.com
