# Mobile Review Fixture

## mobile_quality 점수

mobile_quality: 9.2/10

Feature boundary와 navigation state를 분리했고 API adapter 오류는 화면 상태로 변환한다. React Query cache와 Zustand UI state의 소유권도 분리했다.

## accessibility 점수

accessibility: 9.0/10

Screen reader label, touch target size, contrast, Dynamic Type font scaling, reduced motion, keyboard avoidance, safe area 동작을 점검했다.

## performance 점수

performance: 8.8/10

긴 목록은 virtualization을 사용하고 이미지 크기와 startup render cost를 측정했다. Offline cache 복구와 background 재시도도 확인했다.

## security 점수

security: 9.1/10

Token은 secure storage에만 보관하며 deep link route와 parameter를 allowlist로 검증한다. 민감한 permission은 기능 진입 시점에만 요청한다.

## release_readiness 점수

release_readiness: 9.0/10

Production signing, environment config, crash reporting, OTA update rollback, store submission 소유자와 release checklist를 확인했다.

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

## device matrix

| Platform | Device | Runtime | Screen/state | Result |
| --- | --- | --- | --- | --- |
| iOS | iPhone SE | iOS simulator | small screen, dark mode | pass |
| Android | Pixel 8 | Android emulator | large screen, offline mode | pass |
| iOS | iPhone 15 | real device | production candidate | pass |

Device matrix는 iOS simulator, Android emulator, real device에서 동일한 핵심 여정을 재현했고 locale 변경과 foreground 복귀도 확인했다.

## permission/offline/deep link evidence

- Permission prompt는 기능 사용 직전에 표시되며 camera permission granted, denied, limited 상태마다 fallback 안내를 확인했다.
- Push notification permission 거부 후 설정 이동과 receive/open 흐름을 검증했다.
- Offline mode에서 저장한 변경은 reconnect 뒤 재전송되며 poor network retry와 sync conflict 병합이 안정적으로 끝났다.
- Deep link cold start와 deep link warm start 모두 인증 상태와 잘못된 parameter를 안전하게 처리했다.
- App icon과 splash 화면은 release build에서 확인했고 store metadata와 privacy 문구도 승인본과 일치한다.

## accessibility evidence

VoiceOver와 TalkBack에서 screen reader label과 focus 순서를 확인했다. 모든 주요 control은 touch target size 기준을 충족하며 contrast, Dynamic Type, font scaling, reduced motion, keyboard avoidance, safe area 상태에서도 내용이 잘리지 않는다.

## release evidence

EAS Build production profile과 EAS Submit dry run을 완료했다. iOS/Android signing credential 접근 권한, app version, build number, crash reporting symbol upload를 확인했다. OTA update는 runtimeVersion이 같은 범위에만 배포하고 지표 악화 시 rollback한다. Release checklist에는 artifact와 담당자 evidence가 기록되어 있다.

## 검증 결과

- build: EAS Build production iOS와 Android artifact 생성 성공, build log FL-185-20260710 확인
- test: Jest unit 및 React Native Testing Library interaction suite 128개 성공
- mobile verification: iOS simulator, Android emulator, real device 핵심 여정과 접근성 점검 성공
