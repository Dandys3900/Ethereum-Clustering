### Run web server manually
In home directory of project, run:
`fastapi dev Server/Web_Server.py`

### Test examples
Few addresses known to produce interesting graphs:
- 0X0BE73D80023FB06C25DD7EA2CE86AE8653443739
- 0X0206FBE501E2D89D858C13FE8117CB2F93CD9348
- 0XDAE946D4ECCD27CD370963A181B39D73A872820C

## Docker
To build image of THIS PROJECT ONLY stuff, run:
`docker build -t eth_server .`
`docker save -o bp_app.tar eth_server:latest`
`docker load -i bp_app.tar`

Before following, make sure Docker Desktop is ON and it's Nebula extension container is PAUSED.

Then to build and run container with both THIS PROJECT & NebulaGraph, run:
`docker-compose -f docker-compose.yml up --build`
or without triggering build sequence
`docker-compose -f docker-compose.yml up`

To transfer docker image to Anton
`scp -i ~/.ssh/id_ed25519 -P 25021 bp_app.tar xdanie14@anton4.fit.vutbr.cz:/home/xdanie14/project`

To monitor system during clustering
`glances --export csv --export-csv-file usage_log.csv --disable-plugin percpu`
