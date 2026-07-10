# Mobile Release Checklist Fixture

## build

- [x] release build가 local 또는 CI에서 성공했다.
- [x] iOS와 Android build artifact가 분리되어 관리된다.
- [x] Expo 프로젝트는 EAS Build profile(dev/staging/prod)과 runtimeVersion/channel 정책이 문서화되어 있다.
- [x] React Native CLI 프로젝트는 Xcode archive와 Gradle assemble/bundle release 절차가 문서화되어 있다.
- [x] app version과 iOS build number, Android versionCode가 release tag와 일치한다.
- [x] dev/staging/prod environment config가 분리되어 있다.
- [x] secret이 repository에 저장되지 않는다.
- [x] production build에 dev endpoint, test credential, secret이 포함되지 않는 것을 확인했다.

Build evidence: 2026-07-10 EAS Build production profile로 iOS와 Android release build를 완료했고 CI artifact FL-185를 보존했다.
Version evidence: app version 1.4.0, iOS build number 140, Android versionCode 140이 release tag v1.4.0과 일치한다.
Environment evidence: dev/staging/prod environment config는 CI secret scope로 분리했고 production build에 개발 endpoint가 없음을 검사했다.

## signing

- [x] iOS certificate/provisioning profile 소유자와 갱신 절차가 정해져 있다.
- [x] Android keystore 소유자와 backup 절차가 정해져 있다.
- [x] signing credential 접근 권한이 최소화되어 있다.

Signing evidence: mobile release owner가 iOS certificate와 provisioning 갱신을 담당하고 Android keystore backup 복구 훈련을 완료했다.

## crash reporting

- [x] crash reporting SDK가 설정되어 있다.
- [x] release build에서 crash report 수집이 검증되었다.
- [x] source map 또는 symbol upload 절차가 있다.
- [x] crash report에서 token, email, phone, address 등 민감 정보가 필터링된다.

Crash evidence: production crash reporting smoke event를 수집했고 source map과 iOS symbol upload 상태 및 개인정보 필터를 확인했다.

## OTA update policy

- [x] OTA update 가능 범위가 문서화되어 있다.
- [x] EAS Update channel/branch와 native runtimeVersion 호환 기준이 정해져 있다.
- [x] native binary 변경이 필요한 update 기준이 문서화되어 있다.
- [x] rollback 조건과 절차가 정해져 있다.
- [x] OTA update를 끄거나 중단해야 하는 조건이 정해져 있다.

OTA evidence: EAS Update production channel은 동일 runtimeVersion JavaScript 변경에만 사용하며 crash 지표가 기준을 넘으면 rollback한다.

## release evidence

- [x] iOS simulator evidence가 첨부되었다.
- [x] Android emulator evidence가 첨부되었다.
- [x] 최소 1개 real device evidence 또는 생략 사유가 첨부되었다.
- [x] small screen evidence가 첨부되었다.
- [x] large screen evidence가 첨부되었다.
- [x] dark mode evidence가 첨부되었다.
- [x] offline mode evidence가 첨부되었다.
- [x] permission prompt copy와 fallback evidence가 첨부되었다.
- [x] push notification permission/receive/open evidence 또는 명시적 비사용 사유가 첨부되었다.
- [x] camera/photo/location/notification permission의 denied/granted/limited 상태 evidence가 첨부되었다.
- [x] offline, poor network/retry, sync conflict evidence가 첨부되었다.
- [x] deep link cold start와 warm start evidence가 첨부되었다.
- [x] screen reader label, touch target size, dynamic type/font scaling, contrast, keyboard avoidance, safe area evidence가 첨부되었다.
- [x] reduced motion evidence가 첨부되었다.

Device evidence: iPhone SE iOS simulator small screen과 Pixel 8 Android emulator large screen에서 핵심 flow를 완료했다.
Real device evidence: iPhone 15 real device에서 dark mode, offline mode, background 복귀와 production signing을 확인했다.
Permission evidence: permission prompt 문구와 camera/photo/location/notification granted, denied, limited fallback을 각각 재현했다.
Network evidence: offline, poor network retry, sync conflict 해결과 deep link cold start 및 warm start를 검증했다.
Accessibility evidence: screen reader label, touch target size, dynamic type font scaling, contrast, keyboard avoidance, safe area, reduced motion을 확인했다.

## store readiness

- [x] app privacy label 또는 data safety form에 필요한 데이터 사용이 정리되었다.
- [x] EAS Submit 또는 수동 App Store Connect/Play Console 제출 절차가 정해져 있다.
- [x] permission purpose string이 실제 기능과 일치한다.
- [x] app icon과 splash screen이 release build에서 검증되었다.
- [x] store metadata, screenshots, description, support URL, privacy policy URL이 준비되었다.
- [x] 심사 거절 가능성이 있는 기능과 대응 계획이 정리되었다.

Store evidence: EAS Submit dry run과 App Store Connect 및 Play Console 권한을 확인했고 제출 담당자와 승인 순서를 기록했다.
Asset evidence: app icon, splash, store metadata, screenshots, description, support URL, privacy policy URL이 승인본과 일치한다.
