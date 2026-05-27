# React Native Harness Design

## 역할

React Native 하네스는 모바일 앱 개발을 담당하는 전문 하네스입니다. PM 하네스의 기획 산출물과 `harness.yaml`을 읽고, 모바일 앱 구조와 플랫폼 리스크를 기준으로 구현 계획과 리뷰 기준을 만듭니다.

```yaml
id: react-native-harness
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

## 기본 철학

모바일 앱은 웹보다 권한, 저장소, 배포, 네이티브 의존성, 앱스토어 릴리즈 리스크가 큽니다. 따라서 하네스는 코드 구조뿐 아니라 권한 요청, local storage, token handling, offline behavior, navigation safety, crash reporting, release checklist까지 검토해야 합니다.

기본 추천은 Expo 기반 시작입니다. Expo는 빠른 MVP, EAS Build, OTA update, 일반적인 native capability를 안정적으로 다루기 좋습니다. 다만 필수 네이티브 모듈, custom native code, 복잡한 platform-specific build requirement가 명확하면 React Native CLI를 선택합니다.

보안은 `web-security-harness`와 협력하지만, mobile secure storage, biometric permission, deep link validation, certificate pinning, PII local storage 금지 같은 모바일 고유 보안 정책은 이 하네스가 담당합니다.

QA는 `qa-harness`와 협력하지만, iOS/Android, simulator/device, OS version, permission state, offline/online 전환 같은 기기/플랫폼 테스트 계획은 이 하네스가 담당합니다.

## 선택지

### runtime/tooling

- `expo`: 기본 추천. MVP, 일반적인 앱, EAS Build, OTA update를 빠르게 가져갈 때 선택합니다.
- `react-native-cli`: native module 요구가 강하거나, 플랫폼별 native code와 custom build 제어가 중요한 경우 선택합니다.

### architecture

- `feature-sliced`: feature 단위로 화면, API, state, model을 묶어 확장성을 확보합니다.
- `layered`: app, presentation, domain, data 계층을 분리해 팀 협업과 테스트 경계를 명확히 합니다.
- `clean-architecture-lite`: 과도한 계층화를 피하면서 domain/data/presentation 경계를 둡니다.

### navigation

- `react-navigation`: React Native 표준 navigation 선택지입니다.
- `expo-router`: Expo 기반 파일 라우팅과 deep link 흐름이 중요할 때 선택합니다.

### state management

- `react-query`: 서버 상태, cache, loading/error, retry를 담당합니다.
- `zustand`: 작은 클라이언트 상태를 단순하게 관리합니다.
- `redux-toolkit`: 복잡한 전역 상태, audit 가능한 action 흐름, 기존 Redux 팀 역량이 있을 때 선택합니다.

### forms/validation

- `react-hook-form`: 모바일 입력 성능과 form state 관리를 위해 기본 선택합니다.
- `zod`: API boundary와 form validation schema를 공유할 때 사용합니다.

### storage

- `secure-store`: token, refresh token, 민감한 credential 저장에 사용합니다.
- `async-storage`: 민감하지 않은 preference/cache에만 사용합니다.
- `sqlite`: offline-first, local relational data, sync queue가 필요할 때 사용합니다.

### API

- `REST`: 기본 추천. 명확한 resource API와 mobile client cache 전략을 결합합니다.
- `GraphQL`: 화면별 데이터 조합이 복잡하거나 schema 기반 client generation이 중요한 경우 선택합니다.

### testing

- `jest`: 순수 로직, hook, state, API adapter 테스트에 사용합니다.
- `react-native-testing-library`: component interaction, accessibility label, loading/error state 검증에 사용합니다.
- `detox` 또는 `e2e later`: release risk가 커지면 주요 사용자 여정에 E2E를 추가합니다.

### mobile security

- token은 secure storage에 저장하고 async storage에 저장하지 않습니다.
- biometric permission은 명확한 사용자 동의와 fallback을 둡니다.
- deep link는 allowlist, auth state, route parameter validation을 거칩니다.
- certificate pinning은 threat model과 운영 비용을 비교해 결정합니다.
- PII local storage는 기본 금지이며, 예외는 암호화, 만료, 삭제 정책을 문서화해야 합니다.

### release

- `EAS Build`: Expo 기반 release pipeline의 기본값입니다.
- `iOS/Android signing`: signing key, provisioning, keystore 접근 권한을 분리합니다.
- `environment config`: dev/staging/prod config와 secret 주입 경계를 분리합니다.
- `crash reporting`: Sentry, Firebase Crashlytics 등 하나를 선택해 release 전 검증합니다.
- `OTA update policy`: update 가능 범위, rollback 조건, native binary mismatch 기준을 정합니다.

## 산출물

- `.harness/mobile-plan.md`: 모바일 설계와 개발 전략
- `.harness/reports/mobile-review.md`: 모바일 전문 리뷰 결과
- `.harness/reports/review-score.json`: PM review gate가 읽는 점수 자료에 mobile category 반영

## 협업 모델

- PM 하네스: 프로젝트 목적, MVP 범위, 팀 구성, gate 기준 확정
- React Native 하네스: 모바일 구조, 플랫폼 리스크, 릴리즈 준비도 검토
- web-security-harness: 공통 인증/인가, API security, privacy threat 검토
- qa-harness: acceptance criteria, regression, E2E coverage 검토
- designer-harness: mobile UX flow, accessibility, touch target, responsive state 검토
