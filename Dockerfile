FROM node:10.0.0

USER root

RUN mkdir -p /usr/app

RUN apt-get update && apt-get install unzip

# Download repo and make folders
RUN curl -L https://github.com/huytd/agar.io-clone/archive/master.zip -o agar.io-clone-master.zip
RUN unzip agar.io-clone-master.zip
RUN mv -v agar.io-clone-master/* /usr/app

WORKDIR /usr/app

# RUN npm install -g npm@7.8.0
RUN npm install
# RUN npm update -g gulp

EXPOSE 3000

CMD ["npm", "start"]
