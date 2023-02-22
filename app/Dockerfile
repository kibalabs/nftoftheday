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

# Stage 2: Serve with nginx
FROM ghcr.io/kibalabs/app-serve:latest
COPY --from=build /app/dist /usr/share/nginx/html
