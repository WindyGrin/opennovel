#!/usr/bin/env python
"""
本地 Embedding + Reranker 推理服务
兼容 OpenAI API 格式: /v1/embeddings 和 /v1/rerank
GPU: RTX 4080 16GB
Embedding: Qwen3-Embedding-4B  INT8 (~4GB VRAM)
Reranker:  jina-reranker-v3      FP16 (~1.2GB VRAM, 0.6B params)
总显存: ~5.2GB / 16GB
"""
import asyncio
import os
import logging
from contextlib import asynccontextmanager
from typing import List, Optional

import torch
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# ---------- 日志 ----------
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("local-embed")

# ---------- 模型配置 ----------
EMBED_MODEL_NAME = os.environ.get("LOCAL_EMBED_MODEL", "Qwen/Qwen3-Embedding-4B")
RERANK_MODEL_NAME = os.environ.get("LOCAL_RERANK_MODEL", "jinaai/jina-reranker-v3")
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
MAX_SEQ_LENGTH = int(os.environ.get("LOCAL_MAX_LENGTH", "8192"))
BATCH_SIZE = int(os.environ.get("LOCAL_BATCH_SIZE", "8"))
CACHE_DIR = os.environ.get("HF_HOME", None)

# ---------- 全局模型 ----------
embed_model = None
embed_tokenizer = None
rerank_model = None


def load_embedding_model():
    """Qwen3-Embedding-4B INT8, ~4GB VRAM"""
    global embed_model, embed_tokenizer
    from transformers import AutoModel, AutoTokenizer, BitsAndBytesConfig

    logger.info(f"[1/2] Loading embedding: {EMBED_MODEL_NAME} (INT8)")
    embed_tokenizer = AutoTokenizer.from_pretrained(EMBED_MODEL_NAME, trust_remote_code=True, cache_dir=CACHE_DIR)

    quant_config = BitsAndBytesConfig(load_in_8bit=True)
    embed_model = AutoModel.from_pretrained(
        EMBED_MODEL_NAME, trust_remote_code=True, cache_dir=CACHE_DIR,
        quantization_config=quant_config, device_map="auto",
    )
    embed_model.eval()
    vram = torch.cuda.memory_allocated() / 1e9
    logger.info(f"Embedding loaded. VRAM: {vram:.1f}GB")


def load_rerank_model():
    """jina-reranker-v3 FP16, ~1.2GB VRAM (0.6B params)"""
    global rerank_model
    from transformers import AutoModel

    logger.info(f"[2/2] Loading reranker: {RERANK_MODEL_NAME} (FP16)")
    rerank_model = AutoModel.from_pretrained(
        RERANK_MODEL_NAME, trust_remote_code=True, cache_dir=CACHE_DIR,
        torch_dtype=torch.float16, device_map="auto",
    )
    rerank_model.eval()
    vram = torch.cuda.memory_allocated() / 1e9
    logger.info(f"Reranker loaded. Total VRAM: {vram:.1f}GB")


# ---------- 推理 ----------

@torch.no_grad()
def compute_embeddings(texts: List[str]) -> List[List[float]]:
    all_embeddings = []
    for i in range(0, len(texts), BATCH_SIZE):
        batch = texts[i:i + BATCH_SIZE]
        inputs = embed_tokenizer(batch, padding=True, truncation=True,
            max_length=MAX_SEQ_LENGTH, return_tensors="pt").to(embed_model.device)
        outputs = embed_model(**inputs)
        mask = inputs["attention_mask"]
        hidden = outputs.last_hidden_state
        mask_expanded = mask.unsqueeze(-1).expand(hidden.size()).float()
        sum_embeddings = torch.sum(hidden * mask_expanded, dim=1)
        sum_mask = torch.clamp(mask_expanded.sum(dim=1), min=1e-9)
        vecs = torch.nn.functional.normalize(sum_embeddings / sum_mask, p=2, dim=1)
        all_embeddings.extend(vecs.cpu().tolist())
    return all_embeddings


@torch.no_grad()
def compute_rerank(query: str, documents: List[str], top_n: Optional[int] = None) -> List[dict]:
    """jina-reranker-v3 内置 rerank() 方法"""
    results = rerank_model.rerank(query, documents, top_n=top_n)
    # jina-reranker-v3 返回: [{"index": 0, "relevance_score": 0.93, "document": "..."}, ...]
    # 项目 api_client 期望: {"results": [{"index": 0, "relevance_score": 0.9}, ...]}
    # 字段完全兼容，只需去掉 document 字段
    return [{"index": int(r["index"]), "relevance_score": float(r["relevance_score"])} for r in results]


# ---------- FastAPI ----------

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("=" * 50)
    logger.info(f"Local Embedding + Reranker Server | Device: {DEVICE}")
    logger.info(f"  Embedding : {EMBED_MODEL_NAME}  (INT8)")
    logger.info(f"  Reranker  : {RERANK_MODEL_NAME}  (FP16, 0.6B)")
    logger.info(f"  GPU: {torch.cuda.get_device_name(0)} ({torch.cuda.get_device_properties(0).total_memory/1e9:.0f}GB)")
    logger.info("=" * 50)

    load_embedding_model()
    load_rerank_model()

    total = torch.cuda.memory_allocated() / 1e9
    free = (torch.cuda.get_device_properties(0).total_memory - torch.cuda.memory_allocated()) / 1e9
    logger.info(f"Ready! VRAM used: {total:.1f}GB, free: {free:.1f}GB")
    yield
    logger.info("Shutting down...")


app = FastAPI(title="Local Embedding+Reranker Server", lifespan=lifespan)


class EmbedRequest(BaseModel):
    input: List[str] = Field(..., min_length=1)
    model: str = "qwen3-embedding-4b"
    encoding_format: Optional[str] = "float"


class EmbedResponse(BaseModel):
    data: List[dict]


class RerankRequest(BaseModel):
    query: str
    documents: List[str]
    model: str = "jina-reranker-v3"
    top_n: Optional[int] = None


class RerankResponse(BaseModel):
    results: List[dict]


@app.get("/health")
async def health():
    vram_used = torch.cuda.memory_allocated() / 1e9 if DEVICE == "cuda" else 0
    vram_total = torch.cuda.get_device_properties(0).total_memory / 1e9 if DEVICE == "cuda" else 0
    return {"status": "ok", "device": DEVICE, "gpu": torch.cuda.get_device_name(0) if DEVICE == "cuda" else "N/A",
            "vram_used_gb": round(vram_used, 1), "vram_total_gb": round(vram_total, 0)}


@app.post("/v1/embeddings", response_model=EmbedResponse)
async def embeddings(req: EmbedRequest):
    vecs = await asyncio.to_thread(compute_embeddings, req.input)
    return EmbedResponse(data=[{"embedding": v, "index": i} for i, v in enumerate(vecs)])


@app.post("/v1/rerank", response_model=RerankResponse)
async def rerank(req: RerankRequest):
    results = await asyncio.to_thread(compute_rerank, req.query, req.documents, req.top_n)
    return RerankResponse(results=results)


if __name__ == "__main__":
    port = int(os.environ.get("LOCAL_PORT", "9997"))
    host = os.environ.get("LOCAL_HOST", "0.0.0.0")
    uvicorn.run(app, host=host, port=port, log_level="info")
