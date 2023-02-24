# Stage 1: build
FROM node:18.2.0 as build

WORKDIR /app
COPY makefile $WORKDIR

# Install requirements
COPY package.json $WORKDIR
COPY package-lock.json $WORKDIR
RUN make install

# Build app
COPY . $WORKDIR
RUN make build-ssr

EXPOSE 3000
CMD ["./dist/start.sh"]
