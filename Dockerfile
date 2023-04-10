FROM python:3.9

WORKDIR /search

COPY requirements.txt .
RUN pip install -r requirements.txt
RUN python -m nltk.downloader stopwords

ENV SEARCH_CONFIG_PATH=configs/search_config.yaml

COPY . .

EXPOSE 8000

CMD ["uvicorn", "src.server:app", "--host", "0.0.0.0", "--port", "8000"]