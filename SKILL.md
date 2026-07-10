---
name: react-native-harness
description: Use this specialist harness for React Native, Expo, iOS, Android, mobile app, navigation, storage, permissions, offline behavior, mobile security, and release readiness work. It writes and validates .harness/mobile-plan.md and .harness/reports/mobile-review.md for project-local PM Harness gates.
---

# React Native Harness

## When This Harness Runs

Use this harness when `harness.yaml` includes `react-native-harness`, or when the project mentions React Native, Expo, mobile, iOS, or Android.

Human-facing plans, questions, and reports must be Korean. Machine-facing ids, file names, YAML keys, commands, score category names, and code identifiers remain English.

## First Reads

Before planning, implementing, or reviewing, read the project files that exist from this list:

1. `harness.yaml`
2. `.harness/spec.md`
3. `.harness/architecture.md`
4. `.harness/task-packet.md`
5. `.harness/mobile-plan.md`
6. `.harness/reports/mobile-review.md`
7. `package.json`
8. `app.json` or `app.config.ts`
9. `eas.json`
10. `src/`
11. `app/`
12. `ios/`
13. `android/`

Then read this harness's `HARNESS_DESIGN.md`.
Load only the relevant template or policy file when producing or validating that artifact.

If `app/` exists with Expo Router conventions, inspect routing and deep link behavior there. If `src/` exists, inspect feature, navigation, API, storage, and permission boundaries there. If `ios/` or `android/` exists, treat native signing, permission, entitlement, and build configuration as in scope.

## Core Outputs

- Write or update `.harness/mobile-plan.md` from `templates/mobile-plan.md`; this is the mobile architecture and implementation plan.
- Write or update `.harness/reports/mobile-review.md` from `templates/mobile-review.md`; this is the mobile review report consumed by PM review gates.
- Write or update `.harness/release-checklist.md` from `templates/release-checklist.md` before release readiness is claimed.
- Write `.harness/reports/mobile-release-gate.json` when the PM gate requests machine-readable release status.
- When reviewing, include mobile findings in `.harness/reports/review-score.json` if the PM flow asks for score aggregation.
- Validate `.harness/mobile-plan.md` with `scripts/check_mobile_plan.py` before implementation starts.
- Treat `scripts/check_mobile_review.py` as the canonical validator for `.harness/reports/mobile-review.md`; run it before asking PM to pass the review gate.
- Treat `scripts/check_mobile_release.py` as the PM registry-facing entrypoint. It applies the canonical mobile review decision and also validates `.harness/release-checklist.md`; either artifact can block release readiness.
- For PM gate integration, run `scripts/check_mobile_release.py --project-root . --json --output-json .harness/reports/mobile-release-gate.json`. Keep custom checklist and JSON output paths inside `--project-root`.
- Validators must read project evidence only from `--project-root`; do not add network calls, credential lookup, or secret-source access to validation.
- Run `PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/smoke_mobile_review_fixtures.py` after validator changes to prove canonical/registry parity and score, critical issue, verification, template, and missing-report boundaries.

## Decision Defaults

- Prefer `expo-managed` unless the project needs custom native code, unsupported native modules, strict platform-specific build control, or release constraints that make Expo unsuitable.
- Treat `expo-managed` and `expo-prebuild-dev-client` as the primary supported implementation/release workflows for this harness.
- Treat `react-native-cli` and `bare-react-native` as supported review scopes for native release risk, signing, Xcode/Gradle build, store submission, and migration cost; do not imply bare migration is low-risk.
- For Expo projects, document the Expo SDK version, managed/prebuild/dev client workflow, EAS Build profiles, EAS Submit path, EAS Update channel/runtimeVersion policy, and rollback path.
- Move from managed Expo to prebuild or bare only when native module support, config plugin gaps, native entitlement changes, or build/debugging control justify the release risk.
- Prefer `feature-sliced` or `clean-architecture-lite` for most apps. Use heavier layering only when domain complexity justifies it.
- Prefer `react-query` for server state and `zustand` for small client state.
- Prefer `react-hook-form` plus `zod` for forms that cross an API boundary.
- Store tokens only in `secure-store` or an equivalent secure storage mechanism.
- Use `async-storage` only for non-sensitive preferences or cache.
- Add `sqlite` only when offline-first data, local relational queries, or sync queues are required.
- Every release review must include an iOS simulator, Android emulator, small screen, large screen, dark mode, offline mode, and at least one real device result, or a concrete reason why real-device evidence is unavailable.

## Mobile Review Checklist

Evaluate these score categories:

- `mobile_quality`: architecture fit, navigation safety, component boundaries, platform-specific handling
- `accessibility`: labels, roles, focus flow, touch targets, color contrast, screen reader behavior
- `performance`: avoid unnecessary renders, large lists use virtualization, image sizes, startup cost, offline cache behavior
- `security`: secure storage, deep link validation, permission minimization, PII local storage, token handling
- `release_readiness`: signing, env config, crash reporting, OTA policy, store submission risks

Review evidence must include device matrix coverage, permission states, permission prompt, push notification, offline/poor-network behavior, deep link cold/warm starts, app icon/splash, store metadata, mobile accessibility checks, and release checklist status.

## Required Policies

Use these policy files as review criteria:

- `policies/mobile-security-policy.md`
- `policies/mobile-release-policy.md`
- `policies/mobile-accessibility-policy.md`
- `policies/mobile-performance-policy.md`

## Collaboration

- Defer common web/API security findings to `web-security-harness`, but own mobile-only security risks.
- Defer general regression process to `qa-harness`, but own device, OS, permission, offline, and platform matrix planning.
- If design is in scope, coordinate touch target, mobile flow, and screen reader issues with `designer-harness`.

## Gate Behavior

Block review when any of these are true:

- Token or refresh token is stored in `async-storage` or any non-secure storage.
- PII is stored locally without documented encryption, retention, and deletion policy.
- Deep links route to sensitive, authenticated, or destructive screens without allowlist, auth state, and parameter validation.
- Required permissions are requested without user-facing purpose and denial fallback.
- Production build includes development endpoints, test credentials, or secrets.
- Release path lacks signing ownership, crash reporting, or OTA update policy.
- Release checklist is missing, still a blank template, contains unchecked items, has only checked template text without evidence detail, or lacks version/build number, signing, environment config, crash reporting, OTA/rollback, device matrix, mobile accessibility, release risk, and store submission evidence.
- Mobile review is missing, still a blank template, omits any required score category, has a score below `8.0/10`, contains an unresolved Critical Issue, or lacks actual build/test/mobile verification evidence.
- Critical mobile flow has no test strategy.
