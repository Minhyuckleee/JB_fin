# AI Project Harness Guide

## 목적

이 문서는 AI 프로젝트를 요구사항, 데이터, 프롬프트, 실험, 실행 결과, 평가, 의사결정이 재현 가능하고 추적 가능한 형태로 남도록 운영하기 위한 하네스 지침서이다.

핵심 질문은 다음이다.

- 무엇을 만들고 어떻게 성공을 판단하는가?
- 원본, 가공 데이터, 산출물을 어떻게 분리하는가?
- 실험과 실행 결과를 어떻게 다시 재현하는가?
- 검증 결과와 의사결정을 어디에 남기는가?

## 문서 역할

```text
aiagent/AGENTS.md
  전역 에이전트 행동 규칙
  추측 금지, 단순성, 외과적 변경, 검증 중심 실행

aiagent/Harness.md
  프로젝트 운영 지침
  요구사항, 데이터, 프롬프트, 실험, 평가, 기록 관리 방식

PROJECT_REQUIREMENTS.md
  현재 프로젝트의 목표, 제약, 성공 기준
  사용자가 정의한 요구사항의 source of truth
```

프로젝트별 실험 규칙과 폴더별 상세 규칙은 `AGENTS.md`에 길게 넣지 않는다. `Harness.md`, `PROJECT_REQUIREMENTS.md`, 실험 config, log, README, 필요 시 `AGENTS.override.md`에 둔다.

## 핵심 원칙

- 요구사항을 먼저 고정한다: 문제 정의, 입력/출력, 제약, 성공 기준, 제출물 형식을 `PROJECT_REQUIREMENTS.md`에 기록한다.
- 원본과 산출물을 분리한다: 원본은 보존하고, 가공 데이터와 실행 결과는 재생성 가능하게 만든다.
- 실험은 파일로 정의한다: 목적, 입력, 모델/알고리즘, 프롬프트/설정, 실행 명령, 평가 지표를 남긴다.
- 검증은 주장보다 강하다: 테스트, 빌드, 린트, 스키마 검증, 데이터 검증, 평가 스크립트 등 실행 가능한 확인을 우선한다.
- 결과는 증거와 함께 남긴다: 실행 시각, 명령, config, 데이터/프롬프트/모델 버전, 출력, metric, 실패 로그, 다음 액션을 기록한다.

## 추천 구조

프로젝트 성격에 맞게 필요한 것만 만든다.

```text
project/
  PROJECT_REQUIREMENTS.md
  aiagent/
    AGENTS.md
    Harness.md

  docs/
    decisions/
    reports/

  data/
    raw/
    processed/
    external/

  prompts/
    versions/
    evaluations/

  experiments/
    configs/
    notes/

  runs/
    YYYYMMDD_HHMMSS_experiment_name/

  evals/
    scripts/
    reports/

  src/
  tests/
  scripts/
```

역할 기준:

- `docs/`: 설계, 의사결정, 최종 보고서
- `data/raw/`: 수정하지 않는 원본 데이터
- `data/processed/`: 재생성 가능한 가공 데이터
- `prompts/`: 실험에 사용한 프롬프트 버전
- `experiments/`: 실험 config와 가설/노트
- `runs/`: 덮어쓰지 않는 실행 결과와 로그
- `evals/`: 평가 코드와 평가 보고서
- `src/`, `tests/`, `scripts/`: 구현 코드, 테스트, 실행 도구

## 시작 절차

1. `PROJECT_REQUIREMENTS.md`에 문제 정의와 성공 기준을 쓴다.
2. 데이터 소스, 접근 제약, 산출물 저장 방식을 정한다.
3. 필요한 폴더만 만든다.
4. 첫 baseline 실험과 최소 평가 기준을 정의한다.
5. 실행 결과를 `runs/`에 저장한다.
6. 평가 결과를 바탕으로 다음 실험 가설을 정한다.
7. 반복되는 실패나 중요한 결정은 문서와 검증 게이트에 반영한다.

## 실험 루프

```text
요구사항 확인
  -> 가설 정의
  -> 실험 config 작성
  -> 실행
  -> 결과 저장
  -> 평가
  -> 결정 기록
  -> 다음 실험 설계
```

각 단계는 파일이나 로그로 흔적이 남아야 한다.

## 실험 config

프로젝트에 맞게 조정하되, 다음 필드를 출발점으로 삼는다.

```yaml
id: baseline_001
goal: "첫 baseline 성능 확인"
data:
  input: "data/processed/train_v1.csv"
  split: "validation_v1"
model:
  name: "model-or-method-name"
  params: {}
prompt:
  path: "prompts/versions/prompt_v1.md"
execution:
  command: "python scripts/run_experiment.py --config experiments/configs/baseline_001.yaml"
evaluation:
  metrics: ["accuracy", "f1"]
outputs:
  run_dir: "runs/"
notes:
  hypothesis: "초기 기준 성능을 확인한다."
```

## 실행 결과

각 run directory에는 가능한 한 다음을 둔다.

```text
runs/YYYYMMDD_HHMMSS_experiment_name/
  config.yaml
  command.txt
  stdout.log
  stderr.log
  outputs/
  metrics.json
  summary.md
```

`summary.md`에는 실험 목적, 변경점, 핵심 결과, 이상 징후, 다음 액션을 간단히 적는다.

