FROM python:3.8

RUN apt-get update

RUN addgroup apollo
RUN useradd -g apollo apollo

COPY . /home/apollo/apollo
WORKDIR /home/apollo

RUN pip install -e apollo[dev]

# Download wait-for-it to allow waiting for dependency containers
RUN mkdir util
RUN curl https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh > util/wait-for-it.sh
RUN chmod +x util/wait-for-it.sh

WORKDIR /home/apollo/apollo

EXPOSE 8000
ENTRYPOINT ["uvicorn"]
CMD ["apollo:app", "--reload", "--host", "0.0.0.0"]
