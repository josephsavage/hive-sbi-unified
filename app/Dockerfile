FROM python:3.9.10

ARG DJANGO_ENV=prod

WORKDIR /app/

# Install PostgreSQL, MariaDB, and MS SQL prerequisites
RUN apt-get update && apt-get install -y \
    libpq-dev \
    default-libmysqlclient-dev \
    curl \
    gnupg2 \
    # Add Microsoft repository keys and sources for Debian 11
    && curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    # Update and install MS SQL drivers
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql17 \
    && apt-get install -y unixodbc-dev \
    && apt-get install -y dos2unix \
    # Clean up apt cache to keep image size small
    && rm -rf /var/lib/apt/lists/*

# Add requirements and install first to leverage Docker layer caching
ADD requirements /app/requirements
ADD requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && \
    pip install -r requirements/$DJANGO_ENV.txt

# Add the rest of the application files
ADD . /app/

RUN dos2unix /app/boot_scripts/*.sh
RUN chmod +x /app/boot_scripts/*.sh

# Create the unprivileged user
RUN adduser --disabled-password --gecos '' app

ENV HOME=/home/app
ENV DJANGO_SETTINGS_MODULE=hive_sbi_api.settings.$DJANGO_ENV
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8
ENV DJANGO_ENV=$DJANGO_ENV

CMD sh /app/boot_scripts/app.sh
