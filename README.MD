docker-compose down
docker volume rm site_monitoring_statics_volume
docker-compose build
docker-compose up -d