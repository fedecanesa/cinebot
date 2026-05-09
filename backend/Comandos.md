## Loguearnos con Docker

docker login

## Construimos la Imagen y hacemos un Push en nuestro Dockerhub

docker buildx build --platform linux/amd64 -t fedecanesa/cinebot-backend:latest --push .
