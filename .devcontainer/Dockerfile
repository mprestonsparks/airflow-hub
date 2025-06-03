# Airflow Hub Development Container
ARG AIRFLOW_VERSION="3.0.0"
FROM apache/airflow:${AIRFLOW_VERSION}

# Switch to root for system installations
USER root

# Avoid warnings by switching to noninteractive
ENV DEBIAN_FRONTEND=noninteractive

# Set up environment variables
ENV AIRFLOW_HOME=/workspaces/airflow-hub
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="${PATH}:/home/airflow/.local/bin"

# Install system dependencies
RUN apt-get update \
    && apt-get -y install --no-install-recommends \
        # Essential development tools
        build-essential \
        curl \
        wget \
        git \
        make \
        jq \
        tree \
        htop \
        vim \
        nano \
        # Network tools
        net-tools \
        iputils-ping \
        telnet \
        # Additional utilities
        ssh \
        sudo \
        ca-certificates \
        gnupg \
        lsb-release \
        # Database tools
        postgresql-client \
        # Vault CLI dependencies
        unzip \
    && apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*

# Install Docker CLI
RUN curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null \
    && apt-get update \
    && apt-get install -y docker-ce-cli docker-compose-plugin \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*

# Install Vault CLI
RUN curl -fsSL https://releases.hashicorp.com/vault/1.15.4/vault_1.15.4_linux_amd64.zip -o vault.zip \
    && unzip vault.zip \
    && mv vault /usr/local/bin/ \
    && rm vault.zip

# Create directories
RUN mkdir -p /workspaces/airflow-hub \
    && mkdir -p /data \
    && mkdir -p /logs

# Set up user permissions
RUN usermod -aG docker airflow \
    && echo "airflow ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers.d/airflow \
    && chmod 0440 /etc/sudoers.d/airflow

# Switch back to airflow user
USER airflow

# Install additional Python packages
RUN pip install --user --no-cache-dir \
    # Development tools
    black \
    ruff \
    mypy \
    pytest \
    pytest-cov \
    pytest-mock \
    coverage \
    # Airflow providers and extras
    apache-airflow[postgres,vault,docker] \
    # Database connectors
    psycopg2-binary \
    sqlalchemy \
    # Vault integration
    hvac \
    # Utilities
    python-dotenv \
    requests \
    httpx

# Create useful aliases
RUN echo 'alias ll="ls -alF"' >> ~/.bashrc \
    && echo 'alias la="ls -A"' >> ~/.bashrc \
    && echo 'alias l="ls -CF"' >> ~/.bashrc \
    && echo 'alias ..="cd .."' >> ~/.bashrc \
    && echo 'alias dc="docker-compose"' >> ~/.bashrc \
    && echo 'alias airflow-start="airflow webserver -D && airflow scheduler -D"' >> ~/.bashrc \
    && echo 'alias airflow-stop="pkill -f airflow"' >> ~/.bashrc \
    && echo 'export PATH=$HOME/.local/bin:$PATH' >> ~/.bashrc \
    && echo 'export AIRFLOW_HOME=/workspaces/airflow-hub' >> ~/.bashrc \
    && echo 'export VAULT_ADDR=http://host.docker.internal:8200' >> ~/.bashrc

# Set up git configuration
RUN git config --global init.defaultBranch main \
    && git config --global pull.rebase false \
    && git config --global core.autocrlf input \
    && git config --global core.eol lf

# Create workspace directory and set permissions
RUN sudo mkdir -p /workspaces/airflow-hub \
    && sudo chown -R airflow:airflow /workspaces/airflow-hub

# Switch back to dialog for any ad-hoc use of apt-get
ENV DEBIAN_FRONTEND=dialog

# Set the working directory
WORKDIR /workspaces/airflow-hub

# Default command
CMD ["sleep", "infinity"]