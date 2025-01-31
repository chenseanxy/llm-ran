# syntax=docker/dockerfile:1.7-labs

ARG OLLAMA_VERSION=0.5.7
FROM ollama/ollama:${OLLAMA_VERSION}
ENV DEBIAN_FRONTEND=noninteractive
ARG PYTHON_VERSION=3.12

# Install Python and other dependencies
RUN echo 'tzdata tzdata/Areas select Europe' | debconf-set-selections \
    && echo 'tzdata tzdata/Zones/Europe select Helsinki' | debconf-set-selections \
    && apt-get update -y \
    && apt-get install -y ccache software-properties-common git curl python3-pip \
    && apt-get install -y ffmpeg libsm6 libxext6 libgl1 \
    && add-apt-repository ppa:deadsnakes/ppa \
    && apt-get update -y \
    && apt-get install -y python${PYTHON_VERSION} python${PYTHON_VERSION}-dev python${PYTHON_VERSION}-venv libibverbs-dev \
    && update-alternatives --install /usr/bin/python3 python3 /usr/bin/python${PYTHON_VERSION} 1 \
    && update-alternatives --set python3 /usr/bin/python${PYTHON_VERSION} \
    && ln -sf /usr/bin/python${PYTHON_VERSION}-config /usr/bin/python3-config \
    && curl -sS https://bootstrap.pypa.io/get-pip.py | python${PYTHON_VERSION} \
    && python3 --version && python3 -m pip --version

# Setup s6
ARG S6_OVERLAY_VERSION=3.2.0.2
ADD https://github.com/just-containers/s6-overlay/releases/download/v${S6_OVERLAY_VERSION}/s6-overlay-noarch.tar.xz /tmp
RUN tar -C / -Jxpf /tmp/s6-overlay-noarch.tar.xz
ADD https://github.com/just-containers/s6-overlay/releases/download/v${S6_OVERLAY_VERSION}/s6-overlay-x86_64.tar.xz /tmp
RUN tar -C / -Jxpf /tmp/s6-overlay-x86_64.tar.xz
COPY deployment/s6-rc.d/ /etc/s6-overlay/s6-rc.d

# Setup Cloudflared for API networking
ADD --chmod=755 https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 /usr/local/bin/cloudflared

# Setup Poetry for Python dependencies
ARG POETRY_VERSION=2.0

# See https://python-poetry.org/docs/#ci-recommendations
RUN --mount=type=cache,target=/root/.cache/pip pip install "poetry==${POETRY_VERSION}"

WORKDIR /app

# For build caching
COPY pyproject.toml poetry.lock /app/

RUN poetry install --no-root

COPY . /app/

# To make sure llm-ran is installed as a package
RUN poetry install

CMD ["poetry", "run", "python", "-m", "llm_ran"]

# S6 entrypoint
ENTRYPOINT ["/init"]

ENV HOME=/root
