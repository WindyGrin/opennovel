# Webnovel Writer 本地 Embedding + Reranker 安装手册

> 📢 **本项目为 AI 小说共创项目**（《满级重修，每一项刚好及格就行》）。如果你只想参与共创讨论，**不需要**搭建本地环境——直接阅读 [CONTRIBUTING.md](CONTRIBUTING.md) 即可。如果你想基于此框架创作自己的小说，请继续阅读本手册。
>
> 适用 GPU: NVIDIA RTX 4080 16GB | 系统: Windows 10/11 | 日期: 2026-05-02

## 概览

为 Webnovel Writer 项目搭建本地 Embedding 和 Reranker 推理服务，替代云端 API，实现零成本、低延迟的向量化和检索重排。

| 模型 | 参数量 | 量化 | 显存占用 | 用途 |
|---|---|---|---|---|
| `Qwen/Qwen3-Embedding-4B` | 4B | INT8 (bitsandbytes) | ~4.4 GB | 文本向量化 |
| `jinaai/jina-reranker-v3` | 0.6B | FP16 | ~1.2 GB | 检索结果重排 |
| **合计** | | | **~5.6 GB** | |

推理服务通过 FastAPI + uvicorn 暴露 OpenAI 兼容的 `/v1/embeddings` 和 `/v1/rerank` 端点，与项目 `api_client.py` 完全兼容。

---

## 硬件要求

- **GPU**: NVIDIA 显卡，≥8 GB 显存 (RTX 3060/4060 以上)
- **系统内存**: ≥16 GB (建议 32 GB)
- **磁盘**: ~30 GB 空闲 (conda 环境 + 模型权重)
- **CUDA**: 12.x (本手册使用 CUDA 12.4 + PyTorch 2.6.0)

---

## 目录结构 (安装后)

```
H:\Code\mynovel\                      # 项目根目录
├── .env                              # 配置 (EMBED/RERANK 指向 localhost)
├── start_local_server.bat            # 一键启动服务
├── stop_local_server.bat             # 停止服务 (释放 GPU)
├── .hf_cache\                        # HuggingFace 模型缓存 (约 9 GB)
│   └── huggingface\hub\               #   实际模型文件
├── .opencode\
│   └── scripts\
│       └── local_embed_serve.py      # 推理服务主程序
└── requirements.txt

H:\anaconda3\envs\webnovel-embed\     # Conda 环境 (约 5.6 GB)
```

> **所有文件均在 H: 盘，C: 盘无任何大型文件写入。**

---

## 安装步骤

### Step 1: 检测环境

```powershell
python --version    # 需 ≥ 3.9
pip --version
nvidia-smi          # 确认 GPU 型号和驱动
conda --version     # 需已安装 Anaconda/Miniconda
```

### Step 2: 创建 Conda 环境

```powershell
# 创建独立环境 (Python 3.10)
conda create -n webnovel-embed python=3.10 -y

# 激活环境
conda activate webnovel-embed
```

### Step 3: 安装 PyTorch (CUDA 版)

由于 PyTorch CUDA wheel 约 2.5 GB，官方源下载慢，建议先下载到本地再安装：

```powershell
# 方案 A: 断点续传下载 (推荐)
Invoke-WebRequest -Uri "https://download.pytorch.org/whl/cu124/torch-2.6.0%2Bcu124-cp310-cp310-win_amd64.whl" `
    -OutFile "torch-2.6.0+cu124-cp310-cp310-win_amd64.whl"

# 安装本地 wheel
pip install "torch-2.6.0+cu124-cp310-cp310-win_amd64.whl"

# 删除 wheel 节省空间
del "torch-2.6.0+cu124-cp310-cp310-win_amd64.whl"
```

```powershell
# 方案 B: pip mirror 安装 (可能安装 CPU 版，需验证)
pip install torch torchvision torchaudio
```

验证 CUDA 可用：

```powershell
python -c "import torch; print(torch.cuda.is_available(), torch.cuda.get_device_name(0))"
# 输出: True NVIDIA GeForce RTX 4080
```

### Step 4: 安装依赖

```powershell
# bitsandbytes (INT8 量化)
pip install bitsandbytes

# transformers, fastapi, uvicorn 等
pip install transformers fastapi uvicorn accelerate sentencepiece
```

### Step 5: 部署推理服务

确认以下文件已就位：
- `H:\Code\mynovel\.opencode\scripts\local_embed_serve.py` — 推理服务主程序
- `H:\Code\mynovel\start_local_server.bat` — 启动脚本
- `H:\Code\mynovel\stop_local_server.bat` — 停止脚本
- `H:\Code\mynovel\.env` — 配置文件

### Step 6: 配置 .env

```env
# Embedding (本地推理)
EMBED_BASE_URL=http://localhost:9997
EMBED_MODEL=qwen3-embedding-4b
EMBED_API_KEY=not-needed

