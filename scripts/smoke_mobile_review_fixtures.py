#!/usr/bin/env python3
"""Exercise canonical and PM registry mobile validators against fixed cases."""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

from check_mobile_plan import validate as validate_mobile_plan


SCRIPT_ROOT = Path(__file__).resolve().parent
HARNESS_ROOT = SCRIPT_ROOT.parent
FIXTURE_ROOT = HARNESS_ROOT / "tests" / "fixtures" / "mobile-review"
CANONICAL_VALIDATOR = SCRIPT_ROOT / "check_mobile_review.py"
REGISTRY_VALIDATOR = SCRIPT_ROOT / "check_mobile_release.py"


@dataclass(frozen=True)
class Case:
    name: str
    expected_pass: bool
    expected_message: str | None
    transform: str | None = None


CASES = [
    Case("valid", True, None),
    Case("global-placeholder-words", True, None, "global-placeholder-words"),
    Case("missing-category", False, "필수 score category가 없습니다: performance", "missing-category"),
    Case("low-score-7.9", False, "performance 점수가 기준 미만입니다: 7.9 < 8", "low-score"),
    Case(
        "unresolved-critical",
        False,
        "Critical Issues 섹션에 unresolved issue가 남아 있습니다.",
        "critical",
    ),
    Case(
        "critical-owner-none",
        False,
        "Critical Issues 섹션에 unresolved issue가 남아 있습니다.",
        "critical-owner-none",
    ),
    Case(
        "high-owner-none",
        False,
        "High Issues 섹션에 unresolved issue가 남아 있습니다.",
        "high-owner-none",
    ),
    Case("normal-none-table", True, None, "normal-none-table"),
    Case(
        "critical-none-table-unresolved",
        False,
        "Critical Issues 섹션에 unresolved issue가 남아 있습니다.",
        "critical-none-table-unresolved",
    ),
    Case(
        "high-none-table-blocked",
        False,
        "High Issues 섹션에 unresolved issue가 남아 있습니다.",
        "high-none-table-blocked",
    ),
    Case(
        "release-none-table-blocker-yes",
        False,
        "Release Blockers 섹션에 unresolved issue가 남아 있습니다.",
        "release-none-table-blocker-yes",
    ),
    Case(
        "missing-high-section",
        False,
        "High Issues 섹션이 없거나 비어 있습니다.",
        "missing-high-section",
    ),
    Case(
        "missing-release-blockers-section",
        False,
        "Release Blockers 섹션이 없거나 비어 있습니다.",
        "missing-release-blockers-section",
    ),
    Case(
        "empty-verification",
        False,
        "검증 결과 섹션의 build/test 또는 mobile verification 결과가 비어 있습니다.",
        "verification",
    ),
    Case("placeholder-template", False, "placeholder 표현이 너무 많습니다: 3개", "placeholder"),
    Case("missing-report", False, "필수 파일이 없습니다", "missing-report"),
]


