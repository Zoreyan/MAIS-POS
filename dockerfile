# Указываем базовый образ
FROM python:3.10-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем зависимости
COPY requirements.txt requirements.txt

# Устанавливаем зависимости
RUN apt-get update && apt-get install -y redis-tools

RUN pip install --no-cache-dir -r requirements.txt

# Копируем все файлы проекта
COPY . .

# Устанавливаем права для entrypoint
RUN chmod +x entrypoint.sh

# Указываем точку входа
ENTRYPOINT ["./entrypoint.sh"]