# Rerank (本地推理)
RERANK_BASE_URL=http://localhost:9997
RERANK_MODEL=jina-reranker-v3
RERANK_API_KEY=not-needed
```

### Step 7: 首次启动 (自动下载模型)

```cmd
# 双击或在命令行运行
start_local_server.bat
```

首次启动会从 HF Mirror 下载模型权重到 `H:\Code\mynovel\.hf_cache\`：
- `Qwen3-Embedding-4B`: ~7.7 GB
- `jina-reranker-v3`: ~1.2 GB

预计耗时 5-15 分钟 (取决于网络)。启动成功后显示：

```
Ready! VRAM used: 5.6GB, free: 11.6GB
INFO: Uvicorn running on http://0.0.0.0:9997
```

之后启动秒级就绪 (模型已缓存)。

---

## 日常使用

### 启动服务

```cmd
start_local_server.bat
```

### 停止服务

```cmd
stop_local_server.bat
```

或手动：

```powershell
Get-Process python* | Where-Object {$_.CommandLine -match "local_embed"} | Stop-Process
```

### 验证服务

```powershell
# 健康检查
curl http://localhost:9997/health
# → {"status":"ok","device":"cuda","vram_used_gb":5.6}

# 测试 Embedding
curl -X POST http://localhost:9997/v1/embeddings `
  -H "Content-Type: application/json" `
  -d '{"input":["hello world"],"model":"qwen3-embedding-4b"}'

# 测试 Rerank
curl -X POST http://localhost:9997/v1/rerank `
  -H "Content-Type: application/json" `
  -d '{"query":"What is AI?","documents":["AI is...","Banana bread"],"model":"jina-reranker-v3","top_n":1}'
```

---

## 磁盘空间管理

### 安装后占用

| 位置 | 内容 | 大小 |
|---|---|---|
| `H:\Code\mynovel\.hf_cache\` | 模型权重 (Embedding + Reranker) | **~9 GB** |
| `H:\anaconda3\envs\webnovel-embed\` | Python 环境 + 依赖 | **~5.6 GB** |
| **合计** | | **~15 GB** |

> C: 盘不写入任何大型文件。`HF_HOME` 环境变量已永久指向 H: 盘。

### 清理未使用的模型缓存

```powershell
# 查看当前缓存的模型
Get-ChildItem H:\Code\mynovel\.hf_cache\huggingface\hub -Directory

# 删除不需要的模型
Remove-Item H:\Code\mynovel\.hf_cache\huggingface\hub\models--xxx -Recurse -Force
```

### 彻底卸载

```powershell
# 1. 删除 Conda 环境
conda remove -n webnovel-embed --all -y

# 2. 删除模型缓存
Remove-Item H:\Code\mynovel\.hf_cache -Recurse -Force

# 3. 删除服务脚本 (可选)
del H:\Code\mynovel\start_local_server.bat
del H:\Code\mynovel\stop_local_server.bat
del H:\Code\mynovel\.opencode\scripts\local_embed_serve.py
```

---

## 架构说明

### 服务端口

| 端点 | 方法 | 说明 |
|---|---|---|
| `/health` | GET | 健康检查 (VRAM, GPU 信息) |
| `/v1/embeddings` | POST | 文本向量化 (2560 维) |
| `/v1/rerank` | POST | 检索结果重排 |

### 请求格式

**Embedding 请求:**
```json
{
  "input": ["text1", "text2"],
  "model": "qwen3-embedding-4b",
  "encoding_format": "float"
}
```

**Embedding 响应:**
```json
{
  "data": [
    {"embedding": [0.01, -0.02, ...], "index": 0},
    {"embedding": [0.03, 0.04, ...], "index": 1}
  ]
}
```

**Rerank 请求:**
```json
{
  "query": "search query",
  "documents": ["doc1", "doc2"],
  "model": "jina-reranker-v3",
  "top_n": 10
}
```

**Rerank 响应:**
```json
{
  "results": [
    {"index": 0, "relevance_score": 0.93},
    {"index": 1, "relevance_score": 0.15}
  ]
}
```

### 与项目集成

项目的 `api_client.py` (`H:\Code\mynovel\.opencode\scripts\data_modules\api_client.py`) 通过 `.env` 中的配置自动连接本地服务，无需修改代码：

- `EMBED_BASE_URL` → `http://localhost:9997` → `/v1/embeddings`
- `RERANK_BASE_URL` → `http://localhost:9997` → `/v1/rerank`

---

## 常见问题

**Q: 启动后显示 "ACCESS_VIOLATION" 崩溃？**
A: 显卡显存不足。确认未同时运行其他 GPU 程序，或降低模型精度。

**Q: 启动后显示 "commitment limit" 错误？**
A: Windows 虚拟内存不足。增大系统页面文件 或 关闭其他占用内存的程序。

**Q: 模型下载速度慢？**
A: `start_local_server.bat` 中已配置 `HF_ENDPOINT=https://hf-mirror.com` (镜像加速)。如仍慢，可尝试设置代理或更换镜像。

**Q: 如何切换到其他模型？**
A: 编辑 `.env` 中的 `EMBED_MODEL` / `RERANK_MODEL`，并对应修改 `local_embed_serve.py` 中的加载逻辑。

**Q: 可以只用 Embedding 或只用 Reranker 吗？**
A: 可以。注释掉 `local_embed_serve.py` 中 `lifespan()` 里不需要的 `load_xxx_model()` 调用即可。

---

## 引用

- [Qwen3-Embedding](https://hf-mirror.com/Qwen/Qwen3-Embedding-4B)
- [jina-reranker-v3](https://hf-mirror.com/jinaai/jina-reranker-v3)
- [Webnovel Writer](https://github.com/lujih/webnovel-writer-opencode)
