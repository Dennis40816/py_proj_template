# Changelog

## [1.0.3] - 2025-10-19

- 新增 GitHub Actions 工作流程 `update-latest-tag.yml`，在推送版本標籤後自動驗證與更新 `latest`。
- README 說明自動化標籤管理流程，仍保留腳本供本地檢查使用。
- 工作流程會忽略 `latest` 標籤的推送以避免無限循環。

## [1.0.2] - 2025-10-19

- 擴充 `scripts/update_latest_tag.py`，讓所有專案都能使用；模板專案仍會額外檢查 `config/settings.toml`。
- README 新增管理標籤與 Git hook 說明，方便在推送前自動驗證。

## [1.0.1] - 2025-10-19

- README Quick Start 說明如何同步保留 `upstream`（模板）與 `origin`（專案），建立 `template` 分支並合併更新。
- 新增 `config/settings.toml` 的 `template.version` 欄位，用於紀錄目前採用的模板標籤。
- 新增 `TODO.md`，提醒建立自動更新 `latest` 標籤的流程。
- 新增 `scripts/update_latest_tag.py`，用於驗證發佈前檢查並安全更新 `latest` 標籤。

## [1.0.0] - 2025-10-19

- 建立完整的 `src/` 骨架，涵蓋 `api`、`application`、`core/lib_example`、`cli`、`services`、`domain`、`infra`、`utils` 等常用層級。
- 提供最小示範流程：`lib_example` → `api` → `application` → CLI，並藉由 `python -m proj_name` 展現整體匯入關係。
- 新增 `scripts/run_checks.py` 以整合格式化、靜態檢查與測試指令。
- 擴充 `tests/`，包含單元與整合測試示例以及常用 fixture（`conftest.py`）。
- 撰寫 `README.md` 的 Intro、Quick Start、Usage、Notice、Note 等章節，指引用法、同步流程與測試清理事項。
- 新增 `ai_requirements.md` 給 AI 開發助手，彙整自訂規則與核心開發準則。
