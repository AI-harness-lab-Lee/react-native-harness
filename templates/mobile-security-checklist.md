# Mobile Security Checklist

## token handling

- [ ] access token과 refresh token은 secure storage에 저장한다.
- [ ] token은 log, crash report, analytics event에 남기지 않는다.
- [ ] refresh 실패 시 session cleanup과 재로그인 흐름이 있다.

## local storage

- [ ] PII는 기본적으로 local storage에 저장하지 않는다.
- [ ] PII 저장 예외는 암호화, 보관 기간, 삭제 조건을 문서화한다.
- [ ] async storage에는 민감한 값을 저장하지 않는다.

## permissions

- [ ] 권한 요청은 기능 사용 시점에 한다.
- [ ] 권한 요청 전에 사용자에게 목적을 설명한다.
- [ ] 권한 거부 시 fallback UX가 있다.

## deep links

- [ ] 허용된 scheme/host/path만 처리한다.
- [ ] route parameter를 validation한다.
- [ ] 인증이 필요한 화면은 auth state 확인 후 이동한다.
- [ ] destructive action은 deep link만으로 실행하지 않는다.

## transport

- [ ] 모든 API 통신은 TLS를 사용한다.
- [ ] certificate pinning 여부는 threat model과 운영 비용을 기준으로 결정한다.
- [ ] development endpoint가 production build에 포함되지 않는다.

## privacy

- [ ] analytics event에 PII를 포함하지 않는다.
- [ ] crash report에 token, email, phone, address 등 민감 정보가 포함되지 않게 필터링한다.
- [ ] 계정 삭제 또는 로그아웃 시 local sensitive data cleanup이 수행된다.