def transformed_report(valid_report: str, transform: str | None) -> str | None:
    if transform is None:
        return valid_report
    if transform == "global-placeholder-words":
        return (
            valid_report
            + "\n## Historical validator vocabulary\n\n"
            + "TODO, TBD, template 문자열은 과거 검사 규칙 이름이며 현재 evidence 값이 아니다.\n"
        )
    if transform == "missing-category":
        return valid_report.replace("performance: 8.8/10\n", "")
    if transform == "low-score":
        return valid_report.replace("performance: 8.8/10", "performance: 7.9/10")
    if transform == "critical":
        return valid_report.replace(
            "## Critical Issues\n\n- 없음",
            "## Critical Issues\n\n- Production crash on authenticated deep link remains unresolved",
        )
    if transform == "critical-owner-none":
        return valid_report.replace(
            "## Critical Issues\n\n- 없음",
            "## Critical Issues\n\n- Auth bypass remains unresolved; owner: none",
        )
    if transform == "high-owner-none":
        return valid_report.replace(
            "| none | none | resolved | proceed |",
            "| MOB-HIGH-1 | high | pending | owner: none |",
            1,
        )
    if transform == "normal-none-table":
        return valid_report.replace(
            "## Critical Issues\n\n- 없음",
            "## Critical Issues\n\n| Issue | Status | Decision |\n"
            "| --- | --- | --- |\n"
            "| none | resolved | proceed |",
        )
    if transform == "critical-none-table-unresolved":
        return valid_report.replace(
            "## Critical Issues\n\n- 없음",
            "## Critical Issues\n\n| Issue | Severity | Status |\n"
            "| --- | --- | --- |\n"
            "| none | critical | unresolved |",
        )
    if transform == "high-none-table-blocked":
        return valid_report.replace(
            "| none | none | resolved | proceed |",
            "| none | high | blocked | proceed |",
            1,
        )
    if transform == "release-none-table-blocker-yes":
        return valid_report.replace(
            "| none | resolved | no | proceed |",
            "| none | resolved | release blocker: yes | proceed |",
            1,
        )
    if transform == "missing-high-section":
        return re.sub(
            r"\n## High Issues\n.*?(?=\n## Release Blockers)",
            "",
            valid_report,
            count=1,
            flags=re.DOTALL,
        )
    if transform == "missing-release-blockers-section":
        return re.sub(
            r"\n## Release Blockers\n.*?(?=\n## device matrix)",
            "",
            valid_report,
            count=1,
            flags=re.DOTALL,
        )
    if transform == "verification":
        report = valid_report
        report = report.replace(
            "- build: EAS Build production iOS와 Android artifact 생성 성공, build log FL-185-20260710 확인",
            "- build:",
        )
        report = report.replace(
            "- test: Jest unit 및 React Native Testing Library interaction suite 128개 성공",
            "- test:",
        )
        return report.replace(
            "- mobile verification: iOS simulator, Android emulator, real device 핵심 여정과 접근성 점검 성공",
            "- mobile verification:",
        )
    if transform == "placeholder":
        report = valid_report.replace(
            "- build: EAS Build production iOS와 Android artifact 생성 성공, build log FL-185-20260710 확인",
            "- build: TODO",
        )
        report = report.replace(
            "- test: Jest unit 및 React Native Testing Library interaction suite 128개 성공",
            "- test: TBD",
        )
        return report.replace(
            "- mobile verification: iOS simulator, Android emulator, real device 핵심 여정과 접근성 점검 성공",
            "- mobile verification: placeholder",
        )
    if transform == "missing-report":
        return None
    raise ValueError(f"알 수 없는 fixture transform: {transform}")


