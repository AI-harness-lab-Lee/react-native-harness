# Mobile Release Policy

## 통과 기준

release readiness는 코드 완성만으로 통과하지 않는다. build, signing, environment config, app version/build number, crash reporting, OTA update policy, rollback, app store 제출 리스크, device/release evidence가 문서화되어야 한다.

## build

- iOS와 Android release build가 각각 성공해야 한다.
- Expo 프로젝트는 Expo SDK version과 EAS Build profile을 dev/staging/prod로 분리한다.
- Expo 프로젝트는 EAS Submit 사용 여부와 App Store Connect/Play Console 권한 경계를 문서화한다.
- React Native CLI 프로젝트는 Xcode archive와 Gradle assemble/bundle release build 절차를 문서화한다.
- app version, iOS build number, Android versionCode가 release tag와 일치해야 한다.
- release build에서 debug menu, development endpoint, test credential이 비활성화되어야 한다. production build에 dev endpoint 또는 secret이 포함되면 차단 이슈다.

## signing

- iOS certificate, provisioning profile, App Store Connect 권한 소유자를 문서화한다.
- Android keystore, key alias, backup 위치, rotation 절차를 문서화한다.
- signing credential은 repository에 저장하지 않는다.
- iOS/Android signing 소유자와 갱신 절차가 없으면 release 차단 이슈다.

## environment config

- dev/staging/prod API endpoint와 feature flag를 분리한다.
- secret은 build-time 또는 runtime secret manager로 주입하고 git에 저장하지 않는다.
- production build에서 staging analytics/crash project로 전송되지 않게 검증한다.

## crash reporting

- crash reporting 도구를 하나 이상 설정한다.
- source map 또는 native symbol upload 절차를 release checklist에 기록한다.
- PII와 token이 crash report에 포함되지 않게 필터링한다.
- crash reporting 설정 또는 release build 검증이 없으면 release 차단 이슈다.

## OTA update

- OTA update는 JavaScript/resource 변경에만 사용한다.
- EAS Update를 쓰는 경우 channel/branch, runtimeVersion, rollout 대상, rollback path를 문서화한다.
- native module, permission, entitlements, app config 변경은 binary release가 필요하다.
- rollback 조건과 배포 중단 기준을 정한다.
- OTA update policy가 없으면 release 차단 이슈다.

## release evidence

- iOS simulator와 Android emulator 검증 결과를 release checklist 또는 mobile review에 남긴다.
- 최소 1개 real device 검증 결과를 남긴다. real device를 생략하면 기기 접근 불가, 릴리즈 범위 제한 등 구체적 사유를 기록한다.
- small screen, large screen, dark mode, offline mode 검증 결과를 남긴다.
- permission prompt copy와 거부 fallback 검증 결과를 남긴다.
- push notification 권한, 수신, open flow 검증 결과를 남긴다. 기능이 없으면 명시적 비사용 사유를 남긴다.
- camera/photo/location/notification 권한은 denied/granted/limited 상태를 검증한다.
- offline, poor network/retry, sync conflict, deep link cold start/warm start 결과를 남긴다.
- app icon과 splash screen이 release build에서 올바르게 보이는지 검증한다.
- screen reader label, dynamic type/font scaling, reduced motion, touch target size, contrast, keyboard avoidance/safe area 결과를 남긴다.
- release evidence가 없으면 release readiness 통과를 막는다.

## store submission

- app privacy label 또는 data safety form에 필요한 데이터 수집 항목을 정리한다.
- permission purpose string은 실제 기능과 일치해야 한다.
- store metadata, screenshots, description, support URL, privacy policy URL을 제출 전 준비한다.
- 심사 거절 가능성이 있는 기능은 대응 문구와 fallback을 준비한다.
