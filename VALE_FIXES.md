# Vale Fixes Tracking

This document tracks Vale linting issues in the Crossplane documentation and progress on fixing them.

## Summary

**Last Updated:** 2025-11-20

**High Priority Fixes Completed:**
- ✅ Sentence Length violations (gitlab.SentenceLength & Microsoft.SentenceLength)
- ✅ Passive Voice violations (Microsoft.Passive & Google.Passive) - 28 instances
- ✅ Vale configuration improvements (added technical acronym exceptions)
- ✅ Wordy phrases (gitlab.Wordy) - 17 instances
- ✅ Future tense (gitlab.FutureTense) - 2 instances
- ✅ Complex words (Microsoft.ComplexWords) - 199 instances → 0
- ✅ Acronym exceptions (Microsoft.Acronyms & Google.Acronyms) - 300+ violations → 107 (cloud-native exceptions)

**Current Vale Status:**
- **Errors:** 0
- **Warnings:** 12
- **Suggestions:** 608 (reduced from ~1002)

**Total Files Modified:** 45+ files across master content directory

**Commits:**
- 6cc8539 - Fix long sentence Vale violations for improved readability
- b313f53 - Fix passive voice Vale violations for active, direct writing
- d5b25c0 - Improve sentence clarity and update Vale configuration
- e479210 - Fix gitlab.Wordy Vale violations for clearer documentation
- d9e954f - Fix gitlab.FutureTense Vale violations for present tense
- 18cf004 - Improve readability with simpler word choices
- 9c90104 - Fix all remaining ComplexWords violations

## Completed Fixes

### ✅ Sentence Length (gitlab.SentenceLength & Microsoft.SentenceLength)
**Status:** Fixed
**Commits:**
- 6cc8539 - "Fix long sentence Vale violations for improved readability"
- d5b25c0 - "Improve sentence clarity and update Vale configuration"

**Files Fixed (16 files total):**
- `content/master/composition/environment-configs.md`
- `content/master/composition/composite-resource-definitions.md`
- `content/master/packages/image-configs.md`
- `content/master/cli/command-reference.md`
- `content/master/composition/composition-revisions.md`
- `content/master/composition/compositions.md`
- `content/master/guides/change-logs.md`
- `content/master/guides/crossplane-with-argo-cd.md`
- `content/master/guides/extensions-release-process.md`
- `content/master/guides/function-patch-and-transform.md`
- `content/master/guides/install-from-source.md`
- `content/master/guides/metrics.md`
- `content/master/guides/troubleshoot-crossplane.md`
- `content/master/guides/write-a-composition-function-in-go.md`
- `content/master/guides/write-a-composition-function-in-python.md`
- `content/master/learn/release-cycle.md`
- `content/master/managed-resources/managed-resource-activation-policies.md`
- `content/master/managed-resources/managed-resources.md`
- `content/master/packages/configurations.md`
- `content/master/whats-crossplane/_index.md`
- `content/master/whats-new/_index.md`

**Description:** Broke sentences over 25 words into shorter, clearer sentences to meet style guide requirements and improve readability.

### ✅ Passive Voice (Microsoft.Passive & Google.Passive)
**Status:** Fixed - All violations resolved (28 instances)
**Commit:** b313f53 - "Fix passive voice Vale violations for active, direct writing"

**Files Fixed (10 files):**
- `content/master/composition/composite-resource-definitions.md`
- `content/master/composition/compositions.md`
- `content/master/guides/install-from-source.md`
- `content/master/guides/pods.md`
- `content/master/learn/community-extension-projects.md`
- `content/master/learn/release-cycle.md`
- `content/master/managed-resources/usages.md`
- `content/master/packages/image-configs.md`
- `content/master/managed-resources/managed-resources.md`
- `content/master/packages/providers.md`

**Description:** Converted 28 instances of passive voice to active voice. Active voice makes documentation clearer, more direct, and easier to understand. This aligns with the Crossplane style guide principle to "use active voice."

