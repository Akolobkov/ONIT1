+102
Lines changed: 102 additions & 0 deletions


Original file line number	Diff line number	Diff line change
@@ -0,0 +1,102 @@
# ML Registry
Лабораторная работа №1. Серверное приложение для реестра ML-задач,
моделей и экспериментов на **FastAPI + SQLAlchemy + SQLite + Alembic**.
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
## Требования
- **Python 3.11+**
- **pip**
- **Git** (опционально)
---
## Установка и запуск
### Шаг 1. Клонировать репозиторий
```bash
git clone <https://github.com/Akolobkov/ONIT1>
cd ONIT1
```
### Шаг 2. Создать и активировать виртуальное окружение
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
### Шаг 3. Установить зависимости
```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```
### Шаг 4. Создать `.env`
Скопируйте `.env.example` в `.env`.
### Шаг 5. Создать базу данных через миграции
Удобная штука этот ваш Алембик!
```bash
python -m alembic -c .\alembic.ini upgrade head
```
### Шаг 6. Запустить приложение
```bash
python -m uvicorn app.main:app --reload
```
### Шаг 7. Открыть в браузере
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