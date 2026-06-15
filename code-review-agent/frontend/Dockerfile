FROM node:20-slim

WORKDIR /app

# copy package files first (layer caching)
COPY package.json package-lock.json ./
RUN npm install

# copy source
COPY . .

# build for production
RUN npm run build

# serve with nginx
FROM nginx:alpine
COPY --from=0 /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]