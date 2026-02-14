# ── Stage 1: 建構前端 ──
FROM node:22-slim AS builder

WORKDIR /app

# 先複製 package 檔案以利用 Docker 快取
COPY package.json package-lock.json ./
RUN npm ci

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
