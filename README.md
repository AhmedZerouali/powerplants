# powerplant-coding-challenge

## How it works
The application runs on port 8888.

## Requirements
- Python3
- Flask==2.3.2
- Optional: docker (https://docs.docker.com/install/)

Clone or download the source code and run the application: 

### With Python locally
```
$ pip3 install -r requirements.txt
$ python3 server.py
```
### With Docker:

```
$ docker build -t production-plan .
$ docker run -p 8888:8888 production-plan
```

