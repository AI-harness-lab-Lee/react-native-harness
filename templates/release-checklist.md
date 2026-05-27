# Mobile Release Checklist

## build

- [ ] release build가 local 또는 CI에서 성공했다.
- [ ] iOS와 Android build artifact가 분리되어 관리된다.
- [ ] dev/staging/prod environment config가 분리되어 있다.
- [ ] secret이 repository에 저장되지 않는다.

## signing

- [ ] iOS certificate/provisioning profile 소유자와 갱신 절차가 정해져 있다.
- [ ] Android keystore 소유자와 backup 절차가 정해져 있다.
- [ ] signing credential 접근 권한이 최소화되어 있다.

## crash reporting

- [ ] crash reporting SDK가 설정되어 있다.
- [ ] release build에서 crash report 수집이 검증되었다.
- [ ] source map 또는 symbol upload 절차가 있다.

## OTA update policy

- [ ] OTA update 가능 범위가 문서화되어 있다.
- [ ] native binary 변경이 필요한 update 기준이 문서화되어 있다.
- [ ] rollback 조건과 절차가 정해져 있다.

## store readiness

- [ ] app privacy label 또는 data safety form에 필요한 데이터 사용이 정리되었다.
- [ ] permission purpose string이 실제 기능과 일치한다.
- [ ] screenshots, description, support URL, privacy policy URL이 준비되었다.
- [ ] 심사 거절 가능성이 있는 기능과 대응 계획이 정리되었다.
