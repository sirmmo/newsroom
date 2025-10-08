FROM andrejreznik/python-gdal:py3.10.0-gdal3.2.3 

WORKDIR /srv

# Install system dependencies including Python 3.12
RUN apt update  && \
    apt-get install -y --fix-missing \
    #python3 python3-pip python3-setuptools python3-wheel python3-venv \
    #build-essential python3-dev \
    #libgdal-dev gdal-bin \
    libpq-dev \
    pkg-config && \
    rm -rf /var/lib/apt/lists/*

# Set GDAL environment variables for pip installation
#ENV GDAL_CONFIG=/usr/bin/gdal-config
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

# Create and activate virtual environment
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Set Docker environment variable
ENV IN_DOCKER="true"

# First install setuptools before other packages
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Install GDAL Python bindings separately to ensure version compatibility
#RUN pip install --no-cache-dir GDAL==$(gdal-config --version)

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .


# Custom entrypoint to handle migrations properly
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

CMD ["granian", "--interface", "asgi", "newsroom.asgi:application", "--host", "0.0.0.0", "--port", "80"]
