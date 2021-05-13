# agar.aio

Bot for the online multiplayer game [agar.io](https://agar.io/). Trained with a local Node.js server modified from [juslee/agar-io-clone](https://github.com/juslee/agar-io-clone)

---

| <a href="https://sampsonjacob.com" target="_blank">**Jacob Sampson**</a> |
| :----------------------------------------------------------: |
| [![JacobSampson](https://avatars3.githubusercontent.com/u/42616056?s=200&v=4)](http://sampsonjacob.com) |
| <a href="http://linkedin.com/in/jacob-i-sampson" target="_blank"><img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white"></a> <a href="mailto: jacob.samps@gmail.com"><img src="https://img.shields.io/badge/Gmail-D14836?style=for-the-badge&logo=gmail&logoColor=white"></a>  |

## About

See [report.pdf](report/report.pdf) for a full report

## Getting Started

### Requirements

- Python
  - Dependencies in [requirements.txt](requirements.txt)
- Graphviz
    - `conda install graphviz`
- Docker
  - `docker-compose`

### Running

Run `sh train.sh` to start training program

Run the local Node.js server on a specific port
```bash
SERVER_PORT=3000 docker-compose -f servers/gulp/docker-compose.yaml up --build
```

### Tips

```bash
# Shows the IP address of the running server
`docker-machine inspect default | grep IPAddress`

# Stop and remove all Docker images
docker kill $(docker ps -q)
echo "y" | docker container prune
```
