This directory is used to build the docker image. Need to change the git hub token and broker address in .env

Use docker pull to pull the image from dockerhub:
docker pull morioxd/de2-project:latest


These commands are used to run the different scripts:

docker run --rm --env-file .env morioxd/de2-project python pulsar_producer_commit.py
The last part of the command is the scipt what will run, so change it accordingly. 
This command uses the hosts .env file which need to be set according to the picture attached in the bottom of this file. 


If you want to make changes to the image, first build the image and then push it using this:
docker build -t morioxd/de2-project .
docker push morioxd/de2-project:latest


![image](https://github.com/user-attachments/assets/0bce54ae-5b1a-4042-b264-0c000eaee707)


