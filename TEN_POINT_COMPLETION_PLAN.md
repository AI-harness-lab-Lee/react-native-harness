# React Native Harness 10점 완성 계획

## 목표

`react-native-harness`를 Expo/React Native 앱 release harness로 완성한다. 10점 기준은 device matrix, release evidence, mobile accessibility, permissions, offline/deep link evidence가 없으면 통과하지 않는 상태다.

## 10점까지 남은 핵심 작업

1. Expo/RN scope를 명확히 고정한다.
   - Expo managed workflow
   - Expo prebuild/dev client
   - bare React Native 지원 범위
   - EAS Build/Submit evidence

2. release validator를 PM gate와 연결한다.
   - `.harness/release-checklist.md`
   - `.harness/device-matrix.md`
   - `.harness/mobile-security-checklist.md`
   - template 그대로 사용 시 실패
   - unchecked checklist가 남으면 실패

3. device matrix evidence를 강화한다.
   - iOS simulator
   - Android emulator
   - at least one physical device 또는 명시적 예외
   - small screen
   - large screen
   - dark mode
   - offline mode

4. mobile accessibility evidence를 필수화한다.
   - screen reader label
   - touch target size
   - dynamic font
   - contrast
   - keyboard avoidance
   - reduced motion

5. release risk evidence를 추가한다.
   - permission prompt
   - push notification
   - deep link
   - app icon/splash
   - crash reporting
   - store metadata

## 삭제/제거 가드레일

사용자 승인 없이 Expo, RN, release, device, accessibility, security 관련 파일이나 체크 항목을 삭제하지 않는다.

삭제 또는 제거가 필요하면 먼저 다음 형식으로 승인 요청을 한다.

```text
삭제 승인 요청
- 대상:
- 이유:
- 영향:
- 대체안:
- 되돌리는 방법:
```

승인 전 금지 작업:

- `rm`, `git rm`, `find -delete`
- Expo evidence 요구사항 삭제
- device matrix 항목 삭제
- release checklist 완화
- mobile accessibility 항목 제거
- permission/security checklist 제거

대신 허용되는 작업:

- unsupported workflow를 planned로 표시
- 별도 harness 후보로 분리
- release evidence를 더 구체화
- validator fixture 추가

## 완료 기준

- `python3 -m compileall react-native-harness/scripts` 통과
- `check_mobile_release.py`가 template release checklist를 실패 처리
- 정상 release fixture 통과
- PM registry에 mobile outputs와 validator가 연결
- Expo/RN scope가 README, SKILL, HARNESS_DESIGN에 일치
