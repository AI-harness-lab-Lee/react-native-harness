# Mobile Plan

이 문서는 실제 프로젝트 내용을 기준으로 작성합니다. 빈 항목, placeholder, "추후 작성" 상태로는 모바일 계획 검증을 통과할 수 없습니다.

## 앱 목표

- 목적:
- 핵심 사용자:
- MVP 범위:

## 대상 플랫폼

- iOS:
- Android:
- 최소 OS version:
- 지원 기기:
- 지원 locale:
- 접근성 설정 범위:

## 선택한 runtime/tooling

```yaml
runtime_tooling: expo-managed | expo-prebuild-dev-client | react-native-cli | bare-react-native
expo_sdk:
workflow: managed | prebuild-dev-client | bare | react-native-cli
eas_build:
eas_submit:
ota_updates:
```

- 선택 이유:
- Expo SDK 선택 기준:
- managed/prebuild-dev-client/bare 또는 React Native CLI 전환 기준:
- native module 요구:
- native module risk:
- build/deploy 영향:
- release risk:

## 선택한 architecture

```yaml
architecture:
```

- 폴더 구조:
- feature 경계:
- domain/data/presentation 경계:

## navigation 전략

```yaml
navigation:
```

- 주요 stack/tab 구조:
- deep link 정책:
- deep link cold start evidence:
- deep link warm start evidence:
- 인증 상태별 route guard:
- 뒤로가기/복귀 흐름:

## state management 전략

```yaml
state_management:
```

- server state:
- client state:
- cache/retry 정책:

## API 연동 전략

```yaml
api:
```

- API protocol:
- auth header/token refresh:
- error format:
- timeout/retry:

## storage 전략

```yaml
storage:
```

- secure storage 대상:
- async storage 대상:
- sqlite 사용 여부:
- PII local storage 정책:

## 권한 요청 계획

- 필요한 권한:
- 요청 시점:
- 사용자 설명:
- 거부 시 fallback:
- OS permission string:
- permission evidence:
  - camera/photo:
  - location:
  - notification:
  - denied:
  - granted:
  - limited:

## offline behavior

- offline에서 가능한 기능:
- poor network/retry:
- sync 대상:
- conflict 처리:
- cache 만료:
- offline evidence:

## 테스트 전략

- unit:
- component:
- integration:
- e2e:
- device matrix:
  | Platform | Device | Simulator/Emulator/Real | OS version | Screen size | Locale | Accessibility setting | Mode | Evidence |
  | --- | --- | --- | --- | --- | --- | --- | --- | --- |
  | iOS |  | iOS simulator |  | small screen |  |  | light/dark mode |  |
  | Android |  | Android emulator |  | large screen |  |  | offline mode |  |
  | iOS/Android |  | real device 또는 생략 사유 |  |  |  |  |  |  |
- 접근성 검증:
- screen reader label 검증:
- dynamic type/font scaling 검증:
- reduced motion 검증:
- touch target size 검증:
- contrast 검증:
- keyboard avoidance/safe area 검증:
- offline/online 전환 검증:
- permission/deep link 검증:

## 배포 전략

- EAS Build/native build:
- EAS Submit/store submit:
- app version/build number:
- iOS signing:
- Android signing:
- environment config:
- crash reporting:
- source map/symbol upload:
- OTA update policy:
- rollback policy:
- release checklist:
- permission prompt/push notification evidence:
- app icon/splash evidence:
- store metadata evidence:
- production secret/dev endpoint 검증:

## 주요 리스크

- 보안:
- 성능:
- 접근성:
- 릴리즈:
- 네이티브 의존성:
