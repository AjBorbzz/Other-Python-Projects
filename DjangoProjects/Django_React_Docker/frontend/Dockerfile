FROM node:16-alpine

WORKDIR /app/fronted/

COPY package*.json /app/fronted/
RUN npm install

COPY . /app/fronted/

CMD ["npm", "start"]