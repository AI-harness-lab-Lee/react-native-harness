# Mobile Security Policy

## 통과 기준

모바일 앱은 웹보다 local device에 남는 정보와 deep link, 권한, native API 리스크가 큽니다. 다음 항목 중 하나라도 위반하면 security score를 낮추고, token 또는 PII 노출 가능성이 있으면 critical issue로 처리합니다.

## token handling

- access token, refresh token, session secret은 `secure-store`, Keychain, Android Keystore 기반 저장소에만 저장한다.
- `async-storage`, plain file, sqlite plain table에는 token을 저장하지 않는다.
- token은 log, analytics, crash report, screenshot, error message에 남기지 않는다.
- logout, account deletion, refresh token expiration 시 local credential을 삭제한다.

## PII local storage

- PII local storage는 기본 금지다.
- offline 기능 때문에 예외가 필요한 경우 저장 대상, 암호화 방식, 보관 기간, 삭제 조건, sync 실패 시 처리 방식을 `.harness/mobile-plan.md`에 기록한다.
- 민감 데이터가 cache에 들어갈 수 있는 API response는 cache key, persistence, invalidation 정책을 검토한다.

## permission

- 권한은 앱 시작 시 일괄 요청하지 않는다. 기능 사용 시점에 최소 권한만 요청한다.
- 권한 요청 전 사용자에게 목적을 설명하고, 거부 시 fallback UX를 제공한다.
- camera, location, contacts, photo library, microphone, notification 권한은 별도 리스크로 기록한다.

## deep link

- deep link는 scheme, host, path allowlist를 적용한다.
- route parameter는 schema validation을 거친다.
- 인증이 필요한 route는 auth state와 authorization을 확인한 뒤 이동한다.
- 결제, 삭제, 권한 변경 같은 destructive action은 deep link 진입만으로 실행하지 않는다.

## transport

- production API는 HTTPS만 허용한다.
- certificate pinning은 high-risk 앱에서 검토하되, 인증서 교체와 장애 대응 절차가 없으면 무조건 적용하지 않는다.
- development/staging endpoint가 production build에 포함되지 않도록 environment config를 분리한다.

## 협업

공통 인증/인가, API 보안, privacy threat model은 `web-security-harness`와 함께 검토한다. secure storage, permission, deep link, device-local data는 `react-native-harness`가 최종 책임을 가진다.
