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

**Current Vale Status:**
- **Errors:** 0
- **Warnings:** 0
- **Suggestions:** ~1000

**Total Files Modified:** 25+ files across master content directory

**Commits:**
- 6cc8539 - Fix long sentence Vale violations for improved readability
- b313f53 - Fix passive voice Vale violations for active, direct writing
- d5b25c0 - Improve sentence clarity and update Vale configuration
- e479210 - Fix gitlab.Wordy Vale violations for clearer documentation
- d9e954f - Fix gitlab.FutureTense Vale violations for present tense

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

## Remaining Issues by Category

Analysis run on all `content/master/**/*.md` files.

### 1. Microsoft.ComplexWords - 195 occurrences
**Priority:** Medium
**Description:** Suggests simpler word alternatives for better readability.

Common suggestions:
- "provide" → "give" or "offer"
- "multiple" → "many"
- "contains" → "has"
- "determine" → "decide" or "find"

**Impact:** Improves clarity and readability for broader audience.

### 2. Acronym Issues - 151 occurrences each
**Rules:** Microsoft.Acronyms & Google.Acronyms
**Priority:** Low
**Description:** Missing definitions or explanations for acronyms.

Common acronyms flagged:
- OCI
- XPKG
- XRD
- YAML
- API

**Note:** Many of these are technical acronyms well-known to the Kubernetes/cloud-native audience. May need to add to exception list rather than spell out every occurrence.

### 3. Google.Parens - 125 occurrences
**Priority:** Low
**Description:** Excessive or improper use of parentheses.

**Guideline:** Use parentheses judiciously.

### 4. gitlab.Uppercase - 116 occurrences
**Priority:** Low
**Description:** Inappropriate uppercase usage.

**Note:** Often triggered by legitimate technical terms (NOTES, YAML, etc.). May need exception list updates.

### 5. Microsoft.Vocab - 106 occurrences
**Priority:** Low
**Description:** Words to verify against Microsoft A-Z word list.

Common words flagged:
- "allow/allows"
- "beta"
- "as well as"

### 6. Microsoft.Headings - 98 occurrences
**Priority:** Low
**Description:** Heading capitalization issues (should use sentence-style capitalization).

**Note:** Many are legitimate code/technical terms in headings (e.g., "xpkg build", "beta convert").

### 7. gitlab.ReadingLevel - 46 occurrences
**Priority:** Low
**Description:** Content exceeds 8th grade reading level.

**Note:** This is an aggregate metric affected by sentence length and word complexity. May improve as other issues are fixed.

### 8. Other Issues - <10 occurrences each
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
6. 🎯 **Microsoft.ComplexWords** (NEXT) - 195 occurrences (larger effort, consider priority)
7. Review and update exception lists for acronyms, uppercase terms, and vocab (ongoing)

## Notes

- **Zero errors** - All Vale errors have been resolved ✅
- **Zero warnings** - All Vale warnings have been resolved ✅
- Current remaining issues are primarily **suggestions** (~1000)
- Many technical terms may need to be added to exception lists rather than changed
- Some rules may conflict with technical accuracy (e.g., changing technical terms to simpler words may reduce precision)
- **Progress:** All high-impact readability improvements completed (sentence length, passive voice, wordy phrases, future tense)
- **Next Steps:** Consider addressing complex words (195 occurrences) or exception list updates for acronyms and technical terms
