FROM python:3.6

RUN apt-get update \
    && apt-get install -y ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY docker/get_dakara.sh /
RUN chmod u+x get_dakara.sh && /get_dakara.sh

RUN pip install -r /dakara-server/requirements.txt

COPY ./ /dakaraneko
RUN pip install -r /dakaraneko/karaneko/requirements.txt

ENV DAKARA_SERVER_DIR=/dakara-server
ENV DAKARANEKO_DIR=/dakaraneko
ENV KARA_DIR=/karabase

COPY docker/entrypoint.sh /
RUN chmod u+x entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
CMD ["run"]
