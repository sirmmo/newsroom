FROM andrejreznik/python-gdal:py3.10.0-gdal3.2.3 

WORKDIR /srv

# Create and activate virtual environment
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

run python manage.py migrate

CMD ["granian", "--interface", "asgi", "newsroom.asgi:application", "--host", "0.0.0.0", "--port", "80"]
