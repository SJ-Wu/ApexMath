# ApexMath — 峰數學能力檢測平台

## 專案概述

「峰數學能力檢測平台」是一套數學能力診斷系統，核心圍繞三大要素：**學生**、**知識點**、**數學素養**。
系統透過測驗卷評量學生的知識點能力與數學素養，再由 AI 產出弱點分析與強化建議。

**目前版本**：V0.1（2026/03/01 實作完成，支援三角色、驗證碼機制、PostgreSQL 持久化）

## 技術棧

- **後端框架**：FastAPI (Python 3.13)
- **資料庫**：PostgreSQL + SQLAlchemy async (asyncpg)
- **認證**：JWT (python-jose) + bcrypt (passlib)
- **資料庫遷移**：Alembic
- **組態管理**：pydantic-settings
- **前端框架**：Vue 3 + Element Plus + ECharts
- **前端建構**：Vite
- **部署**：Docker Compose / Render
- **虛擬環境**：`.venv/`（位於專案根目錄）
- **入口檔案**：`api/main.py`

## 專案結構

```
ApexMath/
├── api/                              # FastAPI 後端
│   ├── main.py                       # 應用程式入口（lifespan 管理）
│   ├── pyproject.toml                # Python 依賴
│   ├── Dockerfile
│   ├── alembic.ini                   # Alembic 遷移設定
│   ├── alembic/                      # 遷移檔案
│   │   ├── env.py
│   │   └── versions/
│   │       └── 001_initial_schema.py
│   ├── app/
│   │   ├── core/
│   │   │   └── config.py            # 集中組態（pydantic-settings）
│   │   ├── db/
│   │   │   ├── engine.py            # async engine + session factory
│   │   │   ├── models.py            # SQLAlchemy ORM 模型（5 張表）
│   │   │   └── seed.py              # 初始資料（admin + 小五試卷）
│   │   ├── auth/
│   │   │   ├── security.py          # JWT + bcrypt 工具
│   │   │   ├── dependencies.py      # get_current_user, require_role
│   │   │   └── router.py            # /api/auth/login, /api/auth/verify-code
│   │   ├── api/
│   │   │   ├── router.py            # /api/exams/* — 公開端點（原有）
│   │   │   ├── schemas.py           # 請求/回應 Pydantic 模型
│   │   │   ├── teacher_router.py    # /api/teacher/* — 教師功能
│   │   │   ├── student_router.py    # /api/student/* — 學生測驗流程
│   │   │   └── admin_router.py      # /api/admin/* — 管理者功能
│   │   ├── domain/
│   │   │   ├── models.py            # 核心領域模型（Pydantic）
│   │   │   ├── scoring.py           # 純函數評分引擎（不可修改）
│   │   │   ├── analysis_models.py   # AIAnalysis 模型
│   │   │   └── exam_registry.py     # 記憶體內試卷管理
│   │   ├── services/
│   │   │   ├── analysis_service.py  # LLM prompt + AI 分析
│   │   │   ├── llm_client.py        # OpenAI 客戶端
│   │   │   └── verification_service.py  # 驗證碼生成邏輯
│   │   ├── repositories/
│   │   │   ├── verification_repo.py # 驗證碼資料存取
│   │   │   └── session_repo.py      # 測驗 session 資料存取
│   │   └── data/
│   │       └── grade5_entrance.py   # 小五入班檢測試卷定義
│   └── tests/                        # 73 個測試（全部通過）
│       ├── conftest.py              # create_test_app() — 不依賴 DB
│       ├── test_api.py
│       ├── test_analysis_api.py
│       ├── test_scoring.py
│       ├── test_models.py
│       ├── test_exam_registry.py
│       └── test_analysis_service.py
├── web/                              # Vue 3 前端
│   ├── src/
│   │   ├── main.js                  # 入口（Element Plus + Router）
│   │   ├── App.vue
│   │   ├── router/index.js          # 路由 + navigation guard
│   │   ├── api/
│   │   │   ├── index.js             # Axios 實例（自動附帶 JWT）
│   │   │   ├── exam.js              # 公開試卷 API
│   │   │   ├── teacher.js           # 教師 API
│   │   │   ├── student.js           # 學生 API
│   │   │   └── admin.js             # 管理者 API
│   │   ├── composables/
│   │   │   ├── useAuth.js           # JWT token + 角色管理
│   │   │   └── useStudentSession.js # 學生 session 管理
│   │   ├── layouts/
│   │   │   ├── AdminLayout.vue      # 管理者後台框架
│   │   │   ├── TeacherLayout.vue    # 教師後台框架
│   │   │   └── StudentLayout.vue    # 學生測驗框架
│   │   ├── views/
│   │   │   ├── LoginView.vue        # 帳密登入頁
│   │   │   ├── VerifyCodeView.vue   # 驗證碼輸入頁
│   │   │   ├── ExamListView.vue     # 測驗卷列表（原有）
│   │   │   ├── ExamScoringView.vue  # 老師評分（原有）
│   │   │   ├── ResultReportView.vue # 結果報告（原有）
│   │   │   ├── admin/               # 管理者頁面
│   │   │   ├── teacher/             # 教師頁面
│   │   │   └── student/             # 學生頁面
│   │   ├── components/
│   │   │   ├── charts/              # KnowledgeBarChart, LiteracyRadarChart
│   │   │   └── exam/                # SectionScoring
│   │   └── utils/
│   │       └── chartOptions.js
│   ├── package.json
│   ├── vite.config.js
│   └── Dockerfile
├── docker-compose.yml                # PostgreSQL + API + Web
├── render.yaml                       # Render 部署藍圖（含 DB）
├── .env.example                      # 環境變數範本
└── .github/workflows/ci.yml          # CI/CD

```

