# ML Search service

API for finding profession in base by query

## Quick start
Build docker image from inside the `ML-Search` directory:
```commandline
docker build -t searchplay .
```
Run docker container :
   ```commandline
   docker run -d -p 8000:8000 searchplay
   ```
Go to http://0.0.0.0:8000/ to see if the search engine is ready.

Making HTTP GET requests examples

Search:
 - http://0.0.0.0:8000/role_search/python -> `{"profession":"python developer"}`, *status 200*
 - http://0.0.0.0:8000/role_search/тупой%20запрос -> `{"detail":"Nothing was found"}`, *status 404*

Role hints:
- http://0.0.0.0:8000/recommend/c -> `{"professions":["c# developer","c++ developer","c developer","mlops","ml researcher"]}`, *status 200*
- http://0.0.0.0:8000/recommend/docker?n=3 -> `{"professions":["devops","MongoDB","mlops"]}`, *status 200*

CV_analyze for profession: ...

Technoloy hints: ...

**Swagger for full API documentation:** http://0.0.0.0:8000/docs.
