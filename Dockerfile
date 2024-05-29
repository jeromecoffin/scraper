FROM python:3.8-slim-buster

# Ensure any piped commands exit on error
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

ENV PATH /usr/local/bin:$PATH
ENV LANG C.UTF-8

WORKDIR /app
RUN mkdir -p /app/data/logs/

# Copy the current directory contents into the container at /app
COPY code/getprice.py /app/code/
COPY requirements.txt /root/
COPY louis_vuitton.txt /app/code/louis_vuitton.txt

# Install the latest versions of Google Chrome and Chromedriver
# Patches Chrome launch script to disable /dev/shm and sandbox for use in docker
RUN export DEBIAN_FRONTEND=noninteractive && apt-get update \
  && apt-get install --no-install-recommends --no-install-suggests --assume-yes \
    curl \
    unzip \
    gnupg \
    unzip \
    wget \
    locales \
    cron \
    vim \
    dos2unix \
  ####Pour choper chrome et chromedriver : https://googlechromelabs.github.io/chrome-for-testing/
  && CHROME_DOWNLOAD_URL='https://dl.google.com/linux' \
  && curl -sL "${CHROME_DOWNLOAD_URL}/linux_signing_key.pub" | apt-key add - \
  && curl -sL "${CHROME_DOWNLOAD_URL}/direct/google-chrome-stable_current_amd64.deb" > /tmp/chrome.deb \
  # TODO find packages that cause fail before this and install first
  && (dpkg -i /tmp/chrome.deb || apt-get install --no-install-recommends --no-install-suggests --assume-yes --fix-broken) \
  && CHROMIUM_OPTIONS_FILE=/opt/google/chrome/google-chrome \
  && echo "$(cat ${CHROMIUM_OPTIONS_FILE}) ${CHROMIUM_FLAGS}" > "${CHROMIUM_OPTIONS_FILE}"  \
  && BASE_URL='https://chromedriver.storage.googleapis.com' \
  && VERSION=$(curl -sL "${BASE_URL}/LATEST_RELEASE") \
  && curl -sL "https://storage.googleapis.com/chrome-for-testing-public/125.0.6422.60/linux64/chromedriver-linux64.zip" -o /tmp/driver.zip \
  && unzip /tmp/driver.zip \
  && chmod 0755 chromedriver-linux64/chromedriver \
  && mv chromedriver-linux64/chromedriver /root/chromedriver \
  && apt-get purge -y \
    curl \
    unzip \
    gnupg \
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && rm -rf /tmp/* /usr/share/doc/* /var/cache/* /var/lib/apt/lists/* /var/tmp/* \
  && mkdir /root/log \
  && pip install --upgrade pip \
  && pip install --no-cache-dir -r /root/requirements.txt \
  && dos2unix /app/code/getprice.py

# Create a volume for the database file
VOLUME /app/data/

# Run the script when the container launches
CMD ["python3", "/app/code/getprice.py"]

#Pour choper chrome et chromedriver : https://googlechromelabs.github.io/chrome-for-testing/