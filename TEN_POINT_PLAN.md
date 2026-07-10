# 10점 달성 수정 계획

목표 점수: 10 / 10

현재 핵심 감점 원인은 모바일 고유 리스크는 잘 잡았지만 실제 device matrix, store/release evidence, Expo/EAS workflow, mobile accessibility 자동 검증이 약하다는 점입니다.

## 10점 기준

- Expo/React Native CLI 선택 기준이 SDK, native module, build pipeline, release risk까지 포함한다.
- iOS/Android device matrix와 permission/offline/deep link 상태가 review evidence로 남는다.
- release readiness가 signing, build, OTA, rollback, crash reporting, store checklist까지 검증한다.
- mobile review score가 PM `review-score.json`에 안정적으로 반영된다.

## 수정 체크리스트

1. Expo/EAS 기준을 보강한다.
   - Expo SDK 선택 기준
   - managed/prebuild/bare workflow 전환 기준
   - EAS Build, EAS Submit, OTA update, rollback 정책
   - native module risk 기준

2. device matrix를 template에 추가한다.
   - iOS simulator
   - Android emulator
   - 최소 1개 real device 또는 생략 사유
   - OS version, screen size, locale, accessibility setting

3. permission/offline/deep link evidence를 필수화한다.
   - camera/photo/location/notification permission 상태
   - denied/granted/limited 상태
   - offline/poor network/retry/conflict 상태
   - deep link cold start/warm start

4. release checklist validator를 추가한다.
   - 새 파일: `scripts/check_mobile_release.py`
   - `templates/release-checklist.md`가 signing, env, build number, version, crash reporting, OTA policy를 포함하는지 검사한다.

5. mobile accessibility를 강화한다.
   - screen reader label
   - dynamic type/font scaling
   - reduce motion
   - touch target
   - keyboard/safe area

6. review score JSON 예시를 추가한다.
   - `mobile_quality`, `accessibility`, `performance`, `security`, `release_readiness`
   - critical issue와 release blocker를 PM gate가 읽을 수 있게 한다.

## 수정 대상 파일

- `HARNESS_DESIGN.md`
- `README.md`
- `SKILL.md`
- `templates/mobile-plan.md`
- `templates/mobile-review.md`
- `templates/release-checklist.md`
- `templates/mobile-security-checklist.md`
- `policies/mobile-release-policy.md`
- `policies/mobile-accessibility-policy.md`
- `policies/mobile-security-policy.md`
- `scripts/check_mobile_plan.py`
- `scripts/check_mobile_review.py`
- 새 파일: `scripts/check_mobile_release.py`

## 통과 조건

- `python3 -m compileall scripts` 통과
- mobile plan이 Expo/EAS/native module 선택 근거를 포함
- mobile review가 device matrix, permission, offline, accessibility, release evidence를 포함
- release checklist validator가 signing/build/OTA/crash reporting 누락을 실패 처리
