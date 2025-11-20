---
title: Release Cycle
weight: 308
description: "The Crossplane release schedule and process"
---

Starting with the v1.10.0 release, Crossplane releases on a quarterly (13
week) cadence. A cycle comprises three general stages:

- Weeks 1—11: [Active Development]
- Week 12: [Feature Freeze]
- Week 13: [Code Freeze]

This results in four releases per year, with the most recent three releases
under maintenance at any given time. When Crossplane cuts a new release, the fourth most
recent release reaches end of life (EOL). Users can expect Crossplane to maintain any given release
for nine months.

### Definition of maintenance

The Crossplane community defines maintenance as follows:
- Relevant bug fixes that merge to the main development branch are eligible for
  backporting to the release branch of any maintained version
- Crossplane cuts patch releases appropriately
- Maintainers may merge a fix directly to the release branch if it's no longer
  applicable on the main development branch

Maintenance doesn't include any SLA on response time for user support in the
form of Slack messages or issues.
However, maintainers and contributors fix problems on a best effort basis
for maintained releases.

### Patch releases

_This policy is subject to change in the future._

Crossplane cuts patch releases for maintained minor versions on an as needed
basis. Crossplane includes any critical backported fixes in a patch release as
soon as possible after merge.

### Pre-releases

_This policy is subject to change in the future._

Crossplane cuts Alpha, Beta, and RC releases for an upcoming release on an as needed
basis. As a policy, Crossplane cuts at least one pre-release before any minor
release. Crossplane doesn't make pre-releases on release branches.

### Provider releases

Other Crossplane projects don't need to adhere to the Crossplane release cycle, but Crossplane encourages a similar cadence. Maintainers listed in
each repository's `OWNERS.md` file are responsible for determining and
publishing the release cycle for their project.

## Release stages

The following stages are the main milestones in a Crossplane release.

### Active development

During active development, maintainers merge code that meets the requisite
criteria into the main development branch.
This includes code that passes appropriate tests and that a maintainer
approves.

At present, you don't need to formally submit an enhancement proposal before the
release cycle starts.
However, Crossplane encourages contributors to open an issue and gather feedback
before starting work on a major implementation.
See [CONTRIBUTING.md] for more information.

### Feature freeze

During feature freeze, maintainers shouldn't merge new features into the main
development branch.
Maintainers may make bug fixes, documentation changes, and non critical changes.

If maintainers deem a new feature essential for a release, the Crossplane
maintainers weigh the impact of the change.
They then make a decision on whether to include it.

### Code freeze

During code freeze, there should be no changes merged to the main development
branch with the following exceptions:
- Fixes to a failing test that's deemed to be incorrectly testing
  features.
- Documentation only changes. It's possible that a documentation freeze is
  implemented in the future, but it's not enforced.
- Fixes to a critical bug that wasn't identified before. Merging a bug fix
  during code freeze requires requesting and approval of an exception by
  Crossplane maintainers. This process is informal, but may be
  formalized in the future.

## Release dates

Crossplane releases once a quarter (every 13 weeks). Typically, the release
happens on the Tuesday of the last week of the quarter, as shown on the
[community calendar][community calendar]. Keep in mind that the specific date is
**about**. A lot of factors can alter the date slightly, such as code
reviews, testing, and bug fixing to ensure a quality release.

## Release process

The release process for the Crossplane project is fully documented in the
[`crossplane/release`] repository.

<!-- Named links -->

[Active Development]: #active-development
[Feature Freeze]: #feature-freeze
[Code Freeze]: #code-freeze
[CONTRIBUTING.md]: https://github.com/crossplane/crossplane/blob/main/CONTRIBUTING.md
[community calendar]: https://zoom-lfx.platform.linuxfoundation.org/meetings/crossplane
[`crossplane/release`]: https://github.com/crossplane/release