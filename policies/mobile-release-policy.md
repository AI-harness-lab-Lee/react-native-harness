# Mobile Release Policy

## 통과 기준

release readiness는 코드 완성만으로 통과하지 않는다. build, signing, environment config, crash reporting, OTA update policy, app store 제출 리스크가 문서화되어야 한다.

## build

- iOS와 Android release build가 각각 성공해야 한다.
- Expo 프로젝트는 EAS Build profile을 dev/staging/prod로 분리한다.
- React Native CLI 프로젝트는 Xcode/Gradle release build 절차를 문서화한다.
- release build에서 debug menu, development endpoint, test credential이 비활성화되어야 한다.

## signing

- iOS certificate, provisioning profile, App Store Connect 권한 소유자를 문서화한다.
- Android keystore, key alias, backup 위치, rotation 절차를 문서화한다.
- signing credential은 repository에 저장하지 않는다.

## environment config

- dev/staging/prod API endpoint와 feature flag를 분리한다.
- secret은 build-time 또는 runtime secret manager로 주입하고 git에 저장하지 않는다.
- production build에서 staging analytics/crash project로 전송되지 않게 검증한다.

## crash reporting

- crash reporting 도구를 하나 이상 설정한다.
- source map 또는 native symbol upload 절차를 release checklist에 기록한다.
- PII와 token이 crash report에 포함되지 않게 필터링한다.

## OTA update

- OTA update는 JavaScript/resource 변경에만 사용한다.
- native module, permission, entitlements, app config 변경은 binary release가 필요하다.
- rollback 조건과 배포 중단 기준을 정한다.

## store submission

- app privacy label 또는 data safety form에 필요한 데이터 수집 항목을 정리한다.
- permission purpose string은 실제 기능과 일치해야 한다.
- 심사 거절 가능성이 있는 기능은 대응 문구와 fallback을 준비한다.
