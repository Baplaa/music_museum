# Music Museum

Music Museum is an ***asynchronous, containerized Microservices-Based Architecture (MSA)*** application developed incrementally over the course of my last 14-week semester at BCIT in the CIT program.

## Table of Contents
1. [Background](#background)
2. [Infrastructure](#infrastructure)
3. [Technologies Used](#technologies-used)

## Background

Music Museum allows users to POST music singles and albums to the application and retrieve them for content viewing using GET methods.

Music Museum also has a graphical UI which displays:

    1. Application Title
    2. Application Logo
    3. Current Statistics of Information in the Database
        - # of Albums
        - # of Max Album Count
        - # of Single Songs
        - # of Max Single Song Count
        - Last Updated
    4. Current Statuses (health checks) of Microservices
        - Receiver
        - Storage
        - Processing
        - Audit
        - Last Updated
    5. Query Content (in JSON)
        - Albums
        - Single Songs

## Infrastructure

![Infrastructure Diagram](https://github.com/Baplaa/music_museum/blob/main/assets/infrastructure.jpg)

**Music Musuem was stressed tested with **<= 100,000 simulated client applications** using jMeter*

**Microservice**  | **Description**
------------- | -------------
Receiver  | *Receives new endpoint events and publishes records to a Kafka queue*
Storage  | *Consumes events from a Kafka queue and stores them in a MySQL DB*
Processing  | *Connects to Storage with GET calls in order to process stored events for statistics in a JSON file*
Audit  | *Consumes events from a Kafka queue for Event Sourcing*
Dashboard  | *A Single-page application (SPA) to dynamically display information about Music Museum*
Health  | *Performs health checks on each microservice*

Each microservice is:
- containerized using Docker
- have external
    - configuration
    - and logging
- examined using Pylint

## Technologies Used
- [Apache Kafka](https://kafka.apache.org/) - *Publish and Consume pattern for event processing*
- [Apache jMeter](https://jmeter.apache.org/) - *simulated client-apps for stress tests*
- [Azure Virtual Machines](https://azure.microsoft.com/en-ca/products/virtual-machines) - *cloud solution for Music Museum*
- [Docker](https://www.docker.com/) - *containerization for microservices*
- [JavaScript](https://developer.mozilla.org/en-US/docs/Web/JavaScript), [HTML](https://developer.mozilla.org/en-US/docs/Web/HTML), & [CSS](https://developer.mozilla.org/en-US/docs/Web/CSS) - *technologies used for front-end web development*
- [Jenkins](https://www.jenkins.io/) - *CI/CD solution for Music Museum*
- [JSON](https://www.json.org/json-en.html) - used as a statistics storage solution for Processing
- [MySQL](https://www.mysql.com/) - *used as a relational database storage solution*
- [NGiNX](https://www.nginx.com/) - *used for Load Balancer capabilities*
- [OpenAPI](https://www.openapis.org/) - *foundational resource for HTTP API develpoment*
- [Python](https://www.python.org/) - *main logic language of microservices*
