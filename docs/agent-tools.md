# Agent Tool Stack

체류 외국인 대상 대출/금융상품 숏폼 마케팅 AI Agent의 tool/model 선택 문서.

기준 자료:

- `../AI 마케팅 에이전트 기술 스택 조사.pdf`
- 수치와 모델명은 PDF 조사 결과 기준이다. 실제 구현 전 공식 문서, 가격표, API 제공 여부는 재확인한다.

## 1. 최종 선택

MVP는 **Single Agent + Tool Calling** 구조로 시작한다. Agent가 모든 일을 직접 생성하지 않고, 전문 tool들이 JSON state를 주고받는 구조로 설계한다.

```text
Orchestration : LangGraph
Parsing       : LlamaParse Cost-effective
RAG/Vector DB : pgvector + Hybrid Search
Embedding     : Upstage Solar-embedding-1-large
Target        : Rule filter + Gemini 3.1 Flash-Lite
Script        : Claude 4.6 Sonnet
Translation   : Gemini 3.1 Flash-Lite
Compliance    : GPT-5.4 + rules + RAG evidence
TTS           : OpenAI TTS tts-1
Image         : Ideogram v3
Subtitle      : OpenAI Whisper API or Deepgram Nova-2
Video         : Remotion + FFmpeg
```

핵심 판단:

- 금융 문구는 RAG citation으로 통제한다.
- Compliance는 LLM 단독이 아니라 `rules + RAG evidence + LLM review`로 검증한다.
- 번역 후에도 숫자, 조건, 금리, 유의문구 보존 여부를 재검증한다.
- 영상은 Sora/Veo/Runway가 아니라 Remotion + FFmpeg로 조립한다.
- 브랜드 로고, 법적 고지문, CTA 텍스트는 생성형 이미지/영상 모델에 맡기지 않는다.

## 2. Architecture

```text
Single Marketing Agent
├─ Document Parsing Tool
├─ RAG Search Tool
├─ Target Matching Tool
├─ Script Planning & Generation Tool
├─ Translation / Localization Tool
├─ Compliance & Fact Check Tool
├─ TTS Tool
├─ Image Generation Tool
├─ Subtitle Tool
└─ Video Editing Tool
```

`Campaign Planning Tool`은 독립 tool로 두지 않는다. MVP에서는 `Script Planning & Generation Tool`의 prompt preparation 단계로 흡수한다. 별도 tool로 분리하면 latency와 토큰 비용이 늘어난다.

## 3. MVP Stack

| Tool | MVP 선택 | 비용 | 속도/Latency | 성능 근거 | 판단 |
| --- | --- | --- | --- | --- | --- |
| Orchestration | LangGraph | 오픈소스 | workflow overhead | state 전이/순환 제어 | MVP 선택 |
| Parsing | LlamaParse Cost-effective | `$3.75 / 1K pages` | API 비동기 | Agentic 기준 `84.9%` | MVP 선택 |
| Vector DB | pgvector | `$120~$200/mo` | p50 `5ms` | PostgreSQL 통합 용이 | MVP 선택 |
| Embedding | Upstage Solar | `$0.10 / 1M tokens` | API | Kor-IR NDCG@10 `83.61` | MVP 선택 |
| Target | Gemini 3.1 Flash-Lite | input `$0.25`, output `$1.50` / 1M tokens | 빠름 | GPQA `86.9%` | MVP 선택 |
| Script | Claude 4.6 Sonnet | input `$3`, output `$15` / 1M tokens | 중간 | SWE-bench `80.8%`, GPQA `74.1%` | MVP 선택 |
| Translation | Gemini 3.1 Flash-Lite | 시간당 약 `< $0.01` 추산 | 빠름 | 저자원 언어 처리 안정 | MVP 선택 |
| Compliance | GPT-5.4 | 확인 필요 | 중간 | GPQA `92.0%`, OSWorld `75.0%` | MVP 선택 |
| TTS | OpenAI TTS tts-1 | `$15 / 1M chars` | p50 `250ms` | MOS `3.9` | MVP 선택 |
| Image | Ideogram v3 | `$0.03~$0.05 / image` | 중간 | text rendering `5/5` | MVP 선택 |
| Subtitle | Whisper API | `$0.36 / audio hour` | 중간 | 범용 STT 안정성 | MVP 선택 |
| Video | Remotion + FFmpeg | 서버 비용 | 렌더링 시간 필요 | 결정론적 제어 O | MVP 선택 |

