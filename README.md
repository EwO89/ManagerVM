# ManagerVM

**Зависимости**:
- Python 3.12
- Docker
- Makefile (`sudo apt install make`)

**Запуск**:

- `git clone https://github.com/EwO89/ManagerVM.git` - клонирование репозитория
- `python -m venv venv` - создание виртуального окружения
- `source venv/bin/activate` - активация виртуального окружения
-  НА Windows: `venv/Scripts/activate`
-  переименование .env.sample в .env
- `make r` - скачивание requirements
- `make docker-up` - запуск postgres в докере
- `make start` - запуск приложения

***Тесты***:
- `make test` - запуск тестов

***Видео***:
- ссылка > https://drive.google.com/drive/folders/1HHghmescC3qAKLqk0IZyGvwt2OIct6oN?usp=drive_link
  
***ТЗ***:
 - ссылка на ТЗ > https://docs.google.com/document/d/1lNCpFL3w_8O_iOvRhlAbkwyO8WnrNPfj/edit?usp=drive_link&ouid=106308963898479999770&rtpof=true&sd=true
