FROM node:23.9.0-bookworm-slim AS base

ARG APP_HOME=/app

# Set environment variables
ENV NODE_ENV=development
ENV BUILD_ENV=local

# set the volumes
VOLUME /app

# Set the working directory
WORKDIR ${APP_HOME}/

# Install required system dependencies
RUN apt-get update && apt-get install --no-install-recommends -y \
    # devcontainer dependencies and utils
    sudo git bash-completion nano ssh \
    # Translations dependencies
    gettext \
    # cleaning up unused files
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js dependencies
COPY ./frontend/package.json ./frontend/package-lock.json ./

# Install Node.js dependencies globally
RUN npm install --no-audit --progress=false --prefer-offline \
    && npm cache clean --force

# run infinite loop to keep the container alive
CMD npm run dev