## 資料庫 Schema

| 表名 | 欄位概要 | 用途 |
|------|----------|------|
| `users` | id, username, hashed_password, display_name, role, is_active | 管理者 / 教師帳號 |
| `exam_templates` | id, exam_id, name, template_data(JSONB), is_active | 試卷模板 |
| `teacher_exam_access` | id, teacher_id, exam_template_id | 教師試卷權限 |
| `verification_codes` | id, code, prefix, student_number, teacher_id, exam_template_id, status | 驗證碼（unused→in_progress→completed） |
| `exam_sessions` | id, verification_code_id, student_name, exam_id, answers, results, assessment, ai_analysis(JSONB), status | 學生測驗紀錄 |

## API 路由

| 路由前綴 | 用途 | 認證 |
|----------|------|------|
| `POST /api/auth/login` | 管理者/教師登入 | 公開 |
| `POST /api/auth/verify-code` | 學生驗證碼驗證 | 公開 |
| `GET/POST /api/exams/*` | 試卷查詢 + 評分 | 公開 |
| `GET/POST /api/teacher/*` | 驗證碼管理、成績查看、手動評分 | teacher / admin |
| `GET/POST /api/student/*` | 取得試卷、提交作答、查看結果 | student session |
| `GET/POST/PUT/DELETE /api/admin/*` | 教師 CRUD、試卷管理、統計 | admin |

## 前端路由

| 路徑 | 用途 | 認證 |
|------|------|------|
| `/login` | 管理者/教師登入 | 訪客 |
| `/verify` | 學生驗證碼輸入 | 訪客 |
| `/admin/*` | 管理者後台（總覽、試卷、教師、學生） | admin |
| `/teacher/*` | 教師後台（總覽、驗證碼、評分、成績） | teacher |
| `/student/exam/:sessionId` | 學生線上作答 | student session |
| `/student/result/:sessionId` | 學生結果報告 | student session |
| `/`、`/exam/:examId`、`/result` | 原有公開評分流程（向下相容） | 公開 |

## 領域模型

### 核心實體