**Examples of fixes:**
- "are required" → "require values"
- "is written" → "uses"
- "was built" → "from the previous steps"
- "be provided" → "you must provide"
- "is unsupported" → "doesn't support"
- "is archived" → "maintainers archive"
- "been approved" → "a maintainer approves"

### ✅ Vale Configuration Updates
**Status:** Completed
**Commit:** d5b25c0 - "Improve sentence clarity and update Vale configuration"

**Changes:**
- Disabled `write-good.E-Prime` rule (too pedantic for technical documentation)
- Added common technical acronyms to exception lists: AWS, CNCF, DNS, KCL, RBAC, TLS, VPC
- Added AWS to Crossplane provider words list

**Description:** Reduced false positive Vale warnings for legitimate technical terminology commonly used in Kubernetes and cloud-native documentation.

### ✅ Wordy Phrases (gitlab.Wordy)
**Status:** Fixed - All violations resolved (17 instances)
**Commit:** e479210 - "Fix gitlab.Wordy Vale violations for clearer documentation"

**Files Fixed (9 files):**
- `content/master/composition/environment-configs.md`
- `content/master/guides/install-from-source.md`
- `content/master/guides/metrics.md`
- `content/master/guides/troubleshoot-crossplane.md`
- `content/master/learn/_index.md`
- `content/master/packages/configurations.md`
- `content/master/packages/image-configs.md`
- `content/master/packages/providers.md`
- `content/master/whats-new/_index.md`

**Description:** Removed wordy phrases to improve clarity and directness. This makes documentation more concise and easier to understand.

**Examples of fixes:**
- "respectively" → listed each option explicitly
- "Please note that" → removed "Please" and "note that"
- "Note that" → removed redundant phrase
- "Please see" → "See"

**Types of changes (17 total):**
- Removed "respectively" and listed options explicitly (2 instances)
- Removed unnecessary "please" (7 instances)
- Removed redundant "note that" phrases (8 instances)

### ✅ Future Tense (gitlab.FutureTense)
**Status:** Fixed - All violations resolved (2 instances)
**Commit:** d9e954f - "Fix gitlab.FutureTense Vale violations for present tense"

**Files Fixed (2 files):**
- `content/master/guides/write-a-composition-function-in-go.md`
- `content/master/guides/write-a-composition-function-in-python.md`

**Description:** Converted future tense to present tense. Present tense makes documentation more direct and actionable, aligning with the Crossplane style guide principle to use present tense.

**Example of fix:**
- "will lint, test, and build" → "lints, tests, and builds"

### ✅ Complex Words (Microsoft.ComplexWords)
**Status:** Fixed - All violations resolved (199 instances → 0)
**Commits:**
- 18cf004 - "Improve readability with simpler word choices"
- 9c90104 - "Fix all remaining ComplexWords violations"

**Files Fixed (20 files):**
- `content/master/cli/command-reference.md`
- `content/master/composition/composite-resource-definitions.md`
- `content/master/composition/composition-revisions.md`
- `content/master/composition/compositions.md`
- `content/master/get-started/get-started-with-operations.md`
- `content/master/guides/change-logs.md`
- `content/master/guides/extensions-release-process.md`
- `content/master/guides/function-patch-and-transform.md`
- `content/master/guides/install-from-source.md`
- `content/master/guides/pods.md`
- `content/master/guides/troubleshoot-crossplane.md`
- `content/master/guides/upgrade-to-crossplane-v2.md`
- `content/master/guides/write-a-composition-function-in-go.md`
- `content/master/guides/write-a-composition-function-in-python.md`
- `content/master/learn/release-cycle.md`
- `content/master/managed-resources/managed-resource-definitions.md`
- `content/master/managed-resources/managed-resources.md`
- `content/master/managed-resources/usages.md`
- `content/master/operations/cronoperation.md`
- `content/master/operations/operation.md`
- `content/master/operations/watchoperation.md`
- `content/master/packages/image-configs.md`
- `content/master/whats-crossplane/_index.md`

