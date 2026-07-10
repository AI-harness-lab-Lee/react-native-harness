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
  - .harness/release-checklist.md
validators:
  - scripts/check_mobile_plan.py
  - scripts/check_mobile_review.py
  - scripts/check_mobile_release.py
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
- EAS Submit, app version/build number, OTA channel/runtimeVersion, rollback 정책 검토
- Expo managed workflow와 Expo prebuild/dev client를 1차 지원 범위로 두고, bare React Native/React Native CLI는 native release risk review 범위로 검토
- iOS simulator, Android emulator, real device 또는 생략 사유, small screen, large screen, dark mode, offline mode를 포함하는 device matrix evidence 검토
- permission, offline/poor network, deep link cold/warm start evidence 검토
- permission prompt, push notification, app icon/splash, store metadata evidence 검토
- web-security-harness와 협력하는 모바일 보안 리뷰
- qa-harness와 협력하는 기기/플랫폼 테스트 리뷰

## 기본 철학

모바일 앱은 웹보다 권한, 저장소, 배포, 네이티브 의존성, 앱스토어 릴리즈 리스크가 큽니다. 따라서 이 하네스는 코드 구조만 보지 않고 권한 요청, local storage, token handling, offline behavior, navigation safety, crash reporting, release checklist까지 함께 검토합니다.

기본 추천은 Expo입니다. Expo를 선택하면 Expo SDK version, managed/prebuild/dev client workflow, EAS Build, EAS Submit, EAS Update channel/runtimeVersion, rollback 정책을 계획에 남깁니다. Expo managed와 prebuild/dev client는 1차 구현/릴리즈 계획 범위이며, bare React Native/React Native CLI는 필요한 네이티브 모듈, 커스텀 빌드 파이프라인, 플랫폼별 native code 요구가 명확할 때 Xcode/Gradle release와 signing ownership까지 문서화하는 review 범위로 다룹니다.

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
scripts/check_mobile_release.py
scripts/smoke_mobile_review_fixtures.py
```

## 산출물과 검증

이 하네스가 담당하는 프로젝트 산출물은 다음 세 개입니다.

- `.harness/mobile-plan.md`: 모바일 앱 목표, 플랫폼, runtime/tooling, architecture, navigation, state management, API, storage, permission, offline behavior, test, release 전략
- `.harness/reports/mobile-review.md`: `mobile_quality`, `accessibility`, `performance`, `security`, `release_readiness` 점수와 critical issue, recommendations, next actions, 검증 결과. 각 점수는 `8.0/10` 이상이어야 하며 8점 미만은 통과할 수 없습니다.
- `.harness/release-checklist.md`: release readiness를 주장하기 전 signing, environment config, app version/build number, crash reporting, OTA/rollback, store submission, device/permission/offline/deep link/accessibility evidence를 기록합니다.

`scripts/check_mobile_review.py`는 `.harness/reports/mobile-review.md`의 정식(canonical) 검증기입니다. 다섯 score category가 모두 `8.0/10` 이상이고, unresolved Critical Issues가 없으며, 실제 build/test/mobile verification과 충분한 모바일 evidence가 있어야 통과합니다.

`scripts/check_mobile_release.py`는 PM registry가 호출하는 통합 entrypoint입니다. 정식 mobile review 검증을 그대로 실행한 뒤 `.harness/release-checklist.md`도 검증하므로, 두 산출물 중 하나라도 실패하면 PM gate를 차단합니다. JSON 결과에는 다섯 score category와 두 required artifact가 포함됩니다. 검증 대상과 JSON 출력은 `--project-root` 내부 경로로 제한되며 검증기는 network 또는 secret source에 접근하지 않습니다.

검증 스크립트는 실제 프로젝트 root에서 실행합니다.

```bash
python3 .harness/harnesses/react-native-harness/scripts/check_mobile_plan.py
python3 .harness/harnesses/react-native-harness/scripts/check_mobile_review.py
python3 .harness/harnesses/react-native-harness/scripts/check_mobile_release.py
```

다른 위치에서 실행할 때는 `--project-root`를 사용합니다.

```bash
python3 scripts/check_mobile_plan.py --project-root /path/to/project
python3 scripts/check_mobile_review.py --project-root /path/to/project
python3 scripts/check_mobile_release.py --project-root /path/to/project
python3 scripts/check_mobile_release.py --project-root /path/to/project --json --output-json /path/to/project/.harness/reports/mobile-release-gate.json
```

정상/실패 경계와 canonical/registry 판정 일치는 고정 fixture smoke로 확인합니다.

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/smoke_mobile_review_fixtures.py
```

## 선택 기준

기본 추천은 Expo입니다. 빠른 MVP, EAS Build, EAS Submit, OTA update, 일반적인 native capability를 안정적으로 가져갈 수 있기 때문입니다. 지원 범위는 `expo-managed`, `expo-prebuild-dev-client`, `react-native-cli` 또는 `bare-react-native`로 나눕니다. Expo managed와 prebuild/dev client는 1차 구현/릴리즈 계획 범위이며, bare React Native는 native module, Xcode/Gradle, signing, store submission 리스크가 명확할 때만 선택합니다. 선택 근거에는 Expo SDK, workflow 전환 기준, native module risk, build pipeline, release risk를 포함해야 합니다.

## 협력 지점

- `web-security-harness`: 공통 인증/인가, API security, privacy threat model을 함께 검토합니다.
- `qa-harness`: iOS/Android device matrix, permission state, offline/online 전환, regression 범위를 함께 검토합니다.
- `designer-harness`: mobile UX flow, touch target, screen reader, dynamic text, 접근성 리스크를 함께 검토합니다.
