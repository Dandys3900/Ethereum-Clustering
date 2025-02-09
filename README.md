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

Before following, make sure Docker Desktop is ON and it's Nebula extension container is PAUSED.

Then to build and run container with both THIS PROJECT & NebulaGraph, run:
`docker-compose -f docker-compose.yml up --build`
