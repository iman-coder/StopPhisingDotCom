### frontend/Dockerfile
# Multi-stage: build with Node, serve static via nginx

FROM node:20-bullseye-slim AS build
WORKDIR /app

# update OS packages to reduce known vulnerabilities and ensure required certs
RUN apt-get update && apt-get upgrade -y && apt-get install -y --no-install-recommends ca-certificates && rm -rf /var/lib/apt/lists/*

# copy package manifest first and install dependencies
COPY package*.json ./
RUN npm ci --silent

# copy source and build
COPY . .
RUN npm run build

FROM nginx:stable-alpine

# Copy built static files
COPY --from=build /app/dist /usr/share/nginx/html

# Custom nginx config to handle SPA fallback and proxy API
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
