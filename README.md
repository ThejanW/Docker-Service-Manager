# Docker-Service-Manager
A tool to manage &amp; monitor containerized web applications

# Quickstart
I've already built the the Master dockerfile and pushed to Dockerhub. Pull it first.

`docker pull thejanw/docker-service-manager`

Then, pull the reverse proxy that I'm currently using.

`docker pull jwilder/nginx-proxy:0.4.0`

Once pulled the above two images, run Docker Service Manager with this command,

`docker run -it -p 8765:8765 -v /var/run/docker.sock:/var/run/docker.sock:ro thejanw/docker-service-manager`

Then head to http://localhost:8765/ and you will see a web GUI similar to this.

![alt text](https://raw.githubusercontent.com/ThejanW/Docker-Service-Manager/master/imgs/dsm-service-summary.png)

If you don't have these images in your machine, you'll have to pull them by heading to the relevant tab in the SERVICES pane. 
You will see the pulling progress in real time. 

![alt text](https://raw.githubusercontent.com/ThejanW/Docker-Service-Manager/master/imgs/dsm-pulling-image.png)

Once the pull is completed, you will see the START button in the service window of the pulled image, By pressing the start button,
you'll be running it on your machine with a VIRTUAL_HOST. 
All these configurations are in the dsm-config.json file which is located in the Master folder in this repository.
Head to the service summary page and see the running services, if it is running you can issue a cURL commands like these,
you will get the index page of each service.

`curl -H "Host: object_recognition-image.tika.dl" localhost:8764/`

`curl -H "Host: captioning-image.tika.dl" localhost:8764/`

# TODO

1. The current automated reverse proxy I'm using doesn't support does not support VIRTUAL_PATH although it supports VIRTUAL_HOST. 
Therefore I can’t proxy into the url paths in the server back ends. 
I found a possible alternative to this. Let’s see how it goes. 

2. Including CPU usage, usage statistics graphs to services.

3. Allowing to change the dsm-config.json file through a web form.
