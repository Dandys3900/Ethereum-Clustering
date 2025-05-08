# Ethereum Clustering App

## Content
- Helpers/
    - Contains helper class for enhancing terminal readability by text colouring
- Plotting/
    - Contains collected CSV data about used system resources during clustering operation runtime. Data for each scope are merged into single archive *plotting_data.zip*. Directory also contains Python scripts used for generating resource plots in this thesis.
- Server/
    - API/
        - Contains Python classes each for interaction with given component (database + blockchain client)
    - static/
        - Contains static contents used on webpage(s)
    - templates/
        - Contains main HTML file rendering app's webpage(s)

## Setup
1. Make sure *Docker* and *Docker-compose* are installed
    - For Linux:
        - https://docs.docker.com/engine/install/ubuntu/
        - https://docs.docker.com/compose/install/
2. In root directory of this project, TAR archive *prebuild_image.tar* should be present
3. In root directory, load pre-built Docker image:
`docker load -i prebuild_image.tar`
    - Depending on current system user priviliges, using `sudo` prefix might be needed
4. Final step is to run the application via installed Docker-compose tool: `docker-compose -f docker-compose.yml up`
    - Then just wait for the terminal output from the FastAPI web server containing IP address and port (8000 by default) of the running application instance. To ensure the correct sequence of initialization tasks, in particular starting the database and creating the necessary structures, the startup procedure may take on for several tens of seconds

**In case of having custom running instance of blockchain client**, it is necessary to edited config file located in */Server/API/configFile.yml*. Finally, run the application: `docker-compose -f docker-compose.yml up --build`

### Test examples
Addresses known to produce interesting clusters:
- 0XDAE946D4ECCD27CD370963A181B39D73A872820C
- 0X81E11145FC60DA6EBD43EEE7C19E18CE9E21BFD5

### Unit-tests
The easiest way to run the provided unit-tests is within running application's container.

1. Find image ID of the running instance, look for entry with name "eth_server*": `docker ps`
2. Connect to running container: `docker exec -it IMAGE_ID bash`
3. Then simply type: `pytest`
