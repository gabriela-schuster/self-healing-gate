FROM python:3.12

# Install uv
ADD https://astral.sh/uv/install.sh /uv-installer.sh
RUN sh /uv-installer.sh && rm /uv-installer.sh
ENV PATH="/root/.local/bin/:$PATH"

# Copy and install dependencies
WORKDIR /app
ENV UV_LINK_MODE=copy
COPY pyproject.toml /app/
RUN uv sync

# Now copy the rest of the code
COPY . /app

RUN apt-get update && apt-get install -y poppler-utils

# Run the app
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]

