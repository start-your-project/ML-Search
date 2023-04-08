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

Search:
 - http://0.0.0.0:8000/search/python -> `{"profession":"python developer"}`
 - http://0.0.0.0:8000/search/тупой%20запрос -> `{"profession":"NAN"}`

Reccommend system:
- http://0.0.0.0:8000/recommend/c -> `{"professions":["c# developer","c++ developer","c developer","mlops","ml researcher"]}`
- http://0.0.0.0:8000/recommend/docker?n=3 -> `{"professions":["devops","MongoDB","mlops"]}`


