#!/bin/sh
# Проверка, что Redis доступен
until redis-cli -h redis ping; do
  echo "Ожидание Redis..."
  sleep 1
done
echo "Redis доступен!"
