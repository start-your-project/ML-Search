# ML Search service

API for finding profession in base by query

## Quick start
Build docker image from inside the `ML-Search` directory:
```commandline
docker build -t searchplay .
```
Run docker container :
   ```commandline
   docker run -p -d 8000:8000 searchplay
   ```
Go to http://0.0.0.0:8000/ to see if the search engine is ready.

Making HTTP GET requests examples
 - http://0.0.0.0:8000/search/python -> `{"profession":"python developer"}`
 - http://0.0.0.0:8000/search/тупой%20запрос -> `{"profession":"NAN"}`