**Description:** Replaced complex words with simpler alternatives while preserving technical accuracy. Added technical term exceptions for words appropriate in Crossplane documentation.

**Technical Term Exceptions Added (6 terms, 91 instances preserved):**
- `provide` - technical standard (provide credentials, provide configuration)
- `multiple` - technical standard (multiple resources, multiple instances)
- `maintain` - technical standard (maintain software, maintain compatibility)
- `aggregate` - Kubernetes technical term (ClusterRole aggregation)
- `component` - technical term (software component, system component)
- `address` - technical term (IP address, memory address)

**Word Simplifications Applied (108 instances):**
- `approximate` → `about` (1 instance)
- `incorrect` → `wrong` (1 instance)
- `numerous` → `many` (1 instance)
- `concept` → `idea` (1 instance)
- `accomplish` → `do` (1 instance)
- `encounter` → `meet` (1 instance)
- `frequently` → `often` (7 instances)
- `identical` → `same` (7 instances)
- `previous` → `earlier` (10 instances)
- `attempt` → `try` (2 instances)
- `accordingly` → removed as redundant (2 instances)
- `determine` → `decide`/`find` (16 instances)
- `contains` → `has` (27 instances)
- `Monitor` → `Watch` (3 heading instances)
- `address` (non-technical) → `fix`/`solve` (4 instances)

**Configuration Changes:**
- Disabled generic `Microsoft.ComplexWords` rule
- Created custom `Crossplane.ComplexWords.yml` with technical term exceptions
- Updated `.vale.ini` to use custom rule

## Remaining Issues by Category

Analysis run on all `content/master/**/*.md` files.

### 1. ✅ Microsoft.ComplexWords - COMPLETED
**Status:** All 199 violations fixed
**Description:** Replaced complex words with simpler alternatives while preserving technical accuracy.

See "Complex Words" section above for complete details.

### 2. ✅ Acronym Exceptions (Microsoft.Acronyms & Google.Acronyms)
**Status:** Cloud-native exceptions added - 300+ violations → 107
**Commits:** (current work, not yet committed)

**Strategy:**
Created custom `Crossplane.Acronyms.yml` rule to replace Microsoft and Google acronym rules. This allows cloud-native and technical acronyms well-known to Kubernetes audiences to be excepted, while keeping Crossplane-specific acronyms subject to definition requirements.

**Important Design Decision:**
Crossplane-specific acronyms (XRD, CRD, MRD, MRAP, XPKG, CEL) are **intentionally NOT excepted** - they should be properly defined in documentation for readers new to Crossplane.

**Cloud-Native/Technical Acronyms Added to Exceptions (23 terms, 192 violations resolved):**
- **Cloud providers:** GCP (Google Cloud Platform), GKE (Google Kubernetes Engine), RDS (Relational Database Service), IAM (Identity and Access Management), GHCR (GitHub Container Registry)
- **Container standards:** OCI (Open Container Initiative)
- **Authentication:** OIDC (OpenID Connect)
- **Networking/Time:** TTL (Time To Live), UTC (Coordinated Universal Time), DST (Daylight Saving Time)
- **Web standards:** REST (Representational State Transfer), RPC (Remote Procedure Call)
- **Security/Hashing:** SHA (Secure Hash Algorithm)
- **Operations:** SLA (Service Level Agreement), QPS (Queries Per Second), EOL (End of Life)
- **Configuration languages:** CUE (CUE configuration language)
- **Special cases:** NOTES (Helm chart NOTES section)

**Crossplane Acronyms Still Requiring Definitions (107 violations remain):**
- XRD (23) - CompositeResourceDefinition
- CRD (30) - CustomResourceDefinition
- MRD (30) - ManagedResourceDefinition
- MRAP (20) - ManagedResourceActivationPolicy
- XPKG (1) - Crossplane package format
- CEL (3) - Common Expression Language

