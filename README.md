# Instructions for Setting Up Pulsar and Broker: TBD

# Docker Directory
The `/docker` directory is used to build the Docker image. You need to update the GitHub token and broker address in the `.env` file.

## Pulling the Docker Image
Use the following command to pull the image from Docker Hub:

```bash
docker pull morioxd/de2-project:latest
```

## Running Scripts
To run different scripts, use the following command:

```bash
docker run --rm --env-file .env morioxd/de2-project python pulsar_producer_commit.py
```

- The last part of the command specifies the script to run, so change it accordingly.
- This command uses the host's `.env` file, which needs to be configured as shown in the image below:

![Environment Configuration](https://github.com/user-attachments/assets/0bce54ae-5b1a-4042-b264-0c000eaee707)

## Making Changes to the Image
If you want to make changes to the image, follow these steps:

1. Build the image:
    ```bash
    docker build -t morioxd/de2-project .
    ```

2. Push the updated image to Docker Hub:
    ```bash
    docker push morioxd/de2-project:latest
    ```

# Instructions for Getting Results: TBD