| 實體 | 屬性 | 說明 |
|------|------|------|
| **學生 (Student)** | 學年、知識點清單、數學素養能力分佈 | 受測對象，記錄已習得能力 |
| **知識點 (KnowledgePoint)** | 名稱、前後置關係 | 如正整數、小數、分數，知識點之間具有承先啟後的依賴關係 |
| **數學素養 (MathLiteracy)** | 名稱 | 概念理解、計算流暢度、情境策略與脈絡素養、邏輯推理 |
| **題目組 (QuestionGroup)** | 知識點(含分數)、數學素養 | 每題涵蓋特定知識點，解題過程可訓練特定數學素養 |
| **測驗卷 (Exam)** | 學年門檻、題組清單、檔案連結 | 需滿足學年條件才可使用，包含多個題目組 |
| **AI分析 (AIAnalysis)** | 弱點分析、強化建議 | 根據知識點能力+數學素養雷達圖產出 |

### 知識點能力（九大類 + 資優挑戰）

能力值範圍：**0 ~ 5 分**

| # | 知識點類別 | 測驗卷對應單元 |
|---|----------|-------------|
| 1 | 正整數 | 一、正整數運算思維 (5題) |
| 2 | 小數 | 二、小數思維 (5題) |
| 3 | 分數 | 三、分數思維 (5題) |
| 4 | 容積 | 四、容積與面積問題 (4題) |
| 5 | 距離問題 | 五、距離問題與單位換算 (5題) |
| 6 | 時間問題 | 六、時間問題 (5題) |
| 7 | 解題策略 | 七、應用問題解題策略 (5題) |
| 8 | 規律推演 | 八、規律推演 (5題) |
| 9 | 面積/立方體 | 九、面積與立方體問題 (2大題) |
| 10 | 資優挑戰 | 資優思維 (3題) |

### 數學素養能力（雷達圖四象限）

| 象限 | 說明 |
|------|------|
| 概念理解 | 對數學概念的掌握程度 |
| 計算流暢度 | 運算的正確性與效率 |
| 情境策略與脈絡素養 | 將數學應用於實際情境的能力 |
| 邏輯推理 | 分析規律、推導結論的能力 |

## 分析流程

```
測驗卷（學生作答）
    │
    ├──→ 知識點能力評估（長條圖，0~5分 × 10類）
    │         │
    │         └──→ AI 分析與建議
    │                   ├─ 弱點分析
    │                   └─ 強化建議
    │
    └──→ 數學素養能力評估（雷達圖，4象限）
              │
              └──→ AI 分析與建議（同上合併）
```

## 關鍵設計決策

1. **scoring.py 純函數引擎不可修改** — 所有新功能圍繞它包裝
2. **ExamRegistry（記憶體）保留** — 評分端點使用 registry，避免每次查 DB
3. **JSONB 儲存試卷與成績** — 避免複雜 JOIN，scoring engine 直接消費 Pydantic model
4. **JWT 認證** — 適合 Render 無狀態部署，免 Redis
5. **學生無帳號** — 以驗證碼 + 姓名識別，符合一次性測驗需求
6. **單一 users 表 + role 欄位** — admin / teacher 共用，權限差異用 `require_role()` 處理
7. **測試不依賴 DB** — `tests/conftest.py` 的 `create_test_app()` 直接設定 `app.state`

## 開發指令

```bash
# 後端測試
cd api && ../.venv/bin/pytest -v --tb=short

# 前端建構
cd web && npm run build

# 本地開發（需先啟動 PostgreSQL）
docker compose up postgres -d
cd api && ../.venv/bin/uvicorn main:app --reload
cd web && npm run dev

# 完整本地部署
docker compose up
```

## 開發注意事項

- 知識點之間有**前後置依賴關係**（如：先學正整數 → 再學小數 → 再學分數），系統需建模此關係
- 每道題目同時關聯「知識點」與「數學素養」，解題歷程決定給分
- AI 分析需整合知識點能力（量化）與數學素養（雷達圖）兩套數據
- 測驗卷需支援不同學年，具備學年門檻控制
- 報告生成需支援圖表（長條圖 + 雷達圖）+ 文字（AI 建議）
- `pyproject.toml` 需設定 `[tool.setuptools.packages.find] include = ["app*"]` 以排除 alembic 目錄
- Render 部署時 `DATABASE_URL` 的 `postgres://` 前綴會自動轉換為 `postgresql+asyncpg://`
