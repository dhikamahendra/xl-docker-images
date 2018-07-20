FROM alpine:3.7

COPY resources/xl /usr/local/bin
RUN chmod +x /usr/local/bin/xl

USER 10001
VOLUME "/data"

ENTRYPOINT ["/usr/local/bin/xl"]
