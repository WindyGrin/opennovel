# 变更日志

> 记录对 `.opencode/` 目录下 skills/scripts 的本地修改。原始版本来自 [webnovel-writer-opencode](https://github.com/lujih/webnovel-writer-opencode)。

---

## 2026-05-02 | 本地推理服务集成

**修改文件：**
- `scripts/local_embed_serve.py`（新建）—— FastAPI 本地推理服务，搭载 Qwen3-Embedding-4B (INT8) + jina-reranker-v3 (FP16)
- `start_local_server.bat` / `stop_local_server.bat`（新建）—— 服务启动/停止脚本
- `scripts/data_modules/api_client.py`—— `get_client()` 新增 `_ensure_local_server()` 自动后台启动
- `scripts/data_modules/image_generator.py`—— `generate()` 新增提示词输出模式（未配置 API key 时输出 txt 替代 API 调用）
- `skills/webnovel-image-gen/SKILL.md`—— 补充提示词输出模式说明

**影响：** 写作文操作无需手动启动本地 AI 服务；图片生成可在无 ModelScope Key 时输出提示词供手工生成。

---

## 2026-05-02 | 设定加载协议

**修改文件：**
- `skills/webnovel-write/references/setting-load-protocol.md`（新建）—— 三层加载协议（Pre-flight / In-writing / Post-write）

**影响：** 后续 `/webnovel-write` 应参考此协议注入角色快照、避免长篇 OOC。

---

## 2026-05-02 | 设定集目录重组

**修改内容：**
- `设定集/` 目录按 L0/L1/L2/L3 分层重组，新建 README.md 索引
- `设定集/角色库/` 拆分为 主要角色/反派角色/次元角色 三目录
- `设定集/核心设定/力量体系.md` 重写为渐进式三段悟道（下阶描红→中阶刻印→上阶悟道）

**影响：** 设定检索效率大幅提升。写作前只需按 L1→L2 逐层加载，不再一次性加载全量设定。

---

## 使用说明

- 如需从上游仓库更新 skills/scripts，运行 `python install.py`
- 更新后检查本文件中的本地修改是否被覆盖，如有冲突需手动合并
