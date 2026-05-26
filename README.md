# JB Fin AI Challenge

JB Fin AI Challenge 최종 제출용 repository입니다.

본 브랜치는 최종 제출 가능한 안정본만 포함합니다. 개발 중인 기능과 실험 코드는 `develop` 브랜치에서 관리하며, 대회 요강과 아이디어 원문 등 참고자료는 `reference` 브랜치에서 관리합니다.

## Branch Role

- `master`: 최종 제출용 안정본
- `develop`: 기능 개발 및 통합 브랜치
- `reference`: 대회 요강, 아이디어 원문, 외부 리서치 자료 보관

## Project Overview

> 프로젝트 주제가 확정된 뒤 작성합니다.

작성 예정 항목:

- 서비스명
- 선택 주제
- 문제 정의
- 핵심 솔루션
- 주요 기능
- 기대 효과

## Repository Structure

```text
/
  docs/        프로젝트 설명, 아키텍처, 데이터 출처, 평가 결과
  backend/     백엔드 API 및 Agent 로직
  frontend/    데모 UI
  data/        제출용 샘플 데이터 및 정제 데이터
  scripts/     실행 및 데이터 준비 스크립트
  evals/       평가 시나리오 및 검증 결과
  proposals/   제출용 제안서 및 기능명세서
```

## Quick Start

> 최종 실행 방법은 제출 전 작성합니다.

예상 구성:

```bash
# Backend
cd backend
# run backend server

# Frontend
cd frontend
# run frontend server
```

## Demo Scenario

> 최종 시연 시나리오는 제출 전 작성합니다.

작성 예정 항목:

1. 사용자 입력
2. Agent 판단 과정
3. Tool/RAG 호출 결과
4. 최종 응답
5. 직원용 리포트 또는 결과 화면

## Submission Artifacts

> 최종 제출 산출물 확정 후 작성합니다.

예상 산출물:

- MVP 제안서 PDF
- 기능명세서 PDF
- 시연영상 링크
- 실행 코드
- 데모/배포 링크

## Notes

- 본 브랜치에는 최종 제출 가능한 안정본만 반영합니다.
- 개발 중 변경사항은 `develop` 브랜치에서 관리합니다.
- 원본 참고자료는 `reference` 브랜치에서 관리합니다.
