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

## 선택한 runtime/tooling

```yaml
runtime_tooling:
```

- 선택 이유:
- native module 요구:
- build/deploy 영향:

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

## offline behavior

- offline에서 가능한 기능:
- sync 대상:
- conflict 처리:
- cache 만료:

## 테스트 전략

- unit:
- component:
- integration:
- e2e:
- device/platform matrix:
- 접근성 검증:
- offline/online 전환 검증:

## 배포 전략

- build:
- iOS signing:
- Android signing:
- environment config:
- crash reporting:
- OTA update policy:
- production secret/dev endpoint 검증:

## 주요 리스크

- 보안:
- 성능:
- 접근성:
- 릴리즈:
- 네이티브 의존성:
