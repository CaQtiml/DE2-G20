# Instructions for Setting Up Pulsar and Broker

The `/pulsar_setup` directory contains the setup and automation scripts.

## System Overview

| Role                      | VM             |
|---------------------------|----------------|
| Broker / Consumer / Ansible control | `Group20_1`   | |
| Producers (x4)            | `Group20_2~5`  | Execute producer scripts (each responsible for one query) |

All VMs have been pre-created and provisioned on **OpenStack**.  
Access is handled via SSH and Ansible using a shared key (`cluster-key`).


## Directory Structure

```bash
pulsar_setup/
├── inventory.ini                      # VM configuration for Ansible
├── cluster-keys/                      # SSH key pair for Ansible access (private)
├── playbooks/                         # Ansible deployment scripts
│   ├── install_brocker_consumer.yml   # Sets up Pulsar + consumer on Group20_1
│   ├── install_producer.yml           # Sets up Python + pulsar-client on producers
│   ├── install_producer_dependencies.yml  # Installs additional Python dependencies
├── scripts/
│   └── producer-requirements.txt      # Python packages for producer nodes
```


Deployment Tutorial

1. Enter the setup directory
    ```
    cd DE2-G20/pulsar_setup/
    ```

2. Configure inventory file (already pre-filled)

    Ensure the IP addresses and SSH key path are correct in inventory.ini.

    > This file is already pre-filled for our 5 OpenStack VMs.

3. Deploy Broker + Consumer (on Group20_1)

    ```
    ansible-playbook -i inventory.ini playbooks/install_brocker_consumer.yml
    ```

    This playbook will:
    - Install Docker
    - Pull and run apachepulsar/pulsar:2.9.4 in standalone mode
    - Expose ports 6650 (Pulsar client) and 8080 (HTTP UI)
    - Install python3, pip, and pulsar-client for the consumer

4. Deploy Producers (on Group20_2 ~ Group20_5)

    Step 1 – Basic Python + Pulsar client:
    ```
    ansible-playbook -i inventory.ini playbooks/install_producer.yml
    ```
    Step 2 – Install additional Python dependencies:
    ```
    ansible-playbook -i inventory.ini playbooks/install_producer_dependencies.yml
    ```

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
