# 使用 Node.js 镜像作为基础镜像，前提是你的项目需要 Node.js 来构建
FROM node:16.15.0 AS build  
# 推荐使用较新版本的 Node.js

# 设置工作目录
WORKDIR /app

# 复制 package.json 和 package-lock.json
COPY package*.json ./

# 安装依赖
RUN npm install

# 复制其余的项目文件
COPY . .

# 执行 npm run build:prod 命令进行生产环境构建
RUN npm run build:prod

# 使用 Nginx 镜像作为基础镜像
FROM nginx

# 设置环境变量，确保采用 key=value 格式
ENV DATA_DIR=/data/dist
ENV LOG_DIR=/data/log/nginx

# 创建日志目录并设置权限
RUN mkdir -p /data/log/nginx && chown nginx:nginx -R /data/log/nginx

# 将构建的前端代码复制到 Nginx 的根目录
COPY --from=build /app/dist /data/dist

# 复制 Nginx 配置文件
ADD default.conf /etc/nginx/conf.d/default.conf  
# 确保 default.conf 文件存在

# 暴露 Nginx 的 80 端口
EXPOSE 80

# 启动 Nginx
ENTRYPOINT ["nginx", "-g", "daemon off;"]
