# Используем официальный образ Python
FROM python:3.12.0-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем файлы проекта в контейнер
COPY . /app/

# Устанавливаем зависимости из requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Открываем порт для работы сервера
EXPOSE 8000

# Запуск Django-сервера
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