def run_validator(script: Path, project_root: Path, *extra_args: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return subprocess.run(
        [sys.executable, "-B", str(script), "--project-root", str(project_root), *extra_args],
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )


def combined_output(result: subprocess.CompletedProcess[str]) -> str:
    return result.stdout + result.stderr


def prepare_project(root: Path, report: str | None, release_fixture: Path) -> None:
    reports = root / ".harness" / "reports"
    reports.mkdir(parents=True)
    shutil.copyfile(release_fixture, root / ".harness" / "release-checklist.md")
    if report is not None:
        (reports / "mobile-review.md").write_text(report, encoding="utf-8")
    (reports / "review-score.json").write_text(
        json.dumps(valid_review_score_payload()),
        encoding="utf-8",
    )


def assert_case(case: Case, report: str | None, release_fixture: Path, temp_root: Path) -> None:
    project_root = temp_root / case.name
    prepare_project(project_root, report, release_fixture)
    canonical = run_validator(CANONICAL_VALIDATOR, project_root)
    registry = run_validator(REGISTRY_VALIDATOR, project_root)
    expected_code = 0 if case.expected_pass else 1

    if canonical.returncode != expected_code or registry.returncode != expected_code:
        raise AssertionError(
            f"{case.name}: expected {expected_code}, canonical={canonical.returncode}, "
            f"registry={registry.returncode}\ncanonical:\n{combined_output(canonical)}"
            f"\nregistry:\n{combined_output(registry)}"
        )
    if canonical.returncode != registry.returncode:
        raise AssertionError(f"{case.name}: canonical/registry 판정 불일치")
    if case.expected_message:
        if case.expected_message not in combined_output(canonical):
            raise AssertionError(f"{case.name}: canonical failure message 누락")
        if case.expected_message not in combined_output(registry):
            raise AssertionError(f"{case.name}: registry failure message 누락")

    outcome = "PASS" if case.expected_pass else "FAIL(expected)"
    print(f"{case.name}: {outcome}; canonical={canonical.returncode}, registry={registry.returncode}")


def assert_project_boundary(valid_project: Path, temp_root: Path) -> None:
    outside_release = temp_root / "outside-release-checklist.md"
    outside_release.write_text("secret-like external content must not be read", encoding="utf-8")
    release_result = run_validator(
        REGISTRY_VALIDATOR,
        valid_project,
        "--release-checklist",
        str(outside_release),
    )
    if release_result.returncode != 1 or "project root 외부" not in combined_output(release_result):
        raise AssertionError("project-root 외부 release checklist가 차단되지 않았습니다.")

    outside_output = temp_root / "outside-gate.json"
    output_result = run_validator(
        REGISTRY_VALIDATOR,
        valid_project,
        "--json",
        "--output-json",
        str(outside_output),
    )
    if output_result.returncode != 1 or "project root 외부" not in combined_output(output_result):
        raise AssertionError("project-root 외부 JSON output이 차단되지 않았습니다.")
    if outside_output.exists():
        raise AssertionError("project-root 외부 JSON output이 생성되었습니다.")

    relative_escape = temp_root / "escape.json"
    relative_result = run_validator(
        REGISTRY_VALIDATOR,
        valid_project,
        "--output-json",
        "../escape.json",
    )
    if relative_result.returncode != 1 or "project root 외부" not in combined_output(relative_result):
        raise AssertionError("relative .. JSON output 경로가 차단되지 않았습니다.")
    if relative_escape.exists():
        raise AssertionError("relative .. JSON output이 project root 외부에 생성되었습니다.")

    print("project-boundary: PASS; external read/write paths rejected")


def assert_output_input_collisions(valid_project: Path, release_fixture: Path) -> None:
    custom_release = valid_project / ".harness" / "custom-release-checklist.md"
    shutil.copyfile(release_fixture, custom_release)
    collision_cases = [
        ("release-checklist", valid_project / ".harness" / "release-checklist.md", []),
        ("mobile-review", valid_project / ".harness" / "reports" / "mobile-review.md", []),
        ("review-score", valid_project / ".harness" / "reports" / "review-score.json", []),
        (
            "custom-release",
            custom_release,
            ["--release-checklist", str(custom_release.relative_to(valid_project))],
        ),
    ]
    for name, collision_path, extra_args in collision_cases:
        before = {
            path.relative_to(valid_project): path.read_bytes()
            for path in valid_project.rglob("*")
            if path.is_file() and not path.is_symlink()
        }
        result = run_validator(
            REGISTRY_VALIDATOR,
            valid_project,
            *extra_args,
            "--output-json",
            str(collision_path),
        )
        output = combined_output(result)
        if result.returncode != 1 or "validation input artifact와 충돌" not in output:
            raise AssertionError(f"output-collision-{name}: collision이 차단되지 않았습니다.\n{output}")
        after = {
            path.relative_to(valid_project): path.read_bytes()
            for path in valid_project.rglob("*")
            if path.is_file() and not path.is_symlink()
        }
        if before != after:
            raise AssertionError(f"output-collision-{name}: input file bytes가 변경되었습니다.")
        leftovers = list(collision_path.parent.glob(f".{collision_path.name}.*.tmp"))
        if leftovers:
            raise AssertionError(f"output-collision-{name}: 임시 파일이 남았습니다: {leftovers}")
    print("output-input-collision: PASS; canonical/custom inputs preserved")


def assert_input_hardlinks(valid_report: str, release_fixture: Path, temp_root: Path) -> None:
    cases = ["mobile-review", "review-score", "release-checklist"]
    for name in cases:
        project_root = temp_root / f"hardlink-{name}"
        prepare_project(project_root, valid_report, release_fixture)
        if name == "mobile-review":
            target = project_root / ".harness" / "reports" / "mobile-review.md"
            validators = [CANONICAL_VALIDATOR, REGISTRY_VALIDATOR]
        elif name == "review-score":
            target = project_root / ".harness" / "reports" / "review-score.json"
            validators = [CANONICAL_VALIDATOR, REGISTRY_VALIDATOR]
        else:
            target = project_root / ".harness" / "release-checklist.md"
            validators = [REGISTRY_VALIDATOR]
        outside = temp_root / f"outside-{name}{target.suffix}"
        outside.write_bytes(target.read_bytes())
        target.unlink()
        os.link(outside, target)
        for validator in validators:
            result = run_validator(validator, project_root)
            if result.returncode != 1 or "hardlink" not in combined_output(result):
                raise AssertionError(
                    f"input-hardlink-{name}: {validator.name}가 hardlink input을 허용했습니다."
                )
    print("input-hardlinks: PASS; mobile review, score, release inputs rejected")


def assert_score_and_release_symlinks(
    valid_report: str,
    release_fixture: Path,
    temp_root: Path,
) -> None:
    for name in ["review-score", "release-checklist"]:
        project_root = temp_root / f"symlink-{name}"
        prepare_project(project_root, valid_report, release_fixture)
        if name == "review-score":
            target = project_root / ".harness" / "reports" / "review-score.json"
            validators = [CANONICAL_VALIDATOR, REGISTRY_VALIDATOR]
        else:
            target = project_root / ".harness" / "release-checklist.md"
            validators = [REGISTRY_VALIDATOR]
        outside = temp_root / f"outside-symlink-{name}{target.suffix}"
        outside.write_bytes(target.read_bytes())
        target.unlink()
        target.symlink_to(outside)
        for validator in validators:
            result = run_validator(validator, project_root)
            if result.returncode != 1 or "symlink" not in combined_output(result):
                raise AssertionError(
                    f"input-symlink-{name}: {validator.name}가 symlink input을 허용했습니다."
                )
    print("input-symlinks: PASS; review score and release checklist rejected")


def assert_review_score_required(valid_report: str, release_fixture: Path, temp_root: Path) -> None:
    project_root = temp_root / "missing-review-score"
    prepare_project(project_root, valid_report, release_fixture)
    (project_root / ".harness" / "reports" / "review-score.json").unlink()
    for validator in [CANONICAL_VALIDATOR, REGISTRY_VALIDATOR]:
        result = run_validator(validator, project_root)
        output = combined_output(result)
        if result.returncode != 1 or "review-score.json" not in output or "필수 파일" not in output:
            raise AssertionError(f"review-score-required: {validator.name}가 누락을 허용했습니다.\n{output}")
    print("review-score-required: PASS; missing artifact rejected")


def assert_mobile_plan_path_safety(temp_root: Path) -> None:
    template_bytes = (HARNESS_ROOT / "templates" / "mobile-plan.md").read_bytes()
    valid_plan = """# Mobile Plan

## 앱 목표
Expo 기반 모바일 앱에서 인증된 사용자가 핵심 기록 여정을 안전하고 빠르게 완료한다. MVP는 조회, 작성, 수정과 오류 복구를 포함한다.
## 대상 플랫폼
iOS simulator, Android emulator, real device를 지원하고 small screen, large screen, dark mode, offline mode를 device matrix에서 검증한다.
## 선택한 runtime/tooling
Expo SDK와 EAS Build, EAS Submit을 사용한다. managed workflow를 기본으로 하고 native module risk가 커지면 prebuild workflow 또는 bare React Native CLI 전환을 검토한다.
## 선택한 architecture
Feature, domain, data, presentation 경계를 분리하고 API adapter와 화면 상태의 소유권을 명확히 한다. Native module 의존성은 adapter 뒤로 제한한다.
## navigation 전략
인증 route guard와 deep link allowlist를 적용하며 deep link cold start와 warm start를 각각 실제 build에서 검증한다.
## state management 전략
Server state cache와 client UI state를 분리하고 mutation retry, rollback, conflict 처리 정책을 기능 경계에 기록한다.
## API 연동 전략
문서화된 API contract, auth token refresh, timeout, error format을 adapter에서 검증하고 production endpoint만 release build에 포함한다.
## storage 전략
Token은 secure storage, 비민감 preference는 async storage를 사용하며 PII local storage를 금지하고 logout 시 정리한다.
## 권한 요청 계획
Permission prompt는 기능 진입 시 요청한다. Camera permission granted, denied, limited evidence와 push notification fallback을 실제 device에서 확인한다.
## offline behavior
Offline evidence에는 poor network retry, reconnect, sync conflict 병합 결과와 cache 만료 후 복구 command를 포함한다.
## 테스트 전략
Unit, component, integration, E2E를 실행한다. Screen reader label, Dynamic Type font scaling, reduced motion, touch target size, contrast, keyboard avoidance, safe area를 접근성 evidence로 남긴다.
## 배포 전략
EAS Build artifact와 EAS Submit dry run, app version, build number, signing, crash reporting, OTA update runtimeVersion, rollback 절차를 확인한다. App icon, splash, store metadata와 permission prompt, push notification evidence를 release checklist에 연결한다.
## 주요 리스크
Build 실패와 release risk, native module 호환성, offline conflict, 접근성 회귀를 owner와 trigger별로 추적하고 이전 검증 build로 rollback한다.
"""
    valid_project = temp_root / "plan-valid"
    (valid_project / ".harness").mkdir(parents=True)
    (valid_project / ".harness" / "mobile-plan.md").write_text(valid_plan, encoding="utf-8")
    valid_errors = validate_mobile_plan(valid_project)
    if valid_errors:
        raise AssertionError(f"mobile-plan valid fixture failed: {'; '.join(valid_errors)}")

    outside = temp_root / "outside-mobile-plan.md"
    outside.write_bytes(template_bytes)

    final_symlink = temp_root / "plan-final-symlink"
    (final_symlink / ".harness").mkdir(parents=True)
    (final_symlink / ".harness" / "mobile-plan.md").symlink_to(outside)
    if not any("symlink" in error for error in validate_mobile_plan(final_symlink)):
        raise AssertionError("mobile-plan final symlink가 차단되지 않았습니다.")

    outside_parent = temp_root / "outside-plan-parent"
    outside_parent.mkdir()
    (outside_parent / "mobile-plan.md").write_bytes(template_bytes)
    parent_symlink = temp_root / "plan-parent-symlink"
    parent_symlink.mkdir()
    (parent_symlink / ".harness").symlink_to(outside_parent, target_is_directory=True)
    if not any("symlink" in error for error in validate_mobile_plan(parent_symlink)):
        raise AssertionError("mobile-plan parent symlink가 차단되지 않았습니다.")

    hardlink_project = temp_root / "plan-hardlink"
    (hardlink_project / ".harness").mkdir(parents=True)
    os.link(outside, hardlink_project / ".harness" / "mobile-plan.md")
    if not any("hardlink" in error for error in validate_mobile_plan(hardlink_project)):
        raise AssertionError("mobile-plan hardlink가 차단되지 않았습니다.")
    print("mobile-plan-path-safety: PASS; parent/final symlink and hardlink rejected")


def assert_symlink_boundary(valid_report: str, release_fixture: Path, temp_root: Path) -> None:
    project_root = temp_root / "symlink-boundary"
    reports = project_root / ".harness" / "reports"
    reports.mkdir(parents=True)
    shutil.copyfile(release_fixture, project_root / ".harness" / "release-checklist.md")
    outside_report = temp_root / "outside-mobile-review.md"
    outside_report.write_text(valid_report, encoding="utf-8")
    (reports / "mobile-review.md").symlink_to(outside_report)

    for validator in [CANONICAL_VALIDATOR, REGISTRY_VALIDATOR]:
        result = run_validator(validator, project_root)
        if result.returncode != 1 or "symlink" not in combined_output(result):
            raise AssertionError(
                f"symlink-boundary: {validator.name}가 외부 report를 차단하지 않았습니다."
            )

    print("symlink-boundary: PASS; external report target rejected before read")


def assert_release_template_rejected(valid_report: str, temp_root: Path) -> None:
    project_root = temp_root / "release-template"
    reports = project_root / ".harness" / "reports"
    reports.mkdir(parents=True)
    (reports / "mobile-review.md").write_text(valid_report, encoding="utf-8")
    shutil.copyfile(
        HARNESS_ROOT / "templates" / "release-checklist.md",
        project_root / ".harness" / "release-checklist.md",
    )
    result = run_validator(REGISTRY_VALIDATOR, project_root)
    if result.returncode != 1 or "release-checklist.md가 템플릿 그대로입니다." not in combined_output(result):
        raise AssertionError("release checklist blank template가 차단되지 않았습니다.")

    print("release-template: FAIL(expected); registry=1")


def assert_json_contract(valid_project: Path) -> None:
    output_path = valid_project / ".harness" / "reports" / "mobile-release-gate.json"
    result = run_validator(
        REGISTRY_VALIDATOR,
        valid_project,
        "--json",
        "--output-json",
        str(output_path),
    )
    if result.returncode != 0:
        raise AssertionError(f"json-contract: valid gate failed\n{combined_output(result)}")

    stdout_payload = json.loads(result.stdout)
    file_payload = json.loads(output_path.read_text(encoding="utf-8"))
    expected_categories = [
        "mobile_quality",
        "accessibility",
        "performance",
        "security",
        "release_readiness",
    ]
    expected_artifacts = [
        ".harness/reports/mobile-review.md",
        ".harness/reports/review-score.json",
        ".harness/release-checklist.md",
    ]
    if stdout_payload != file_payload:
        raise AssertionError("json-contract: stdout와 output file payload가 다릅니다.")
    if stdout_payload.get("score_categories") != expected_categories:
        raise AssertionError("json-contract: five score categories가 정확하지 않습니다.")
    if stdout_payload.get("required_artifacts") != expected_artifacts:
        raise AssertionError("json-contract: required artifacts가 정확하지 않습니다.")
    if stdout_payload.get("status") != "pass" or stdout_payload.get("failures"):
        raise AssertionError("json-contract: valid payload status가 pass가 아닙니다.")

    print("json-contract: PASS; five categories and three required artifacts exposed")


def valid_review_score_payload() -> dict[str, object]:
    return {
        "categories": {
            "mobile_quality": 9.2,
            "accessibility": 9.0,
            "performance": 8.8,
            "security": 9.1,
            "release_readiness": 9.0,
        },
        "critical_issues": 0,
        "security": {"critical": 0, "high": 0},
        "findings": [],
        "blocking_reasons": [],
        "passed": True,
    }


def assert_review_score_contract(valid_project: Path) -> None:
    score_path = valid_project / ".harness" / "reports" / "review-score.json"
    base = valid_review_score_payload()
    score_path.write_text(json.dumps(base), encoding="utf-8")
    valid_result = run_validator(CANONICAL_VALIDATOR, valid_project)
    if valid_result.returncode != 0:
        raise AssertionError(f"review-score-current-schema: valid payload failed\n{combined_output(valid_result)}")

    mobile_schema = {
        "categories": base["categories"],
        "critical_issues": [],
        "high_issues": [],
        "release_blockers": [],
        "release_ready": True,
    }
    score_path.write_text(json.dumps(mobile_schema), encoding="utf-8")
    mobile_result = run_validator(CANONICAL_VALIDATOR, valid_project)
    if mobile_result.returncode != 0:
        raise AssertionError(
            f"review-score-mobile-schema: documented schema failed\n{combined_output(mobile_result)}"
        )

    missing_indicators = [
        ("critical", ["critical_issues"], ["critical"], "critical indicator가 없습니다"),
        ("high", [], ["high"], "high indicator가 없습니다"),
        ("release-blocker", ["blocking_reasons"], [], "release blocker indicator가 없습니다"),
        ("readiness", ["passed"], [], "readiness indicator가 없습니다"),
    ]
    for name, top_level_keys, security_keys, expected in missing_indicators:
        payload = json.loads(json.dumps(base))
        for key in top_level_keys:
            payload.pop(key, None)
        security = payload.get("security")
        if isinstance(security, dict):
            for key in security_keys:
                security.pop(key, None)
        score_path.write_text(json.dumps(payload), encoding="utf-8")
        result = run_validator(CANONICAL_VALIDATOR, valid_project)
        if result.returncode != 1 or expected not in combined_output(result):
            raise AssertionError(
                f"review-score-missing-{name}: missing indicator accepted\n{combined_output(result)}"
            )

    invalid_cases: list[tuple[str, object, str]] = [
        ("bool", True, "숫자 score가 아닙니다: performance"),
        ("nan", float("nan"), "유한한 숫자 score가 아닙니다: performance"),
        ("infinity", float("inf"), "유한한 숫자 score가 아닙니다: performance"),
        ("out-of-range", 10.1, "점수 범위가 올바르지 않습니다: performance=10.1"),
        ("below-threshold", 7.9, "performance 점수가 기준 미만입니다: 7.9 < 8"),
    ]
    for name, value, expected in invalid_cases:
        payload = valid_review_score_payload()
        categories = payload["categories"]
        assert isinstance(categories, dict)
        categories["performance"] = value
        score_path.write_text(json.dumps(payload), encoding="utf-8")
        result = run_validator(CANONICAL_VALIDATOR, valid_project)
        if result.returncode != 1 or expected not in combined_output(result):
            raise AssertionError(f"review-score-{name}: invalid score accepted\n{combined_output(result)}")

    blockers: list[tuple[str, object, str]] = [
        ("critical-count", {"critical_issues": 1}, "critical issue가 남아 있습니다"),
        ("critical-array", {"critical_issues": ["MOB-1"]}, "critical issue가 남아 있습니다"),
        ("high-count", {"security": {"critical": 0, "high": 1}}, "high issue가 남아 있습니다"),
        ("high-array", {"high_issues": ["MOB-2"]}, "high issue가 남아 있습니다"),
        ("release-blocker", {"release_blockers": ["MOB-BLOCK"]}, "release blocker가 남아 있습니다"),
        ("not-ready", {"release_ready": False}, "release_ready가 true가 아닙니다"),
    ]
    for name, updates, expected in blockers:
        payload = valid_review_score_payload()
        assert isinstance(updates, dict)
        payload.update(updates)
        score_path.write_text(json.dumps(payload), encoding="utf-8")
        result = run_validator(CANONICAL_VALIDATOR, valid_project)
        if result.returncode != 1 or expected not in combined_output(result):
            raise AssertionError(f"review-score-{name}: blocker accepted\n{combined_output(result)}")

    score_path.write_text(json.dumps(base), encoding="utf-8")
    print("review-score-contract: PASS; current/mobile schemas, required indicators, hostile numbers covered")


def assert_output_path_safety(valid_project: Path, temp_root: Path) -> None:
    reports = valid_project / ".harness" / "reports"
    inside_target = reports / "inside-target.json"
    inside_target.write_text("must stay unchanged", encoding="utf-8")
    output_symlink = reports / "output-symlink.json"
    output_symlink.symlink_to(inside_target)
    symlink_result = run_validator(
        REGISTRY_VALIDATOR,
        valid_project,
        "--output-json",
        str(output_symlink),
    )
    if symlink_result.returncode != 1 or "symlink" not in combined_output(symlink_result):
        raise AssertionError("output-symlink: project 내부 output symlink가 차단되지 않았습니다.")
    if inside_target.read_text(encoding="utf-8") != "must stay unchanged":
        raise AssertionError("output-symlink: symlink target이 덮어써졌습니다.")

    outside_hardlink = temp_root / "outside-hardlink.json"
    outside_hardlink.write_text("outside inode must stay unchanged", encoding="utf-8")
    output_hardlink = reports / "output-hardlink.json"
    os.link(outside_hardlink, output_hardlink)
    hardlink_result = run_validator(
        REGISTRY_VALIDATOR,
        valid_project,
        "--output-json",
        str(output_hardlink),
    )
    if hardlink_result.returncode != 0:
        raise AssertionError(f"output-hardlink: atomic replace failed\n{combined_output(hardlink_result)}")
    if outside_hardlink.read_text(encoding="utf-8") != "outside inode must stay unchanged":
        raise AssertionError("output-hardlink: 외부 hardlink inode가 덮어써졌습니다.")
    if output_hardlink.stat().st_ino == outside_hardlink.stat().st_ino:
        raise AssertionError("output-hardlink: output이 새 inode로 atomic replace되지 않았습니다.")
    json.loads(output_hardlink.read_text(encoding="utf-8"))

    normal_output = reports / "atomic-output.json"
    normal_result = run_validator(
        REGISTRY_VALIDATOR,
        valid_project,
        "--output-json",
        str(normal_output),
    )
    if normal_result.returncode != 0 or not normal_output.is_file():
        raise AssertionError(f"atomic-output: 정상 output write 실패\n{combined_output(normal_result)}")
    leftovers = list(reports.glob(f".{normal_output.name}.*.tmp"))
    if leftovers:
        raise AssertionError(f"atomic-output: 임시 파일이 남았습니다: {leftovers}")
    print("output-path-safety: PASS; symlink rejected and hardlink atomically replaced")


def main() -> None:
    valid_report = (FIXTURE_ROOT / "valid-mobile-review.md").read_text(encoding="utf-8")
    release_fixture = FIXTURE_ROOT / "valid-release-checklist.md"
    blank_template = (HARNESS_ROOT / "templates" / "mobile-review.md").read_text(encoding="utf-8")
    with tempfile.TemporaryDirectory(prefix="mobile-validator-fixtures-") as directory:
        temp_root = Path(directory)
        for case in CASES:
            report = transformed_report(valid_report, case.transform)
            assert_case(case, report, release_fixture, temp_root)
        assert_case(
            Case("blank-template", False, "mobile-review.md가 템플릿 그대로입니다."),
            blank_template,
            release_fixture,
            temp_root,
        )
        assert_release_template_rejected(valid_report, temp_root)
        assert_json_contract(temp_root / "valid")
        assert_review_score_contract(temp_root / "valid")
        assert_project_boundary(temp_root / "valid", temp_root)
        assert_symlink_boundary(valid_report, release_fixture, temp_root)
        assert_score_and_release_symlinks(valid_report, release_fixture, temp_root)
        assert_input_hardlinks(valid_report, release_fixture, temp_root)
        assert_review_score_required(valid_report, release_fixture, temp_root)
        assert_output_input_collisions(temp_root / "valid", release_fixture)
        assert_output_path_safety(temp_root / "valid", temp_root)
        assert_mobile_plan_path_safety(temp_root)

    print("mobile validator fixture smoke: PASS")


if __name__ == "__main__":
    main()