## 평가 설계

프로젝트 유형에 맞는 검증 기준을 고른다.

- 예측 모델: split 기준, leakage 방지, metric 정의, baseline 비교, seed/재현성
- RAG: 문서 수집 기준, chunking 방식, retrieval metric, 답변 품질, hallucination, source citation
- 에이전트: task success rate, tool call 정확성, latency/비용, 실패 유형, 사람 개입 기준
- API/서비스: request/response schema, contract test, latency, error case, observability

검증을 실행할 수 없다면 이유와 대체 확인 방법을 기록한다.

## 도구 경계

AI나 자동화 도구가 접근하거나 수정할 수 있는 범위를 프로젝트별로 정한다.

예시:

- `data/raw/`는 읽기 전용이다.
- 기존 `runs/` 결과는 덮어쓰지 않는다.
- production key, secret, 개인정보는 읽거나 출력하지 않는다.
- 외부 API 호출은 비용과 개인정보 영향을 확인한 뒤 실행한다.
- DB 작업은 기본적으로 read-only로 시작한다.
- 삭제 작업은 명시적 승인 후 수행한다.

## AGENTS.override.md

`AGENTS.override.md`는 특정 폴더에서만 적용되는 로컬 운영 규칙이다. 전역 행동 규칙을 반복하지 않고, 해당 폴더의 안전 경계, 허용/금지 작업, 완료 기준, 검증 방법만 적는다.

규칙 적용 순서:

```text
1. 사용자의 명시적 지시
2. aiagent/AGENTS.md의 전역 행동 규칙
3. 현재 작업 대상 폴더의 AGENTS.override.md
4. aiagent/Harness.md의 하네스 운영 지침
5. README, log, config 등 기타 프로젝트 문서
```

override는 전역 규칙을 대체하지 않고 보강한다. 충돌이 작업 범위, 데이터 안전성, 검증 가능성에 영향을 주면 사용자에게 확인한다.

사용을 권장하는 경우:

- 원본 데이터, 제출물, 최종 산출물을 보호해야 한다.
- 평가 기준, metric, benchmark를 관리한다.
- 외부 API, 비용, 배포, 비밀정보와 연결된다.
- 실험 결과를 덮어쓰면 안 된다.
- 사람이 만든 산출물과 자동 생성 산출물이 섞이면 위험하다.

권장 위치 예시:

```text
data/raw/AGENTS.override.md
submissions/AGENTS.override.md
evals/AGENTS.override.md
scripts/AGENTS.override.md
selected_model/AGENTS.override.md
deploy/AGENTS.override.md
secrets/AGENTS.override.md
```

작성 형식:

```text
# AGENTS.override.md

1. 폴더 역할
2. 허용되는 작업
3. 금지되는 작업
4. 완료 기준
5. 검증 방법
```

예시:

```text
data/raw/AGENTS.override.md
- 역할: 원본 데이터 보관
- 허용: 목록 확인, 스키마 확인, row count 확인, 파생 데이터 생성
- 금지: 원본 수정, 파일명 변경, 삭제, 인코딩/줄바꿈 변환
- 완료: 파생 산출물은 data/processed/에 저장하고 사용 원본을 기록
- 검증: 작업 전후 원본 파일 개수와 크기 확인
```

## 피드백 루프

반복되는 문제는 개인 기억에 맡기지 않고 하네스에 반영한다.

기록 항목:

- 발생한 문제
- 원인과 영향
- 재발 방지책
- 추가한 검증
- 바꾼 문서 또는 스크립트

예시:

```md
date: 2026-05-20

- 문제: 이전 run 결과를 덮어쓸 뻔했다.
- 원인: run directory 이름이 고정되어 있었다.
- 조치: timestamp 기반 run directory 사용.
- 추가 검증: run directory가 이미 존재하면 실패.
```

## 완료 기준

하네스 관점에서 완료된 작업은 다음을 만족한다.

- 요구사항과 연결되어 있다.
- 입력, 출력, 실행 방법이 명확하다.
- 결과와 검증 결과가 저장되어 있다.
- 남은 위험이나 미검증 항목이 명시되어 있다.
- 중요한 결정이 문서에 반영되어 있다.

## 성숙도 단계

- Level 0: 임시 작업. 채팅과 수동 실행에 의존한다.
- Level 1: 문서화된 작업. 요구사항과 실행 방법이 남아 있다.
- Level 2: 구조화된 실험. config, run directory, 평가 결과가 분리되어 있다.
- Level 3: 자동 검증 하네스. 테스트, 평가 스크립트, 포맷 검증이 자동화되어 있다.
- Level 4: 운영 가능한 하네스. CI, 리포트, 의사결정 기록, 피드백 루프가 함께 작동한다.

## 사용 예시

```text
PROJECT_REQUIREMENTS.md와 aiagent/Harness.md를 기준으로
baseline 실험 구조를 설계해줘.

바로 파일을 만들기 전에 필요한 폴더, override, 검증 게이트,
로그 파일, 확인 질문을 먼저 제안해줘.
```

## 한 줄 요약

하네스 엔지니어링은 AI 프로젝트를 요구사항, 실험, 실행, 평가, 기록이 연결된 재현 가능한 시스템으로 운영하는 방법이다.
