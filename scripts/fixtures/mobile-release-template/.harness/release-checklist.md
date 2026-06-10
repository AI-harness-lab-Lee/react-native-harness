# Mobile Release Checklist

## build

- [ ] release build가 local 또는 CI에서 성공했다.
- [ ] iOS와 Android build artifact가 분리되어 관리된다.
- [ ] Expo 프로젝트는 EAS Build profile(dev/staging/prod)과 runtimeVersion/channel 정책이 문서화되어 있다.
- [ ] React Native CLI 프로젝트는 Xcode archive와 Gradle assemble/bundle release 절차가 문서화되어 있다.
- [ ] app version과 iOS build number, Android versionCode가 release tag와 일치한다.
- [ ] dev/staging/prod environment config가 분리되어 있다.
- [ ] secret이 repository에 저장되지 않는다.
- [ ] production build에 dev endpoint, test credential, secret이 포함되지 않는 것을 확인했다.

## signing

- [ ] iOS certificate/provisioning profile 소유자와 갱신 절차가 정해져 있다.
- [ ] Android keystore 소유자와 backup 절차가 정해져 있다.
- [ ] signing credential 접근 권한이 최소화되어 있다.

## crash reporting

- [ ] crash reporting SDK가 설정되어 있다.
- [ ] release build에서 crash report 수집이 검증되었다.
- [ ] source map 또는 symbol upload 절차가 있다.
- [ ] crash report에서 token, email, phone, address 등 민감 정보가 필터링된다.

## OTA update policy

- [ ] OTA update 가능 범위가 문서화되어 있다.
- [ ] EAS Update channel/branch와 native runtimeVersion 호환 기준이 정해져 있다.
- [ ] native binary 변경이 필요한 update 기준이 문서화되어 있다.
- [ ] rollback 조건과 절차가 정해져 있다.
- [ ] OTA update를 끄거나 중단해야 하는 조건이 정해져 있다.

## release evidence

각 체크 항목 아래에는 실행 일시, 기기/OS, build artifact 또는 report path, 담당자, 결과를 한 줄 이상 기록합니다. 체크박스만 `x`로 바꾸고 evidence detail이 없으면 release validator를 통과할 수 없습니다.

- [ ] iOS simulator evidence가 첨부되었다.
- [ ] Android emulator evidence가 첨부되었다.
- [ ] 최소 1개 real device evidence 또는 생략 사유가 첨부되었다.
- [ ] small screen evidence가 첨부되었다.
- [ ] large screen evidence가 첨부되었다.
- [ ] dark mode evidence가 첨부되었다.
- [ ] offline mode evidence가 첨부되었다.
- [ ] permission prompt copy와 fallback evidence가 첨부되었다.
- [ ] push notification permission/receive/open evidence 또는 명시적 비사용 사유가 첨부되었다.
- [ ] camera/photo/location/notification permission의 denied/granted/limited 상태 evidence가 첨부되었다.
- [ ] offline, poor network/retry, sync conflict evidence가 첨부되었다.
- [ ] deep link cold start와 warm start evidence가 첨부되었다.
- [ ] screen reader label, touch target size, dynamic type/font scaling, contrast, keyboard avoidance, safe area evidence가 첨부되었다.
- [ ] reduced motion evidence가 첨부되었다.

## store readiness

- [ ] app privacy label 또는 data safety form에 필요한 데이터 사용이 정리되었다.
- [ ] EAS Submit 또는 수동 App Store Connect/Play Console 제출 절차가 정해져 있다.
- [ ] permission purpose string이 실제 기능과 일치한다.
- [ ] app icon과 splash screen이 release build에서 검증되었다.
- [ ] store metadata, screenshots, description, support URL, privacy policy URL이 준비되었다.
- [ ] 심사 거절 가능성이 있는 기능과 대응 계획이 정리되었다.
