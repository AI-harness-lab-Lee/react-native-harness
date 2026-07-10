# Mobile Release Checklist

## build

- [x] release build가 local 또는 CI에서 성공했다.
- [x] iOS와 Android build artifact가 분리되어 관리된다.
- [x] Expo 프로젝트는 EAS Build profile(dev/staging/prod)과 runtimeVersion/channel 정책이 문서화되어 있다.
- [x] React Native CLI 프로젝트는 Xcode archive와 Gradle assemble/bundle release 절차가 문서화되어 있다.
- [x] app version과 iOS build number, Android versionCode가 release tag와 일치한다.
- [x] dev/staging/prod environment config가 분리되어 있다.
- [x] secret이 repository에 저장되지 않는다.
- [x] production build에 dev endpoint, test credential, secret이 포함되지 않는 것을 확인했다.

Evidence: 2026-06-10 CI release job `mobile-release-412` produced EAS Build artifacts `ios-a1b2.ipa` and `android-a1b2.aab`; the bare React Native fallback run documented Xcode archive and Gradle bundle release steps for native module escape hatch review.
Evidence: release tag `v1.8.0-mobile.4` matches app version `1.8.0`, iOS build number `184`, Android versionCode `184`; prod env uses `api.example.com` and secret scan `gitleaks-412.json` found no repository secret, test credential, or dev endpoint in production build.

## signing

- [x] iOS certificate/provisioning profile 소유자와 갱신 절차가 정해져 있다.
- [x] Android keystore 소유자와 backup 절차가 정해져 있다.
- [x] signing credential 접근 권한이 최소화되어 있다.

Evidence: iOS certificate/provisioning owner is Release Engineering, Android keystore owner is Mobile Platform, backup is in the approved vault, and signing credential access is limited to the release manager plus two break-glass approvers.

## crash reporting

- [x] crash reporting SDK가 설정되어 있다.
- [x] release build에서 crash report 수집이 검증되었다.
- [x] source map 또는 symbol upload 절차가 있다.
- [x] crash report에서 token, email, phone, address 등 민감 정보가 필터링된다.

Evidence: crash reporting is Sentry project `mobile-prod`; release build smoke crash `CRASH-2026-06-10-01` was received, source map and native symbol upload completed, and token/email/phone/address scrubber rules were verified against the sample event.

## OTA update policy

- [x] OTA update 가능 범위가 문서화되어 있다.
- [x] EAS Update channel/branch와 native runtimeVersion 호환 기준이 정해져 있다.
- [x] native binary 변경이 필요한 update 기준이 문서화되어 있다.
- [x] rollback 조건과 절차가 정해져 있다.
- [x] OTA update를 끄거나 중단해야 하는 조건이 정해져 있다.

Evidence: EAS Update uses `production` channel, `release/1.8` branch, and runtimeVersion `appVersion`; OTA is limited to JavaScript/resource fixes, native module, permission, entitlement, app icon, splash, or app config changes require binary release, and rollback uses previous update group `8f33` after crash-free rate drops below 99.5%.

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

Evidence: iOS simulator iPhone 15 iOS 18.5, Android emulator Pixel 8 API 35, and real device iPhone SE 3 iOS 17.6 passed login, checkout, profile edit, and push notification open flows; small screen iPhone SE 3 and large screen Pixel Tablet confirmed layout stability.
Evidence: dark mode screenshots `dark-ios-184.png` and `dark-android-184.png` passed contrast review; offline mode, poor network retry, and sync conflict evidence are recorded in `.harness/reports/mobile-review.md#permissionofflinedeep-link-evidence`.
Evidence: permission prompt copy was checked for camera/photo/location/notification; denied, granted, and limited states were verified, including push notification receive/open handling and fallback copy after denial.
Evidence: deep link cold start `myapp://orders/123` and warm start `myapp://profile` were validated through allowlist, auth state, and parameter validation before navigation.
Evidence: screen reader label coverage, touch target size over 44px, dynamic type/font scaling at large sizes, reduced motion, contrast, keyboard avoidance, and safe area behavior passed the mobile accessibility checklist.

## store readiness

- [x] app privacy label 또는 data safety form에 필요한 데이터 사용이 정리되었다.
- [x] EAS Submit 또는 수동 App Store Connect/Play Console 제출 절차가 정해져 있다.
- [x] permission purpose string이 실제 기능과 일치한다.
- [x] app icon과 splash screen이 release build에서 검증되었다.
- [x] store metadata, screenshots, description, support URL, privacy policy URL이 준비되었다.
- [x] 심사 거절 가능성이 있는 기능과 대응 계획이 정리되었다.

Evidence: App Store Connect and Play Console store metadata are ready, screenshots include small and large screen variants, support URL and privacy policy URL are valid, app icon and splash render in the release build, and review-risk notes cover location permission, push notification opt-in, account deletion, and offline cache behavior.
