# Python Project Template

## Intro

這個模板提供一套可快速擴充的專案骨架，所有實作僅以最小範例示範模組之間的串接方式。主要結構與職責如下：

```
.
├── README.md                 # 專案說明與操作指引
├── ai_requirements.md        # 規範文件（可放本專案的需求或規則）
├── CHANGELOG.md              # 版本變更紀錄
├── CONTRIBUTING.md           # 貢獻指南
├── config/                   # 設定檔及 logging 相關範本
├── data/
│   ├── raw/                  # 原始資料（含 .gitkeep）
│   └── processed/            # 處理後資料（含 .gitkeep）
├── docs/                     # 文件、架構描述與 ADR 範本
├── scripts/                  # 補助腳本（如 run_checks.py）
├── spec/                     # 需求或規格文件來源
├── src/
│   └── proj_name/
│       ├── __init__.py       # 專案對外公開 API（轉出 get_greeting 範例）
│       ├── __main__.py       # `python -m proj_name` 入口
│       ├── api/              # 對外公開的 API 層（示範 get_greeting）
│       ├── application/      # 應用層範例（demo 工作流程）
│       ├── cli/              # CLI 參考實作，串接核心與應用層
│       ├── core/             # 核心函式庫層（lib_example 展示可重用模組）
│       ├── config/           # 給程式碼使用的設定套件入口
│       ├── domain/           # 網域邏輯放置處
│       ├── infra/            # 外部資源或基礎建設介面
│       ├── services/         # 服務層或 use-case
│       └── utils/            # 共用工具
└── tests/                    # 測試骨架（unit/integration 子資料夾）
```

## Quick Start

1. **建立專案並替換名稱**
   ```bash
   git clone git@github.com:Dennis40816/py_proj_template.git my_project
   cd my_project
   git remote rename origin upstream              # 保留模板遠端以同步更新
   git remote add origin <your_repo_ssh_url>      # 指向自己的 repository
   git fetch upstream
   git checkout -b template upstream/main         # 專用模板分支（追蹤 upstream）
   git checkout main
   ```

   - 將 `src/proj_name/` 目錄與其中檔案改名為你的專案套件名稱（例如 `my_project`）。
   - 更新 `pyproject.toml` 的 `project.name` 等設定，並搜尋替換程式碼裡的 `proj_name`。
   - 視需要同步調整 `scripts/run_checks.py` 或其他腳本。
   - 後續同步模板：在 `template` 分支上執行 `git pull upstream main`，再切回 `main` 以 `git merge template` 帶入更新。

2. **啟動環境並執行 CLI 範例**
   - 建議使用 `uv` 建立虛擬環境並以 editable 模式安裝：
     ```bash
     uv venv
     uv pip install --editable .
     ```
   - 使用 `uv` 執行 CLI 範例：
     ```bash
     uv run python -m proj_name --name Alice
     ```
   - 或者直接啟用虛擬環境後以 Python 執行：
     ```bash
     source .venv/bin/activate  # Windows 使用 .venv\Scripts\activate
     python -m proj_name --name Alice
     ```

3. **安裝與同步依賴**
   - 將依賴寫入 `pyproject.toml` 後，執行：
     ```bash
     uv sync
     ```
     `uv` 會根據 `pyproject.toml` 自動解析、安裝並鎖定所有套件。
   - 若要新增依賴，可使用 `uv add <package>`，之後再次 `uv sync` 讓環境保持一致。
4. **清理或改寫範例測試**
   - 本模板提供的 `tests/unit/test_api.py` 與 `tests/integration/test_cli.py` 只是示範，若未保留範例程式碼請記得刪除或改寫，避免日後測試失敗。
   - 若新增新的測試邏輯，也請同步更新 `tests/conftest.py` 的 fixture。

5. **調整 AI-REQUIREMENT.md**
   - 專案開發前，檢視 `AI-REQUIREMENT.md` 是否符合需求；若需要調整請在模板更新後同步帶回。
6. **記錄模板版號**
   - `config/settings.toml` 中的 `template.version` 標記目前使用的模板標籤，當你從模板合併新變更時務必更新此欄位。

## Usage

### Run Checks

`scripts/run_checks.py` 用來統一執行格式化、靜態檢查與測試：

- 執行所有任務  
  ```bash
  uv run python scripts/run_checks.py
  # 或者
  python scripts/run_checks.py
  ```
- 僅執行特定任務（可選 `format`、`lint`、`test`）  
  ```bash
  python scripts/run_checks.py lint test
  ```
- 查看可用任務清單  
  ```bash
  python scripts/run_checks.py --list
  ```

腳本會自動偵測 `uv` 是否存在，若有則改用 `uv run` 以確保在一致的環境中執行；否則退回到 `python -m <tool>` 的方式。

### Manage Tags

發佈前可使用 `scripts/update_latest_tag.py` 驗證所有檢查項目並更新 `latest` 標籤：

- 顯示預期操作（不動標籤）
  ```bash
  python scripts/update_latest_tag.py --dry-run
  ```
- 實際更新 `latest`
  ```bash
  python scripts/update_latest_tag.py
  ```

若希望在推送前自動檢查，可建立 `.git/hooks/pre-push`：

```bash
cat <<'HOOK' > .git/hooks/pre-push
#!/usr/bin/env bash
python scripts/update_latest_tag.py --dry-run || exit 1
HOOK
chmod +x .git/hooks/pre-push
```

Git 沒有針對 `git tag` 的專屬 hook，使用 `pre-push` 能在送出標籤時進行驗證。

## NOTICE

- 以此模板為基底建立的新專案，請保留一個專用的 `template` 分支。當模板更新時，先在該分支上 `git pull` 最新變更，再透過合併 (`merge`) 將更新帶回主線，避免 rebase 造成不必要的衝突。

## Note

- 程式碼使用絕對匯入（例如 `from proj_name.api import ...`）。本地開發時請先執行 `uv pip install --editable .` 或設定 `PYTHONPATH=src` 後再啟動腳本，否則會出現 `ModuleNotFoundError`。若透過 `uv add git+...` 在其他專案中安裝此套件，`uv` 會自動處理匯入路徑，因此不需額外設定。
