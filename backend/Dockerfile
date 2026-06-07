FROM node:18-alpine
# Strapi için gerekli kütüphanelerin kurulması
RUN apk update && apk add --no-cache build-base gcc autoconf automake zlib-dev libpng-dev vips-dev git bash
ENV NODE_ENV=production

WORKDIR /opt/
COPY package.json package-lock.json ./
RUN npm install --production

WORKDIR /opt/app
COPY . .
RUN npm run build

EXPOSE 1337
CMD ["npm", "run", "start"]