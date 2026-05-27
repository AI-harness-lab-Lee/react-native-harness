---
name: react-native-harness
description: Use this specialist harness for React Native, Expo, iOS, Android, or mobile app projects. It plans mobile architecture, storage, navigation, permissions, offline behavior, testing, security, and release readiness, then produces mobile plan and review reports for PM Harness gates.
---

# React Native Harness

## When This Harness Runs

Use this harness when `harness.yaml` includes `react-native-harness`, or when the project mentions React Native, Expo, mobile, iOS, or Android.

Human-facing plans, questions, and reports must be Korean. Machine-facing ids, file names, YAML keys, commands, score category names, and code identifiers remain English.

## First Reads

1. Read `harness.yaml`.
2. Read `.harness/spec.md`, `.harness/architecture.md`, and `.harness/task-packet.md` if present.
3. Read this harness's `HARNESS_DESIGN.md`.
4. Load only the relevant template or policy file when producing that artifact.

## Core Outputs

- Write or update `.harness/mobile-plan.md` from `templates/mobile-plan.md`.
- Write or update `.harness/reports/mobile-review.md` from `templates/mobile-review.md`.
- When reviewing, include mobile findings in `.harness/reports/review-score.json` if the PM flow asks for score aggregation.

## Decision Defaults

- Prefer `expo` unless the project needs custom native code, unsupported native modules, or strict platform-specific build control.
- Prefer `feature-sliced` or `clean-architecture-lite` for most apps. Use heavier layering only when domain complexity justifies it.
- Prefer `react-query` for server state and `zustand` for small client state.
- Prefer `react-hook-form` plus `zod` for forms that cross an API boundary.
- Store tokens only in `secure-store` or an equivalent secure storage mechanism.
- Use `async-storage` only for non-sensitive preferences or cache.
- Add `sqlite` only when offline-first data, local relational queries, or sync queues are required.

## Mobile Review Checklist

Evaluate these score categories:

- `mobile_quality`: architecture fit, navigation safety, component boundaries, platform-specific handling
- `accessibility`: labels, roles, focus flow, touch targets, color contrast, screen reader behavior
- `performance`: avoid unnecessary renders, large lists use virtualization, image sizes, startup cost, offline cache behavior
- `security`: secure storage, deep link validation, permission minimization, PII local storage, token handling
- `release_readiness`: signing, env config, crash reporting, OTA policy, store submission risks

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

- Token or refresh token is stored in non-secure storage.
- PII is stored locally without documented encryption, retention, and deletion policy.
- Deep links route to authenticated or destructive screens without validation.
- Required permissions are requested without user-facing purpose and fallback path.
- Release path lacks signing ownership, environment separation, or crash reporting plan.
- Critical mobile flow has no test strategy.
