FROM registry.access.redhat.com/rhel7/rhel-atomic

MAINTAINER XebiaLabs Development <docker@xebialabs.com>

LABEL name="xebialabs/xl-release" \
      maintainer="docker@xebialabs.com" \
      vendor="XebiaLabs" \
      version="8.5.0" \
      release="1" \
      summary="XL Release" \
      description="Enterprise-scale Application Release Automation for any environment" \
      url="https://www.xebialabs.com/xl-release"

COPY resources/help.md /tmp/

### add licenses to this directory
COPY resources/licenses /licenses

# Install dependencies
RUN INSTALL_PKGS="golang-github-cpuguy83-go-md2man curl hostname shadow-utils" && \
    microdnf install --enablerepo=rhel-7-server-rpms --enablerepo=rhel-7-server-optional-rpms --nodocs ${INSTALL_PKGS} && \
    microdnf update && \
### help file markdown to man conversion
    go-md2man -in /tmp/help.md -out /help.1 && \
    microdnf clean all

RUN microdnf install --enablerepo=rhel-7-server-rpms --nodocs unzip gawk java-1.8.0-openjdk java-1.8.0-openjdk-devel && \
### Set the Java random source
    echo "securerandom.source=file:/dev/urandom" >> /usr/lib/jvm/java/jre/lib/security/java.security && \
    microdnf clean all


ENV USER_UID=10001 APP_ROOT=/opt/xebialabs
ENV APP_HOME=${APP_ROOT}/xl-release-server

# Install XL Deploy
COPY resources/xl-release-8.5.0-server.zip /tmp
RUN mkdir -p ${APP_ROOT} && \
    unzip /tmp/xl-release-8.5.0-server.zip -d ${APP_ROOT} && \
    mv ${APP_ROOT}/xl-release-8.5.0-server ${APP_HOME}

# Add bin/run-in-container.sh
COPY resources/bin/run-in-container.sh ${APP_HOME}/bin/

# Add (and run) Database driver download script
COPY resources/bin/db-drivers.sh /tmp
RUN chmod ugo+x /tmp/db-drivers.sh && \
    /bin/sh /tmp/db-drivers.sh

# Modify bin/run.sh so that java becomes a child process of dumb-init
RUN sed -i 's/^\($JAVACMD\)/exec \1/' ${APP_HOME}/bin/run.sh

# Move and augment conf directory of regular install
RUN mv ${APP_HOME}/conf ${APP_HOME}/default-conf && \
    rm ${APP_HOME}/default-conf/xl-release.conf && \
    mkdir ${APP_HOME}/conf
COPY resources/default-conf ${APP_HOME}/default-conf
RUN mv ${APP_HOME}/default-conf/boot.conf.template ${APP_HOME}/default-conf/xl-release-server.conf.template

# Modify conf/xlr-wrapper-linux.conf to add node-conf to the classpath and to add container-specific VM options
COPY resources/modify-wrapper-linux-conf.gawk /tmp
RUN chmod +x /tmp/modify-wrapper-linux-conf.gawk && \
    /tmp/modify-wrapper-linux-conf.gawk ${APP_HOME}/default-conf/xlr-wrapper-linux.conf > /tmp/xlr-wrapper-linux.conf && \
    mv /tmp/xlr-wrapper-linux.conf ${APP_HOME}/default-conf/xlr-wrapper-linux.conf && \
    rm /tmp/modify-wrapper-linux-conf.gawk

# Create node-specific conf directory and add template for node-specific xl-release.conf file
RUN mkdir ${APP_HOME}/node-conf
COPY resources/node-conf ${APP_HOME}/node-conf

# Move plugins directory
RUN mv ${APP_HOME}/plugins ${APP_HOME}/default-plugins && \
    mkdir ${APP_HOME}/plugins

# Create empty 'repository', 'work' and 'archive' directory
RUN mkdir ${APP_HOME}/repository ${APP_HOME}/archive ${APP_HOME}/work

# Set permissions
RUN chgrp -R 0 ${APP_ROOT} && \
    chmod -R g=u ${APP_ROOT} && \
    chmod g+x ${APP_HOME}/bin/*.sh

COPY resources/amd64/tini ${APP_ROOT}
RUN chmod ugo+x ${APP_ROOT}/tini

WORKDIR ${APP_HOME}

# Don't run as root
RUN useradd -r -M -u 10001 -g 0 xebialabs
USER 10001

VOLUME ["${APP_ROOT}/bootstrap", "${APP_HOME}/archive", "${APP_HOME}/conf", "${APP_HOME}/hotfix", "${APP_HOME}/ext", "${APP_HOME}/plugins", "${APP_HOME}/repository"]
EXPOSE 5516

ENV XL_CLUSTER_MODE=default \
    XL_DB_URL=jdbc:h2:file:${APP_HOME}/repository/xl-release \
    XL_DB_USERNAME=sa \
    XL_DB_PASSWORD=123 \
    XL_METRICS_ENABLED=false \
    XL_CLUSTER_MODE=default \
    SERVER_URL=http://localhost:5516/ \
    XL_REPORT_DB_URL=jdbc:h2:file:${APP_HOME}/repository/xl-release-report \
    XL_REPORT_DB_USERNAME=\${xl.database.db-username} \
    XL_REPORT_DB_PASSWORD=\${xl.database.db-password}


# Environment variables are not expanded when using the exec form of the ENTRYPOINT command. They are
# expanded when using the shell form, but that results in tini running with a PID higher than 1.
ENTRYPOINT ["/opt/xebialabs/tini", "/opt/xebialabs/xl-release-server/bin/run-in-container.sh"]