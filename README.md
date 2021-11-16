# Animals 

A simple script that gets the animals and sends them home. 

Handles communicating with an unpredictable server.

## Setup
0. Ensure you have the following:
   - python3.x
   - pip
   - docker
   - `lp-programming-challenge-1` docker container locally
1. Install requirements `pip install -r requirements.txt`
2. Ensure animals-api docker container is running:
```bash
 docker run \
   --rm -d --name lp-challenge \
   -p 3123:3123 -e VERIFY=1 -ti lp-programming-challenge-1
```
3. Run the script with `python3 ./main.py`
4. Verify your results with `docker logs -f lp-challenge`. 
   It should say `0 animals left` if everything ran successfully.


## Possible improvements
This project requires a lot of requests that can last a 
long time. It could be sped up significantly using asynchronous 
requests.