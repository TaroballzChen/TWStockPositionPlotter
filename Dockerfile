FROM python:3.10-bookworm

WORKDIR /TWStockPositionViewer
VOLUME /public
VOLUME /private

RUN apt update
RUN apt install -y python3-pip cron tzdata fonts-wqy-zenhei

RUN pip3 install shioaji pandas matplotlib python-dotenv BeautifulSoup4 seaborn

COPY *.py /TWStockPositionViewer/

COPY crontab /etc/cron.d/my-cron
RUN chmod 0644 /etc/cron.d/my-cron
RUN crontab /etc/cron.d/my-cron

COPY start.sh /start.sh
RUN chmod +x /start.sh

ENV PYTHONUNBUFFERED=1
ENV TZ=Asia/Taipei

CMD ["/start.sh"]