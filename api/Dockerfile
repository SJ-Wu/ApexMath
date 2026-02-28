# ── Stage 1: 安裝依賴 ──
FROM python:3.13-slim AS builder

WORKDIR /build
COPY pyproject.toml .
# 建立暫時的 app 套件目錄，讓 pip install -e 不會失敗
RUN mkdir -p app && touch app/__init__.py
RUN pip install --no-cache-dir -e "."

# ── Stage 2: 執行環境 ──
FROM python:3.13-slim

WORKDIR /app

# 複製已安裝的套件
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin/uvicorn /usr/local/bin/uvicorn
COPY --from=builder /usr/local/bin/alembic /usr/local/bin/alembic

# 複製應用程式原始碼
COPY . .

EXPOSE 8000

# 健康檢查
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/')" || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
