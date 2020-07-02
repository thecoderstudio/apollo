FROM python:3.8

ENV PATH="${PATH}:/usr/local/go/bin"

RUN addgroup apollo
RUN useradd -g apollo apollo

COPY . /home/apollo/apollo
WORKDIR /home/apollo

RUN pip install -e apollo[dev,tests]

# Install Go to allow Apollo to compile the agent
RUN wget https://golang.org/dl/go1.14.4.linux-amd64.tar.gz
RUN tar -C /usr/local -xzf go1.14.4.linux-amd64.tar.gz
RUN rm go1.14.4.linux-amd64.tar.gz

# Download wait-for-it to allow waiting for dependency containers
RUN mkdir util
RUN curl https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh > util/wait-for-it.sh
RUN chmod +x util/wait-for-it.sh

WORKDIR /home/apollo/apollo

EXPOSE 8000
ENTRYPOINT ["uvicorn"]
CMD ["apollo:main", "--reload", "--host", "0.0.0.0"]
