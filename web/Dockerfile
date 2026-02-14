# ── Stage 1: 建構前端 ──
FROM node:22-slim AS builder

WORKDIR /app

# 先複製 package 檔案以利用 Docker 快取
COPY package.json package-lock.json ./
RUN npm ci

# Vite 環境變數（build time 替換 import.meta.env.*）
# Render 部署時透過 render.yaml 的 envVars 或 docker build --build-arg 傳入
ARG VITE_API_BASE_URL=/api
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}

# 複製原始碼並建構
COPY . .
RUN npm run build

# ── Stage 2: Nginx 靜態服務 ──
FROM nginx:alpine

# 複製建構產物
COPY --from=builder /app/dist /usr/share/nginx/html

# 複製自訂 Nginx 設定
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD wget -q --spider http://localhost/ || exit 1

