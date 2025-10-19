# AI Coding Guidelines

這份文件提供給 AI 開發助手閱讀，請嚴格遵守以下規範，確保所有專案維持一致品質與風格。

## 自訂開發規則

- **評論與文件**：所有 code comment 與 docstring 一律使用英文撰寫，且每個公開的 function、class、module 都必須描述用途並附上簡單範例。
- **匯入方式**：永遠使用絕對匯入（`from proj_name.module import symbol`），不得使用相對匯入。
- **語法風格**：善用 Python 的語法糖與現代特性（comprehension、context manager 等）在不影響可讀性下簡化程式。
- **整潔哲學**：維持 Clean Code 與類 Unix 的簡潔風格，避免不必要的複雜度與冗長流程。
- **資源管理**：任何需要釋放資源的操作（檔案、鎖、連線等）必須使用 `with` context manager 或等效機制確保自動清理。

## 核心要求（摘錄自專案規格）

- **工具與環境**
  - 使用 `uv` 管理專案生命週期（建立虛擬環境、安裝依賴、打包）。
  - Python 版本固定為 3.12 以上，新的語言特性與 typing 能力皆可使用。
  - 專案對外版本採用 Semantic Versioning，版本資訊需集中管理（如 `pyproject.toml` 與 `__version__`）。
- **專案結構**
  - 採 `src/` 佈局，核心邏輯放在專案同名套件內。
  - `tests/` 目錄必備，依需要劃分 unit、integration 等子資料夾。
  - `scripts/`、`docs/`、`data/` 等常用資料夾需遵循模板提供的層級。
  - 公開 API 應由專屬模組（例如 `proj_name.api`）或套件 `__init__.py` 封裝，區隔內部實作與外部接口。
- **程式風格**
  - 遵循 PEP 8 命名慣例；函式與模組使用 snake_case，類別使用 CamelCase。
  - 以函式為優先，除非確有必要再建立類別。
  - 所有函式必須具備完整的 type hints（參數與回傳值）。
  - 採用 Black 風格或等效設定的自動格式化。
- **撰寫品質**
  - 函式應保持單一責任與可組合性，符合 Unix 「做好一件事」的哲學。
  - 程式碼應盡量簡潔，不寫炫技或晦澀寫法；在保持可讀性的前提下可運用語法糖降低樣板碼。
  - Docstring 需描述用途、參數、回傳值與例外情境，如行為不直覺需提供範例。
- **資源與可靠度**
  - 檔案與路徑一律使用 `pathlib.Path`，提供必要的輔助函式以維持一致作法。
  - 檔案寫入需考慮原子性，避免產生半成品。
  - 任何 I/O 或長時間操作要有 timeout，必要時使用 `asyncio`。
  - 長時間任務需支援 SIGINT（Ctrl+C）安全退出，優先使用集中化的 signal context。
  - 重試機制與實際操作邏輯需拆分，確保每次重試皆重新獲取資源並妥善釋放。
  - 暫時變更工作目錄或環境變數應透過 context manager，結束時還原狀態。
- **測試與建置**
  - 隨著功能成熟需補齊單元與整合測試；模板已預留骨架，請填入實際場景。
  - 專案需可透過 `pyproject.toml` 直接安裝與建置（支援 `uv build` / `uv publish`）。

## Release Checklist

在發佈新版本前，務必完成下列步驟，否則不得更新標籤：

1. 確保工作目錄乾淨（無未提交變更）。
2. 更新版本資訊：`pyproject.toml` 與 `config/settings.toml` 的版本必須一致。
3. 撰寫 `CHANGELOG.md` 條目：所有新變更須新增至下一版本（例如新增 `[1.x.y] - Unreleased`），不得改動已寫入日期的歷史版本；必要補充請以新版本條目紀錄並視需要更新 `README.md`。
4. 執行 `uv run python scripts/run_checks.py`，所有檢查與測試需通過。
5. 建立清楚的提交（例如 `chore: release X.Y.Z`）。
6. 建立 `vX.Y.Z` 標籤後，執行 `python scripts/release_check.py --tag vX.Y.Z --require-highest` 驗證：模板專案 (`py-proj-template`) 會同時比對 `config/settings.toml`，其他專案則檢查 `pyproject.toml` 與 `src/<pkg>/__init__.py` 的版本。
7. 推送程式碼與 `v*` 標籤；GitHub Actions 會透過 `.github/workflows/update-latest.yml` 自動加入 `--update-latest` 檢查，確認最高標籤後更新 `latest`。若要在本地確定最高標籤，可額外加上 `--require-highest`。

遵照以上規定能協助所有新專案維持一致結構、風格與可靠度。若規格更新，請同步調整本文件。