## 4. Advanced Stack

| Tool | 고도화 선택 | 비용/속도 | 성능 근거 | 사용 시점 |
| --- | --- | --- | --- | --- |
| Parsing | Docling | open source, `3.3 pages/sec` | TableFormer `97.9%` | 망분리/로컬 처리 필요 시 |
| Vector DB | Qdrant | `$150~$280/mo`, p50 `3ms` | 빠른 scale-out | 대규모 문서/로그 검색 |
| Translation | DeepSeek V4 Pro | output `$0.87 / 1M tokens`, 시간당 약 `$0.005` | 대량 번역 초저비용 | 대량 캠페인 운영 |
| TTS | ElevenLabs | `$120~$165 / 1M chars`, p50 `380ms` | MOS `4.3` | 고품질 브랜딩 음성 |
| Image | Flux 2 Pro | `$0.03~$0.06 / image` | photorealism `5/5` | 고품질 인물/배경 B-roll |

## 5. Tool별 비교

### 5.1 Document Parsing Tool

목적: PDF, 상품 설명서, 약관, 광고 가이드라인을 RAG용 chunk로 변환한다.

| 순위 | 후보 | 운영방식 | 비용 | 속도 | 성능 | MVP 적합성 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | LlamaParse | API | `$3.75 / 1K pages` | API 비동기 | Agentic 기준 `84.9%` | 높음 |
| 2 | Docling | open source, local | 무료, 인프라 비용 별도 | `3.3 pages/sec` | TableFormer `97.9%` | 중간 |
| 3 | Azure Document Intelligence | cloud API | `$10 / 1K pages`, custom `$30 / 1K` | API | 폼 기반 우수 | 중간 |
| 4 | Google Document AI | cloud API | Form Parser `$30 / 1K pages` | API | OCR/Form 우수 | 낮음 |
| 5 | Unstructured | managed API | `$2.66 / hour` | API | 다양한 포맷, 병합 표 취약 | 낮음 |

우리 선택:

- MVP는 `LlamaParse Cost-effective`.
- 단순 PDF 테스트는 `PyMuPDF`로 보조 가능.
- 금융권 망분리/외부 전송 제한이 생기면 `Docling`으로 전환한다.

### 5.2 RAG Search Tool

목적: 상품 조건, 금리, 한도, 필요서류, 광고 유의문구를 citation과 함께 검색한다.

Vector DB:

| 순위 | 후보 | 운영방식 | 비용 | 속도 | 판단 |
| --- | --- | --- | --- | --- | --- |
| 1 | pgvector | PostgreSQL extension | `$120~$200/mo` | p50 `5ms` | MVP 선택 |
| 2 | Qdrant | open source/cloud | `$150~$280/mo` | p50 `3ms` | 고도화 |
| 3 | Milvus | open source/cloud | `$200~$350/mo` | p50 `4ms` | 대규모용 |
| 4 | Weaviate | open source/cloud | `$180~$320/mo` | p50 `8ms` | hybrid 내장 |
| 5 | Pinecone | managed cloud | `$800~$2,500/mo` | p50 `12ms` | 비싸서 MVP 부적합 |

Embedding:

| 순위 | 후보 | 운영방식 | 비용 | 성능 | 판단 |
| --- | --- | --- | --- | --- | --- |
| 1 | Upstage Solar-embedding-1-large | API | `$0.10 / 1M tokens` | Kor-IR NDCG@10 `83.61` | MVP 선택 |
| 2 | Cohere embed-multilingual-v3.0 | API | `$0.10 / 1M tokens` | NDCG@10 `80.79` | 대안 |
| 3 | Voyage-multilingual-2 | API | `$0.12 / 1M tokens` | NDCG@10 `79.69` | 대안 |
| 4 | BAAI/bge-m3 | open source | 무료, GPU 비용 | NDCG@10 `79.40` | 비용 절감 |
| 5 | OpenAI text-embedding-3-large | API | `$0.02 / 1M tokens` | NDCG@10 `73.74` | 저비용 대안 |

우리 선택:

