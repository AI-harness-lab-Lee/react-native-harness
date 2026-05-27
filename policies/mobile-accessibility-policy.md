# Mobile Accessibility Policy

## 통과 기준

모바일 접근성은 screen reader, touch target, focus flow, contrast, dynamic text를 기준으로 검토한다. 핵심 사용자 여정에서 접근성 blocker가 있으면 release readiness도 낮춘다.

## screen reader

- interactive element에는 명확한 accessibility label을 제공한다.
- icon-only button은 의미 있는 label을 가져야 한다.
- decorative image는 screen reader에서 불필요하게 읽히지 않게 처리한다.
- 상태 변화는 필요한 경우 accessibility announcement로 전달한다.
- 인증, 결제, 삭제, 제출 등 핵심 action은 screen reader 사용자가 목적과 결과를 이해할 수 있어야 한다.

## touch target

- 주요 tap target은 충분한 크기와 간격을 가진다.
- 작은 icon button은 hit slop 또는 충분한 padding을 둔다.
- destructive action은 실수로 누르기 어렵게 배치하고 확인 흐름을 둔다.
- permission 요청 화면의 허용/거부 경로는 모두 접근 가능한 control이어야 한다.

## focus and navigation

- modal, bottom sheet, form error 상태에서 focus 흐름이 끊기지 않아야 한다.
- keyboard 입력 화면은 submit, next, dismiss 흐름이 자연스러워야 한다.
- back gesture와 hardware back button 동작을 명확히 정의한다.

## visual accessibility

- 텍스트와 핵심 UI는 충분한 contrast를 유지한다.
- 색만으로 상태를 전달하지 않는다.
- dynamic text 또는 OS font scaling에서 주요 텍스트가 잘리거나 겹치지 않아야 한다.

## 테스트

- 최소 하나의 주요 flow는 screen reader 기준으로 수동 점검한다.
- component test에서는 중요한 label, role, error message를 검증한다.
- permission denied, form error, offline error 상태도 접근성 검증 대상에 포함한다.
