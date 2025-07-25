FROM node:20-alpine
WORKDIR /app
COPY package.json ./
RUN npm install
RUN ls -l /app/node_modules/.bin
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