- MVP는 `pgvector + Upstage Solar`.
- 검색 방식은 vector 단독이 아니라 BM25/keyword + vector hybrid.
- 모든 검색 결과는 `citation_id`, `source`, `page`, `text`를 포함한다.

### 5.3 Target Matching Tool

목적: 체류자격, 국적, 언어, 소득 등 메타데이터를 보고 고객군과 pain point를 라우팅한다.

| 순위 | 후보 | 운영방식 | 비용 | 성능 | 판단 |
| --- | --- | --- | --- | --- | --- |
| 1 | Gemini 3.1 Flash-Lite | API | input `$0.25`, output `$1.50` / 1M tokens | GPQA `86.9%` | MVP 선택 |
| 2 | DeepSeek V4 Pro | API | input `$0.435`, output `$0.87` / 1M tokens | MMLU `88.2%` | 벌크 처리 대안 |
| 3 | Gemini 3.5 Flash | API | input `$1.50`, output `$9.00` / 1M tokens | 1M+ context | 대량 프로필 입력 |
| 4 | GPT-5.2 Codex | API | input `$1.75`, output `$14.00` / 1M tokens | GPQA `92.4%` | JSON 안정성 필요 시 |
| 5 | Llama 3.1 8B | open source/API | 약 `$0.036 / 1M tokens` | 경량 분류 | 온프레미스 후보 |

우리 선택:

- 명확한 조건은 rule-based filter로 먼저 처리한다.
- LLM은 pain point와 message angle 생성에만 쓴다.
- MVP 모델은 `Gemini 3.1 Flash-Lite`.

### 5.4 Script Planning & Generation Tool

목적: 숏폼 장면, 내레이션, 화면 자막, CTA를 JSON으로 생성한다.

| 순위 | 후보 | 운영방식 | 비용 | 성능 | 판단 |
| --- | --- | --- | --- | --- | --- |
| 1 | Claude 4.6 Sonnet | API | input `$3`, output `$15` / 1M tokens | SWE-bench `80.8%`, GPQA `74.1%` | MVP 선택 |
| 2 | Gemini 3.1 Pro | API | input `$2`, output `$12` / 1M tokens | GPQA `94.3%`, SWE-bench `80.6%` | 대안 |
| 3 | GPT-5.4 | API | 예상 input `$5`, output `$25` / 1M tokens | GPQA `92.0%`, OSWorld `75.0%` | 비싸서 보류 |
| 4 | Claude 4.6 Opus | API | input `$5`, output `$25` / 1M tokens | SWE-bench `80.8%` | 과스펙 |
| 5 | GPT-4o | API | input `$2.50`, output `$10` / 1M tokens | 범용 | 최신 모델 대비 약함 |

우리 선택:

- `Claude 4.6 Sonnet`.
- 이유는 마케팅 카피 뉘앙스, prompt adherence, JSON 구조화 안정성.
- 비용이 부담되면 초안만 Sonnet, 변형안은 Flash-Lite로 처리한다.

### 5.5 Translation / Localization Tool

목적: 한국어 금융 광고를 베트남어, 태국어, 인도네시아어 등으로 번역하고 현지화한다.

| 순위 | 후보 | 운영방식 | 비용 | 특징 | 판단 |
| --- | --- | --- | --- | --- | --- |
| 1 | DeepSeek V4 Pro | API | 시간당 약 `$0.005`, output `$0.87 / 1M tokens` | 초저비용 대량 번역 | 고도화/대량 |
| 2 | Gemini 3.1 Flash-Lite | API | 시간당 `< $0.01`, output `$1.50 / 1M tokens` | 저자원 언어 안정 | MVP 선택 |
| 3 | Claude 4.5 Haiku | API | output `$5 / 1M tokens` | 톤앤매너 유지 | 브랜드 번역 |
| 4 | DeepL Pro API | API | `$25 / 1M chars`, 시간당 약 `$4.05` | 전통적 번역 품질 | baseline |
| 5 | Google Cloud Translation | API | `$20 / 1M chars`, 시간당 약 `$3.24` | 133개 언어 | 직역 성향 |

우리 선택:

- MVP는 `Gemini 3.1 Flash-Lite`.
- 대량 운영에서는 `DeepSeek V4 Pro`.
- 번역 후 숫자, 조건, 유의문구 보존 여부를 반드시 재검증한다.

