# Mobile Performance Policy

## 통과 기준

모바일 성능은 startup, render cost, list performance, image/resource size, network/cache, offline behavior를 기준으로 검토한다. 사용자가 체감하는 주요 flow에서 명백한 지연이 있으면 performance score를 낮춘다.

## startup

- 앱 시작 시 불필요한 API 호출과 무거운 초기화를 피한다.
- auth restore, remote config, initial navigation 결정은 timeout과 fallback을 둔다.
- splash screen이 무한 대기하지 않게 실패 경로를 둔다.

## rendering

- large list는 virtualization을 사용한다.
- list item은 불필요한 re-render를 줄인다.
- navigation 전환 중 무거운 계산을 피한다.
- image는 화면 크기에 맞는 크기와 caching 전략을 사용한다.

## network and cache

- 서버 상태는 cache, retry, stale time, invalidation 기준을 명확히 둔다.
- 느린 네트워크와 offline 상태에서 loading/error/empty state가 분리되어야 한다.
- 중복 submit과 중복 mutation을 방지한다.

## offline behavior

- offline에서 가능한 기능과 불가능한 기능을 UI에서 구분한다.
- sync queue가 있다면 retry, conflict, duplication 방지 정책을 둔다.
- local cache는 만료와 삭제 조건을 가져야 한다.

## measurement

- release 전 핵심 flow의 cold start, list scroll, API retry, offline 전환을 수동 또는 자동으로 점검한다.
- 성능 개선은 추측만으로 처리하지 말고 profiler, logs, reproduction step 중 하나 이상의 근거를 남긴다.