**Configuration Changes:**
- Created `utils/vale/styles/Crossplane/Acronyms.yml` with cloud-native exceptions
- Disabled `Microsoft.Acronyms` and `Google.Acronyms` in `.vale.ini`
- Custom rule uses same validation logic but with expanded exception list

**Result:** Reduced false positive acronym suggestions by 192 (from ~300 to 107) while preserving requirement to define Crossplane-specific terms.

### 3. ~~Acronym Issues~~ (SUPERSEDED - See section 2 above)
**Status:** Addressed with custom Crossplane.Acronyms rule
**Previously:** ~150 occurrences each (Microsoft.Acronyms & Google.Acronyms)
**Now:** 107 violations for Crossplane-specific acronyms only (intentionally kept)

### 4. Google.Parens - 125 occurrences
**Priority:** Low
**Description:** Excessive or improper use of parentheses.

**Guideline:** Use parentheses judiciously.

### 5. gitlab.Uppercase - 116 occurrences
**Priority:** Low
**Description:** Inappropriate uppercase usage.

**Note:** Often triggered by legitimate technical terms (NOTES, YAML, etc.). May need exception list updates.

### 6. Microsoft.Vocab - 106 occurrences
**Priority:** Low
**Description:** Words to verify against Microsoft A-Z word list.

Common words flagged:
- "allow/allows"
- "beta"
- "as well as"

### 7. Microsoft.Headings - 98 occurrences
**Priority:** Low
**Description:** Heading capitalization issues (should use sentence-style capitalization).

**Note:** Many are legitimate code/technical terms in headings (e.g., "xpkg build", "beta convert").

### 8. gitlab.ReadingLevel - 46 occurrences
**Priority:** Low
**Description:** Content exceeds 8th grade reading level.

**Note:** This is an aggregate metric affected by sentence length and word complexity. May improve as other issues are fixed.

### 9. Other Issues - <10 occurrences each
- Microsoft.Accessibility (5) - Accessibility issues
- write-good.TooWordy (3) - Wordy expressions
- Google.Colons (3) - Colon usage
- gitlab.UnclearAntecedent (3) - Unclear pronoun references
- Microsoft.Semicolon (2) - Semicolon usage
- Google.Semicolons (2) - Semicolon usage
- write-good.Weasel (1) - Weasel words
- Microsoft.OxfordComma (1) - Oxford comma usage
- Google.WordList (1) - Word list violation

## Recommended Fix Order

1. ✅ **Sentence Length** (COMPLETED - 6cc8539, d5b25c0)
2. ✅ **Passive Voice** (COMPLETED - b313f53) - 28 instances fixed
3. ✅ **Vale Configuration** (COMPLETED - d5b25c0) - Added acronym exceptions
4. ✅ **gitlab.Wordy** (COMPLETED - e479210) - 17 instances fixed
5. ✅ **gitlab.FutureTense** (COMPLETED - d9e954f) - 2 instances fixed
6. ✅ **Microsoft.ComplexWords** (COMPLETED - 18cf004, 9c90104) - 199 instances fixed
7. ✅ **Acronym exceptions** (COMPLETED - current work) - 300+ violations → 107
8. 🎯 Review and update exception lists for uppercase terms and vocab (ongoing)

## Notes

- **Zero errors** - All Vale errors have been resolved ✅
- **Warnings reduced** - From 0 to 12 (need investigation)
- Current remaining issues are primarily **suggestions** (608, down from ~1002)
- Many technical terms have been added to exception lists to preserve accuracy
- Custom Crossplane.ComplexWords rule balances readability with technical precision
- Custom Crossplane.Acronyms rule preserves Crossplane-specific acronym requirements while excepting cloud-native terms
- **Progress:** All major readability improvements completed
  - Sentence length ✅
  - Passive voice ✅
  - Wordy phrases ✅
  - Future tense ✅
  - Complex words ✅
  - Cloud-native acronym exceptions ✅
- **Next Steps:** Review and update exception lists for uppercase terms and vocab to further reduce false positives