### 5.6 Compliance & Fact Check Tool

목적: 광고 표현 리스크와 상품정보 사실성 리스크를 검증한다.

| 순위 | 후보 | 운영방식 | 비용 | 성능 | 판단 |
| --- | --- | --- | --- | --- | --- |
| 1 | GPT-5.4 | API | 확인 필요 | GPQA `92.0%`, OSWorld `75.0%` | MVP 선택 |
| 2 | Gemini 3.1 Pro | API | input `$2`, output `$12` / 1M tokens | GPQA `94.3%`, 1M+ context | 긴 약관 검증 대안 |
| 3 | Claude 4.6 Opus | API | input `$5`, output `$25` / 1M tokens | GPQA `73.1%` | 심층 검토 |
| 4 | GPT-5.2 Codex | API | input `$1.75`, output `$14` / 1M tokens | GPQA `92.4%` | 수치/구조 검증 |
| 5 | Claude 4.6 Sonnet | API | input `$3`, output `$15` / 1M tokens | GPQA `74.1%` | 빠른 검토 |

우리 선택:

- MVP는 `GPT-5.4 + rules + RAG evidence`.
- 한국어 원문 검증 1회, 번역본 검증 1회로 총 2번 호출한다.
- 이 tool은 법률 자문이 아니라 위험 표현 flagging과 수정 제안만 한다.

검증 데이터 소스:

- 금융소비자보호법 제17조, 제22조 및 시행령
- 여신금융협회/은행연합회 대출광고 심의 가이드라인
- 내부 금융상품 핵심설명서 및 약관 DB

### 5.7 TTS Tool

목적: 최종 검수된 다국어 대본을 음성으로 변환한다.

| 순위 | 후보 | 운영방식 | 비용 | 속도 | 품질 | 판단 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | OpenAI TTS tts-1 | API | `$15 / 1M chars` | p50 `250ms` | MOS `3.9` | MVP 선택 |
| 2 | Google Cloud TTS | API | `$16 / 1M chars` | p50 `180ms` | MOS `3.6` | 대안 |
| 3 | ElevenLabs | API | `$120~$165 / 1M chars` | p50 `380ms`, P99 `700ms` | MOS `4.3` | 고도화 |
| 4 | Amazon Polly Neural | API | `$16 / 1M chars` | p50 `120ms` | 자연스러움 약함 | 보류 |
| 5 | Inworld AI TTS | API | 유동적 | p50 `<200ms` | 실시간 대화 특화 | 보류 |

우리 선택:

- MVP는 `OpenAI TTS tts-1`.
- ElevenLabs는 감정 표현이 중요해지는 고도화 단계 후보.

### 5.8 Image Generation Tool

목적: 장면별 B-roll, 캐릭터, 썸네일 이미지를 생성한다.

| 순위 | 후보 | 운영방식 | 비용 | 텍스트 | 실사화 | 판단 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Ideogram v3 | API | `$0.03~$0.05 / image` | `5/5` | `3/5` | MVP 선택 |
| 2 | Imagen 4 Ultra | API | `$0.04+ / image` | `5/5` | `4/5` | 대안 |
| 3 | Flux 2 Pro | API/local 후보 | `$0.03~$0.06 / image` | `2/5` | `5/5` | 고도화 |
| 4 | GPT Image 1.5 | API | `$0.009~$0.034 / image` | `4/5` | `4/5` | 비용 대안 |
| 5 | Midjourney V7 | web/API 제한 | `$60/mo Pro` | `3/5` | `5/5` | 자동화 부적합 |

우리 선택:

- MVP는 `Ideogram v3`.
- 광고성 텍스트가 필요한 썸네일에 강하다.
- 로고, 법적 고지문, CTA는 Remotion overlay로 합성한다.

### 5.9 Subtitle Tool

목적: TTS 오디오를 분석해 word-level timestamp와 자막 파일을 만든다.

