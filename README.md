# react-native-harness

React Native 하네스는 모바일 앱 개발을 담당하는 프로젝트별 clone 전문 하네스입니다. 전역 Codex skill로 설치하지 않고, PM 하네스가 모바일 프로젝트에서 필요할 때만 프로젝트 내부로 clone합니다.

PM 하네스가 모바일 프로젝트를 선택하면 이 repo를 프로젝트의 `.harness/harnesses/react-native-harness` 아래로 clone하고, 모바일 팀장 세션은 이 하네스의 `SKILL.md`, `templates/`, `policies/`를 기준으로 계획과 리뷰를 진행합니다.

PM `$setup`에서 `project_type: mobile`과 `mobile: expo` 또는 `mobile: react-native`를 선택하면 이 하네스가 clone 대상에 포함됩니다.

## 역할

```text
role: mobile
triggers:
  - react-native
  - expo
  - mobile
  - ios
  - android
outputs:
  - .harness/mobile-plan.md
  - .harness/reports/mobile-review.md
score_categories:
  - mobile_quality
  - accessibility
  - performance
  - security
  - release_readiness
```

## 책임 범위

- Expo 또는 React Native CLI 선택 기준 정리
- 모바일 앱 구조, navigation, state management, API, storage 전략 수립
- 권한 요청, token handling, local storage, deep link, offline behavior 검토
- iOS/Android 플랫폼별 테스트 계획 작성
- EAS Build, signing, environment config, crash reporting, OTA update policy 검토
- web-security-harness와 협력하는 모바일 보안 리뷰
- qa-harness와 협력하는 기기/플랫폼 테스트 리뷰

## 기본 철학

모바일 앱은 웹보다 권한, 저장소, 배포, 네이티브 의존성, 앱스토어 릴리즈 리스크가 큽니다. 따라서 이 하네스는 코드 구조만 보지 않고 권한 요청, local storage, token handling, offline behavior, navigation safety, crash reporting, release checklist까지 함께 검토합니다.

기본 추천은 Expo입니다. 단, 필요한 네이티브 모듈, 커스텀 빌드 파이프라인, 플랫폼별 native code 요구가 명확하면 React Native CLI를 선택합니다.

## 주요 파일

```text
SKILL.md
HARNESS_DESIGN.md
templates/mobile-plan.md
templates/mobile-review.md
templates/release-checklist.md
templates/mobile-security-checklist.md
policies/mobile-security-policy.md
policies/mobile-release-policy.md
policies/mobile-accessibility-policy.md
policies/mobile-performance-policy.md
scripts/check_mobile_plan.py
scripts/check_mobile_review.py
```

## 산출물과 검증

이 하네스가 담당하는 프로젝트 산출물은 다음 두 개입니다.

- `.harness/mobile-plan.md`: 모바일 앱 목표, 플랫폼, runtime/tooling, architecture, navigation, state management, API, storage, permission, offline behavior, test, release 전략
- `.harness/reports/mobile-review.md`: `mobile_quality`, `accessibility`, `performance`, `security`, `release_readiness` 점수와 critical issue, recommendations, next actions, 검증 결과

검증 스크립트는 실제 프로젝트 root에서 실행합니다.

```bash
python3 .harness/harnesses/react-native-harness/scripts/check_mobile_plan.py
python3 .harness/harnesses/react-native-harness/scripts/check_mobile_review.py
```

다른 위치에서 실행할 때는 `--project-root`를 사용합니다.

```bash
python3 scripts/check_mobile_plan.py --project-root /path/to/project
python3 scripts/check_mobile_review.py --project-root /path/to/project
```

## 선택 기준

기본 추천은 Expo입니다. 빠른 MVP, EAS Build, OTA update, 일반적인 native capability를 안정적으로 가져갈 수 있기 때문입니다. 다만 custom native code, Expo에서 지원하지 않는 native module, 플랫폼별 빌드 제어, 복잡한 native signing 요구가 강하면 React Native CLI를 선택합니다.

## 협력 지점

- `web-security-harness`: 공통 인증/인가, API security, privacy threat model을 함께 검토합니다.
- `qa-harness`: iOS/Android device matrix, permission state, offline/online 전환, regression 범위를 함께 검토합니다.
- `designer-harness`: mobile UX flow, touch target, screen reader, dynamic text, 접근성 리스크를 함께 검토합니다.
