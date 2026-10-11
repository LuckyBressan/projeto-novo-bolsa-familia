FROM node:24-alpine AS build

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .

# Só o empacotamento: a checagem de tipos precisa do mock do back-end, que fica fora deste contexto.
RUN npm run build-only


FROM nginx:1.30-alpine AS runtime

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80
