# Changelog

## [1.0.0] - 2025-10-19

- 建立完整的 `src/` 骨架，涵蓋 `api`、`application`、`core/lib_example`、`cli`、`services`、`domain`、`infra`、`utils` 等常用層級。
- 提供最小示範流程：`lib_example` → `api` → `application` → CLI，並藉由 `python -m proj_name` 展現整體匯入關係。
- 新增 `scripts/run_checks.py` 以整合格式化、靜態檢查與測試指令。
- 擴充 `tests/`，包含單元與整合測試示例以及常用 fixture（`conftest.py`）。
- 撰寫 `README.md` 的 Intro、Quick Start、Usage、Notice、Note 等章節，指引用法、同步流程與測試清理事項。
- 新增 `ai_requirements.md` 給 AI 開發助手，彙整自訂規則與核心開發準則。
