# Backend Agent Scaffold

Single Marketing Agent의 초기 mock 구조입니다.

현재 목표:

- 각 tool을 독립 파일로 나눠 팀원이 맡은 부분만 수정할 수 있게 한다.
- 초기 단계에서는 유료 API를 호출하지 않는다.
- 모든 tool이 하나의 `CampaignState` 구조를 공유하게 한다.
- 이후 각 tool 함수를 LangGraph node로 옮기기 쉽게 만든다.

## 실행 방법

```bash
python -m backend.agent.graph
```

Windows PowerShell에서 한글이 깨져 보이면 UTF-8 출력을 먼저 설정합니다.

```powershell
$env:PYTHONIOENCODING='utf-8'
python -m backend.agent.graph
```

## Mock Pipeline 흐름

```text
Target Matching
-> Document Parsing
-> RAG Search
-> Script Generation
-> Compliance Check
-> Translation
-> Compliance Check
-> TTS
-> Image Generation
-> Subtitle Generation
-> Video Editing
```

## 주요 파일

```text
backend/agent/state.py
  공통 CampaignState schema

backend/agent/graph.py
  mock pipeline 실행부

backend/tools/document_parser.py
  문서 파싱 tool

backend/tools/rag_search.py
  RAG 검색 tool

backend/tools/target_matching.py
  타겟 라우팅 tool

backend/tools/script_generator.py
  숏폼 대본 생성 tool

backend/tools/translator.py
  번역/로컬라이징 tool

backend/tools/compliance_checker.py
  준법/사실성 검증 tool

backend/tools/tts.py
  음성 생성 tool

backend/tools/image_generator.py
  이미지 생성 tool

backend/tools/subtitle_generator.py
  자막 생성 tool

backend/tools/video_editor.py
  영상 조립 tool
```

## 개발 방식

각 tool은 아래 패턴을 따른다.

```python
def some_tool(state: CampaignState) -> CampaignState:
    ...
    return state
```

즉, tool은 `CampaignState`를 받아 필요한 값만 추가하거나 수정한 뒤 다시 반환한다.

나중에 실제 API를 붙일 때도 함수 입출력 형태는 유지하는 것이 좋다. 그래야 LangGraph 연결 시 변경 범위가 작아진다.
