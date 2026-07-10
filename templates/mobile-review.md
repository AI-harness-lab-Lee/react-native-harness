# Mobile Review

이 문서는 실제 구현과 검증 결과를 기준으로 작성합니다. 빈 템플릿, 0/10 점수, 8점 미만 점수, unresolved critical issue, 비어 있는 검증 결과는 review gate를 통과할 수 없습니다.

## mobile_quality 점수

mobile_quality: 0/10

- 근거:

## accessibility 점수

accessibility: 0/10

- 근거:

## performance 점수

performance: 0/10

- 근거:

## security 점수

security: 0/10

- 근거:

## release_readiness 점수

release_readiness: 0/10

- 근거:

## Critical Issues

- 없음

## High Issues

| Issue | Severity | Status | Decision |
| --- | --- | --- | --- |
| none | none | resolved | proceed |

## Release Blockers

| Blocker | Status | Release Blocker | Decision |
| --- | --- | --- | --- |
| none | resolved | no | proceed |

## mobile_quality

- 구조:
- navigation:
- state/API 경계:
- 플랫폼별 처리:

## accessibility

- screen reader:
- screen reader label:
- touch target size:
- label/role:
- contrast:
- dynamic type/font scaling:
- reduced motion:
- keyboard avoidance/safe area:

## performance

- render cost:
- list virtualization:
- image/resource:
- startup:
- offline/cache:

## security

- token secure storage:
- biometric permission:
- permission evidence:
  - camera/photo:
  - location:
  - notification:
  - denied/granted/limited:
- deep link validation:
- deep link cold start:
- deep link warm start:
- certificate pinning:
- PII local storage:

## release_readiness

- EAS Build/native build:
- EAS Submit/store submit:
- iOS/Android signing:
- environment config:
- app version/build number:
- crash reporting:
- source map/symbol upload:
- OTA update policy:
- rollback policy:
- release checklist:

## device matrix

| Platform | Device | Simulator/Emulator/Real | OS version | Screen size | Locale | Accessibility setting | Result | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| iOS |  | iOS simulator |  | small screen |  | dark mode |  |  |
| Android |  | Android emulator |  | large screen |  | offline mode |  |  |
| iOS/Android |  | real device 또는 생략 사유 |  |  |  |  |  |  |

## permission/offline/deep link evidence

- permission granted:
- permission denied:
- permission limited:
- permission prompt:
- push notification:
- offline:
- offline mode:
- poor network/retry:
- sync conflict:
- deep link cold start:
- deep link warm start:
- app icon/splash:
- store metadata:

## review-score.json 예시

```json
{
  "mobile_quality": 8.5,
  "accessibility": 8.0,
  "performance": 8.2,
  "security": 8.7,
  "release_readiness": 8.1,
  "critical_issues": [],
  "high_issues": [],
  "release_blockers": [],
  "release_ready": true,
  "evidence": {
    "device_matrix": ".harness/reports/mobile-review.md#device-matrix",
    "release_checklist": ".harness/release-checklist.md"
  }
}
```

## recommendations

-

## next actions

-

## 검증 결과

- build:
- test:
- mobile verification:
- device matrix:
- permission/offline/deep link:
- release checklist:
- 남은 검증:
