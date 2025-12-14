# AI NPC Integration Framework for Game Development

게임 개발 환경에서 활용 가능한 LLM 기반 NPC 인지 프레임워크. Generative Agents, GenSim, AgentSociety 등 최신 LLM Agent 연구에서 제시되는 인지 구조를 게임 NPC에 적용하여 구현했다.

## 연구 배경

본 프레임워크는 최신 LLM 기반 에이전트 연구들(Generative Agents, GenSim, AgentSociety, MOSAIC 등)에서 공통적으로 사용되는 인지 파이프라인을 게임 개발 환경에 맞게 재구성한 것입니다. 이들 연구는 목적과 환경은 서로 다르지만, 공통적으로 **Observation → Memory → Reflection → Planning → Action**으로 구성된 인지 파이프라인을 사용합니다.

---

## 디렉터리 구조

```text
backend/
  app/
    api/v1/routes/    # API 엔드포인트
    core/             # 설정 및 핵심 기능
    agents/           # AI 에이전트 모듈 (query_builder, reflection, importance, run_turn)
    agents/tools/     # Tool 시스템 (행동 도구)
    memory/           # 메모리 관리
      mongo/          # MongoDB 레이어
      vector/         # FAISS 벡터 메모리
    prompts/          # 프롬프트 템플릿
    services/         # 외부 서비스 연동 (LLM, Embedding)
    schemas/          # Pydantic 스키마
    utils/            # 공통 유틸리티
  storage/
    faiss/
      indices/        # FAISS 인덱스 파일
      meta/           # 벡터 메타데이터 (JSONL)
  Dockerfile
  requirements.txt
  .env.example
```
---

## 핵심 인지 구조

### 1. Observation (지각)
게임 이벤트, 환경 상태, 플레이어 입력을 관찰한다. 이벤트는 JSON 형식으로 구조화되어 백엔드 서버로 전달된다.

```json
{
  "event_type": "player_interaction",
  "actor": "player_001",
  "action": "asked about the ring",
  "location": "shire",
  "details": {"dialogue": "What is this ring?"}
}
```

### 2. Memory System (기억 저장·검색)
이중 메모리 시스템을 구현했다:
- **단기 메모리**: MongoDB에 모든 관찰을 저장 (importance < 0.7)
- **장기 메모리**: 중요도가 높은 사건을 FAISS 벡터 인덱스로 승격 (importance >= 0.7)
- **벡터 검색**: OpenAI 임베딩을 사용하여 의미적으로 유사한 기억을 검색 (RAG 기반)

Generative Agents의 Memory Stream + Importance/Recency 기반 Retrieval 구조를 참고하여 구현했다.

### 3. Reflection / Reasoning (성찰·추론)
중요도, 감정 변화, 관계 변화, 퀘스트 상태 변화 등을 평가하여 선택적으로 반성을 트리거한다. Reflection 단계에서는 요약, 상황 재해석, 규칙 추출 과정을 거친다.

### 4. Planning / Decision-Making
LLM이 페르소나, 세계 지식, 검색된 기억을 바탕으로 행동을 계획한다. Function Calling을 통해 도구를 선택하고 실행한다.

### 5. Action
선택된 도구를 실행하여 게임 엔진에 전달한다. 대화, 이동, 전투, 퀘스트, 거래 등 다양한 행동을 지원한다.

## PeaCoK 기반 세계관·페르소나 지식 통합

PeaCoK(Persona Commonsense Knowledge) 연구에서 제안한 구조를 NPC 시스템의 장기기억 Layer로 완전히 통합했다:

### 핵심 기능

- **PersonaFact 시스템**: 페르소나 지식을 5개 dimension(characteristic, routine_habit, goal_plan, experience, relationship)으로 구조화
- **정적 페르소나 지식**: PeaCoK 데이터를 MongoDB + FAISS에 저장하여 검색 가능하게 만듦
- **동적 페르소나 업데이트**: Reflection을 통해 NPC가 경험을 통해 배운 새로운 페르소나 사실을 자동 생성
- **상황별 검색**: Dimension 기반 부스팅으로 상황에 맞는 페르소나 정보만 검색
- **프롬프트 통합**: Dimension별로 그룹화된 PersonaFacts를 LLM 프롬프트에 구조화하여 포함

### 사용 방법

**1. PeaCoK 데이터 임포트:**
```bash
# PeaCoK JSON 파일을 MongoDB에 임포트
python scripts/import_peacok.py --file data/peacok_kg.json

# FAISS에 인덱싱
python scripts/index_peacok_facts.py
```

**2. NPC 생성 및 사용:**
- NPC 생성 시 PersonaFact가 자동으로 연결됨
- 턴 실행 시 상황에 맞는 PersonaFacts가 자동 검색되어 프롬프트에 포함됨
- Reflection 트리거 시 새로운 PersonaFacts가 자동 생성 및 인덱싱됨

자세한 내용은 `PEACOK_IMPLEMENTATION.md` 참고.

## 기술 스택

**백엔드:**
- FastAPI (Python 3.12+)
- MongoDB (메모리 저장)
- FAISS (벡터 검색)
- OpenAI GPT-4o-mini (LLM)
- OpenAI text-embedding-3-large (임베딩)

**프론트엔드:**
- React 18 + TypeScript
- Vite
- Tailwind CSS
- shadcn/ui
- React Query

## 빠른 시작

### 1. 환경 설정

```bash
# 백엔드
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 환경 변수 설정
cp .env.example .env
# .env 파일에서 OPENAI_API_KEY 설정
```

```bash
# 프론트엔드
cd frontend
npm install
```

### 2. MongoDB 실행

```bash
# Docker
docker run -d -p 27017:27017 --name mongodb mongo:latest
```

### 3. 데이터 준비

**FAISS 인덱스 초기화:**
FAISS는 처음 시작할 때 빈 인덱스로 생성된다. 실제 데이터를 사용하려면:

1. **NPC 생성 및 턴 실행**: NPC가 턴을 실행하면 장기 메모리(importance >= 0.7)가 자동으로 FAISS에 벡터화됨

2. **또는 수동으로 인덱스 재구성**:
```bash
# MongoDB에 있는 데이터를 FAISS로 인덱싱
curl -X POST "http://localhost:8000/api/v1/vector/reindex?index_type=episodic"
curl -X POST "http://localhost:8000/api/v1/vector/reindex?index_type=persona"
curl -X POST "http://localhost:8000/api/v1/vector/reindex?index_type=world"
```

**인덱스 상태 확인:**
```bash
curl "http://localhost:8000/api/v1/vector/stats"
```

### 3-1. PeaCoK 데이터 다운로드 및 임포트 (선택사항)

PeaCoK 지식 그래프를 사용하려면:

**1. 데이터 다운로드:**
- Google Drive 링크: https://drive.google.com/file/d/1ZXH-vNmS-UWdEgp6DA4WtP_2HwwWFeMb/view?usp=sharing
- 다운로드한 파일을 `backend/data/peacok_kg.json`에 저장

**2. MongoDB에 임포트:**
```bash
# 스크립트는 삭제되었으므로, API를 통해 직접 임포트하거나
# MongoDB에 직접 데이터를 삽입해야 합니다
```

**3. FAISS 인덱스 초기화:**
```bash
# 벡터 인덱스 재구성 (MongoDB의 데이터를 FAISS로 인덱싱)
curl -X POST "http://localhost:8000/api/v1/vector/reindex?index_type=episodic"
curl -X POST "http://localhost:8000/api/v1/vector/reindex?index_type=persona"
curl -X POST "http://localhost:8000/api/v1/vector/reindex?index_type=world"
```

**참고:** PeaCoK 없이도 시스템은 정상 작동한다. PeaCoK를 사용하면 NPC의 페르소나 일관성이 향상된다.

### 4. 서버 실행

**터미널 1 (백엔드):**
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**터미널 2 (프론트엔드):**
```bash
cd frontend
npm run dev
```

### 5. 사용하기

1. 브라우저에서 `http://localhost:5173` 접속
2. "Create NPC" 클릭하여 NPC 생성
   - Name: `Gandalf`
   - Role: `Wizard`
   - Persona ID: `persona_test_001` (테스트 데이터에서 생성된 ID)
   - World ID: `world_test_001`
3. NPC 선택 후 대화 시작

## 시스템 아키텍처

### 인지 루프 상세

각 NPC 턴은 다음 단계를 거친다:

1. **관찰 저장**: 플레이어의 행동을 관찰하여 단기 메모리로 저장
2. **기억 검색**: 벡터 검색을 통해 관련된 과거 기억을 검색 (episodic, persona, world 지식)
3. **반성 결정**: 중요도, 감정 변화, 관계 변화 등을 평가하여 반성 여부 결정
4. **반성 실행**: 필요 시 LLM을 통해 사건을 반성하고 인사이트 도출
5. **계획 수립**: LLM이 페르소나, 세계 지식, 검색된 기억을 바탕으로 행동 계획
6. **행동 실행**: 선택된 도구를 실행하여 결과 생성
7. **중요도 평가**: 사건의 중요도를 평가하여 장기 메모리 승격 여부 결정
8. **추적 기록**: 전체 과정을 추론 추적으로 기록

### 메모리 시스템

- **단기 메모리**: 모든 관찰을 MongoDB에 저장 (importance < 0.7)
- **장기 메모리**: 중요도가 높은 사건을 FAISS 벡터 인덱스로 승격 (importance >= 0.7)
- **벡터 검색**: OpenAI 임베딩을 사용하여 의미적으로 유사한 기억을 검색
- **페르소나 지식 (PersonaFact)**:
  - **정적 facts**: PeaCoK 기반 페르소나 지식을 dimension별로 구조화하여 저장
  - **동적 facts**: Reflection을 통해 생성된 새로운 페르소나 사실
  - **Dimension 기반 부스팅**: 상황에 맞는 dimension의 facts가 우선 검색됨
- **세계 지식**: 세계관 규칙, 법칙, 사회 규범 등을 벡터 인덱스로 저장

### 도구 시스템

NPC는 다음 도구들을 사용할 수 있다:
- `talk`: 다른 캐릭터와 대화
- `move_to`: 위치 이동
- `attack`: 공격
- `defend`: 방어
- `start_quest`: 퀘스트 시작
- `update_quest`: 퀘스트 상태 업데이트
- `give_item`: 아이템 전달
- `trade`: 아이템 거래
- `wait`: 대기

## 프로젝트 구조

```
backend/
├── app/
│   ├── agents/          # 인지 에이전트 (턴 오케스트레이션, 반성, 중요도 평가)
│   ├── api/v1/routes/  # REST API 엔드포인트
│   ├── memory/          # 메모리 시스템 (MongoDB, FAISS)
│   │   ├── mongo/repository/  # MongoDB 저장소 (PersonaFactRepository 포함)
│   │   └── vector/      # 벡터 검색 (PersonaFact 인덱싱 포함)
│   ├── services/        # LLM, 임베딩 서비스
│   ├── schemas/         # Pydantic 스키마 (PersonaFact 포함)
│   ├── utils/           # 유틸리티 (peacok_parser 포함)
│   └── prompts/         # LLM 프롬프트 (Reflection에 PersonaFact 업데이트 포함)
├── scripts/             # 테스트 및 유틸리티 스크립트
│   ├── import_peacok.py      # PeaCoK 데이터 임포트
│   ├── index_peacok_facts.py # PersonaFact FAISS 인덱싱
│   └── test_peacok_integration.py  # 통합 테스트
└── requirements.txt

frontend/
├── src/
│   ├── components/      # React 컴포넌트
│   ├── pages/           # 페이지 컴포넌트
│   ├── services/        # API 클라이언트
│   └── types/           # TypeScript 타입 정의
└── package.json
```

## API 엔드포인트

주요 엔드포인트:

- `POST /api/v1/npc/create` - NPC 생성
- `GET /api/v1/npc/{npc_id}` - NPC 조회
- `POST /api/v1/npc/{npc_id}/turn` - NPC 턴 실행 (전체 인지 루프)
- `GET /api/v1/npc/{npc_id}/memory` - 메모리 조회
- `GET /api/v1/npc/{npc_id}/traces` - 추론 추적 조회
- `GET /api/v1/persona/{persona_id}` - 페르소나 조회
- `PUT /api/v1/persona/{persona_id}` - 페르소나 수정
- `POST /api/v1/vector/reindex` - 벡터 인덱스 재구성

### PeaCoK 데이터 다운로드

PeaCoK 지식 그래프 데이터는 다음 링크에서 다운로드 가능:
- **Google Drive 링크**: https://drive.google.com/file/d/1ZXH-vNmS-UWdEgp6DA4WtP_2HwwWFeMb/view?usp=sharing
- 다운로드한 파일을 `backend/data/peacok_kg.json`에 저장

자세한 내용은 루트 폴더의 `PEACOK_DOWNLOAD_GUIDE.md`를 참고하세요.

전체 API 문서는 `http://localhost:8000/docs`에서 확인 가능.

## 환경 변수

`.env` 파일에 다음 변수들을 설정:

```env
OPENAI_API_KEY=your_api_key_here
OPENAI_CHAT_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-large
OPENAI_EMBEDDING_DIM=3072

MONGODB_URI=mongodb://localhost:27017
MONGODB_DB=ai_npc_framework

FAISS_INDEX_DIR=storage/faiss/indices
FAISS_META_DIR=storage/faiss/meta
```

## 참고 문헌

본 프레임워크는 다음 연구들을 참고하여 설계했다:

- Park, J. S., et al. (2023). Generative Agents: Interactive Simulacra of Human Behavior.
- Tang, Jiakai, et al. (2025). Gensim: A general social simulation platform with large language model based agents.
- Gao, S., et al. (2023). PeaCoK: Persona Commonsense Knowledge for Consistent and Engaging Narratives.** (ACL 2023)
- Liu, Genglin, et al. (2025). Mosaic: Modeling social ai for content dissemination and regulation in multi-agent simulations.
- Piao, Jinghua, et al. (2025). Agentsociety: Large-scale simulation of llm-driven generative agents advances understanding of human behaviors and society.