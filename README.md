# ML Registry
Лабораторная работа №1 + 2. Серверное приложение для реестра ML-задач,
моделей и экспериментов на **FastAPI + SQLAlchemy + Postgres + Alembic**.
---
# В чем смысл? при разработке ML-моделей, особенно нескольких сразу можно начать путать эксперименты, стеки и методы с метриками. 
**Не то что бы это нельзя было сделать просто в экселе, однако большего от нас вроде не требуется и ладно.**
---
В проекте три таблицы - задачи (tasks), модели (models) и эксперименты (experiments). Одну задачу может решать много моделей, у одной модели может быть много разных экспериментов (условно, на разных данных). Удаление каскадное. У каждой таблицы CRUD + Read по ID. 
---
Бизнес - логика:
1. Нельзя добавлять модель в задачу со статусом `done`
2. У одной модели не может быть двух экспериментов в статусе `running`
3. Эксперимент нельзя перевести в `finished` без `accuracy` в диапазоне `[0..1]`
4. Нельзя удалить задачу, если в ней есть `running`-эксперимент
5. Задачу можно перевести в `done`, только если у каждой её модели есть завершённый эксперимент с `accuracy`
---
### Клонировать репозиторий
```bash
git clone <https://github.com/Akolobkov/ONIT1>
cd ONIT1
```
## В докере:
## Требования: 
- Docker
- Docker Compose
```bash
cp .env.example .env
docker compose up --build
```
Остановка:
```bash
# Остановить контейнеры, данные сохраняются
docker compose down

# Остановить и удалить данные (том pgdata)
docker compose down -v
#Открыть в браузере
http://127.0.0.1:8000/docs - сваггер
# Тесты
docker compose exec backend pytest -v
```
## На локалке:
## Требования
- **Python 3.11+**
- **pip**
- **Git**
### Шаг 1. Создать и активировать виртуальное окружение
**Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```
**Windows (cmd):**
```cmd
python -m venv .venv
.venv\Scripts\activate.bat
```
**Linux / macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```
### Шаг 2. Установить зависимости
```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```
### Шаг 3. Создать `.env`
Скопируйте `.env.example` в `.env`.
### Шаг 4. Создать базу данных через миграции
В файле `.env` замените хост `db` на `localhost`:
```
DATABASE_URL=postgresql+psycopg2://onit2:onit2@localhost:5432/ml_registry
```
/\ Важно, чтобы бэкенд обращался к локалхост, иначе работать не будет
```bash
python -m alembic -c alembic.ini revision --autogenerate -m "init postgres"
python -m alembic -c alembic.ini upgrade head
```
### Шаг 5. Запустить приложение
```bash
python -m uvicorn app.main:app --reload
```
### Шаг 6. Открыть в браузере
http://127.0.0.1:8000/docs - сваггер
---
## Тесты
Всего **9 тестов**: 6 unit + 3 integration.
### Запустить все тесты
```bash
pytest -v
```
### Только unit-тесты
```bash
pytest tests/test_unit.py -v
```
### Только integration-тесты
```bash
pytest tests/test_integration.py -v
```