| 순위 | 후보 | 운영방식 | 비용 | 특징 | 판단 |
| --- | --- | --- | --- | --- | --- |
| 1 | Deepgram Nova-2 | API | `$0.25 / audio hour` | 빠르고 저렴함 | 비용 최적 |
| 2 | OpenAI Whisper API | API | `$0.36 / audio hour` | OpenAI stack 통합 쉬움 | MVP 선택 |
| 3 | AssemblyAI | API | `$0.65 / audio hour` | 한국어/도메인 강점 | 대안 |
| 4 | Azure Speech STT | API | `$1.10 / audio hour` | 엔터프라이즈 보안 | 대안 |
| 5 | Google Speech-to-Text | API | `$1.44~$2.16 / audio hour` | 언어/사투리 폭 넓음 | 비용 높음 |

우리 선택:

- MVP는 `OpenAI Whisper API`.
- 비용 최적화가 필요하면 `Deepgram Nova-2`.
- 산출물은 `.srt`, `.vtt`, burned-in subtitle timing JSON.

### 5.10 Video Editing Tool

목적: 이미지, 음성, 자막, 로고, 고지문을 9:16 숏폼 영상으로 조립한다.

| 순위 | 후보 | 운영방식 | 결정론적 결과 | 코드 제어 | 판단 |
| --- | --- | --- | --- | --- | --- |
| 1 | Remotion + FFmpeg | open source, local/self-host | O | O | MVP 선택 |
| 2 | MoviePy | open source, local | O | O | Python 대안 |
| 3 | DaVinci Resolve Python API | local/server | O | O | 세팅 난이도 높음 |
| 4 | Runway Gen-3 / Luma | cloud API | X | X | 최종 산출물 부적합 |
| 5 | OpenAI Sora | cloud API | X | X | 로고/텍스트 일관성 문제 |

우리 선택:

- MVP는 `Remotion + FFmpeg`.
- 금융 고지문, 로고, 자막은 프레임 단위 통제가 필요하다.
- 생성형 비디오 API는 B-roll 정도로만 사용한다.

## 6. Common State Schema

도구 간 데이터 전달은 하나의 campaign state를 업데이트하는 방식으로 간다.

```json
{
  "campaign_id": "uuid-v4",
  "target_audience": {
    "nationality": "Vietnam",
    "visa_types": ["E-9", "F-4"],
    "pain_points": ["한국어 은행 앱 사용의 어려움"]
  },
  "product_info": {
    "product_name": "외국인 대상 금융상품",
    "interest_rate": null,
    "limit": null,
    "compliance_constraints": []
  },
  "rag_citations": [
    {
      "citation_id": "doc_401",
      "extracted_text": "..."
    }
  ],
  "script_data": {
    "original_korean": null,
    "translated_target": null
  },
  "media_assets": {
    "tts_audio_url": null,
    "word_timestamps": [],
    "background_image_urls": []
  },
  "compliance_status": {
    "is_approved": false,
    "violations_flagged": []
  }
}
```

## 7. 구현 우선순위

1. Document Parsing + RAG citation schema
2. Target Matching rule filter
3. Script Planning & Generation
4. Compliance & Fact Check 1차 검증
5. Translation / Localization
6. Compliance & Fact Check 2차 검증
7. TTS + Subtitle timestamp
8. Remotion + FFmpeg 영상 조립
9. Image generation 연결

## 8. 주요 리스크

- 다국어 번역 중 조건/숫자/유의문구가 바뀔 수 있다.
- 생성형 비디오 API는 로고, 고지문, 자막을 안정적으로 통제하기 어렵다.
- 순차 tool calling만 쓰면 latency가 길어진다.
- 외부 API로 내부 문서를 전송할 때 보안/망분리 문제가 생길 수 있다.

대응:

- `한국어 생성 -> 1차 검증 -> 번역 -> 역번역/일관성 검사 -> 2차 검증`
- 영상은 Remotion + FFmpeg로 결정론적 조립
- 번역, TTS, 이미지 생성은 worker로 병렬 처리
- 민감 문서는 마스킹하거나 로컬 parsing 대안 유지

## 9. 공식 확인 필요

- PDF 내 최신 모델명과 실제 API 제공 여부
- OpenAI, Anthropic, Gemini, DeepSeek 최신 가격표
- LlamaParse, Docling, Upstage Solar 벤치마크 최신성
- GPT-5.4, Gemini 3.1 Pro, Claude 4.6 계열의 공식 benchmark
- Ideogram, Flux, Imagen, GPT Image API 접근성과 상업적 사용 조건
- 금융광고 관련 공식 가이드라인 최신 버전
