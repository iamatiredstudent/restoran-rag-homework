# Tasklist — итерационный план разработки

Опирается на: @vision.md · @conventions.md · @00_project_idea.md · @workflow.md

**Правило:** одна итерация = один проверяемый результат. Не переходить дальше, пока текущий шаг не протестирован.

---

## 📊 Отчёт по прогрессу

| Итерация | Название | Статус | Проверка |
|:--------:|----------|:------:|----------|
| 0 | Каркас проекта | ✅ | `uv sync` без ошибок |
| 1 | Демо-данные Kaggle | ✅ | JSON читается, ≥5 датасетов |
| 2 | Ingestion | ✅ | `documents.jsonl` создан |
| 3 | Chunking | ✅ | `chunks.jsonl`, тест chunking |
| 4 | Индекс TF-IDF | ✅ | файлы в `data/index/` |
| 5 | Retrieval | ✅ | top-k + score в консоли |
| 6 | Demo-ответ | ✅ | ответ + источники без UI |
| 7 | Streamlit UI | ✅ | 3 demo-вопроса в браузере |
| 8 | Тесты и README | ✅ | `pytest` green, README воспроизводим |
| 9 | Документ о данных и репозитории | ✅ | `doc/DATA.md` — источники, назначение |
| 10 | Домашнее задание | ✅ | `homework/` — планирование + итерации |

**Легенда:** ⬜ не начато · 🔄 в работе · ✅ готово · ❌ блокер

**Текущая итерация:** 10  
**Готовность MVP:** 11 / 11

---

## Итерация 0 — Каркас проекта

- [x] `pyproject.toml` — зависимости: streamlit, scikit-learn, pytest
- [x] `.gitignore` — `.venv/`, `data/index/`, `__pycache__/`
- [x] Папки: `app/`, `scripts/`, `data/raw/`, `data/processed/`, `data/index/`, `tests/`
- [x] `app/config.py` — пути, `top_k`, размер чанка

**Проверка:**
```bash
uv venv && uv sync
uv run python -c "import app.config"
```

---

## Итерация 1 — Демо-данные Kaggle

- [x] `data/raw/datasets.json` — 9 жалоб CFPB (из `rows.csv`)
- [x] Поля: `id` (номер записи 0…n), `name`, `text` (на русском)
- [x] `data/raw/rows.csv` в `.gitignore` (скачивается локально с Kaggle)

**Проверка:**
```bash
uv run python -c "import json; d=json.load(open('data/raw/datasets.json')); print(len(d['datasets']))"
```

---

## Итерация 2 — Ingestion

- [x] `scripts/ingest.py` — JSON → `data/processed/documents.jsonl`
- [x] Очистка текста, метаданные (`doc_id`, `name`, `source_file`)

**Проверка:**
```bash
uv run python scripts/ingest.py
# → documents.jsonl, строк = числу датасетов
```

---

## Итерация 3 — Chunking

- [x] `app/chunker.py` — нарезка по абзацам, max 400, overlap 50
- [x] Выход: `data/processed/chunks.jsonl`

**Проверка:**
```bash
uv run python -c "from app.chunker import ..."  # или через build_index позже
uv run pytest tests/test_chunking.py -v
```

---

## Итерация 4 — Индекс TF-IDF

- [x] `scripts/build_index.py` — ingest + chunk + TF-IDF fit
- [x] Сохранение: `data/index/vectorizer.pkl`, `matrix.npz`, `chunks.jsonl`

**Проверка:**
```bash
uv run python scripts/build_index.py
# → три файла в data/index/
```

---

## Итерация 5 — Retrieval

- [x] `app/retriever.py` — загрузка индекса, cosine top-k
- [x] Возврат: `text`, `doc_id`, `score`

**Проверка:**
```bash
uv run python -c "
from app.retriever import Retriever
r = Retriever()
print(r.search('безработица переменные', k=3))
"
```

---

## Итерация 6 — Demo-ответ

- [x] `app/prompts.py` — system-правила (только по контексту, отказ без данных)
- [x] `app/generator.py` — ответ из top-k + список источников

**Проверка:**
```bash
uv run python -c "
from app.generator import ask
print(ask('Какие переменные в датасете про безработицу?'))
"
# → текст + sources с doc_id
```

---

## Итерация 7 — Streamlit UI

- [x] `app/main.py` — поле вопроса, top-k фрагменты, ответ, источники
- [x] Сообщение, если индекс не собран

**Проверка:**
```bash
uv run streamlit run app/main.py
```
Demo-вопросы:
1. «Какие переменные в датасете про безработицу?»
2. «За какой период данные об инфляции?»
3. «Как приготовить борщ?» → отказ

---

## Итерация 8 — Тесты и README

- [x] `tests/test_chunking.py`, `tests/test_retrieval.py` — 3–5 тестов
- [x] Корневой `README.md` — uv, build_index, streamlit, demo-вопросы

**Проверка:**
```bash
uv run pytest tests/ -v
# README: запуск с нуля на чистой машине
```

---

## Итерация 9 — Документ о данных и репозитории

- [x] `doc/DATA.md` — какие данные использованы, откуда, что индексируем / не индексируем
- [x] Раздел **«Назначение репозитория»** — для кого, что демонстрирует, границы MVP
- [x] Ссылки на источники (Kaggle / CFPB и т.п.), лицензия, дата выгрузки
- [x] Ссылка из корневого `README.md` на `doc/DATA.md`

**Проверка:**
```bash
# файл существует, обязательные разделы на месте
uv run python -c "
from pathlib import Path
p = Path('doc/DATA.md')
t = p.read_text(encoding='utf-8')
for s in ['## Источники данных', '## Назначение репозитория', '## Что индексируем']:
    assert s in t, f'нет раздела: {s}'
print('OK')
"
```

---

## Итерация 10 — Домашнее задание

Структура: **сначала планирование (md-файлы по одному)**, **потом реализация (каждая итерация — отдельный шаг)**.

- [x] `homework/README.md` — цель задания, порядок шагов, критерии сдачи
- [x] `homework/00_planning/README.md` — обзор фазы планирования
- [x] Шаги планирования (отдельный файл на каждый md в `doc/`):
  - [x] `homework/00_planning/step_01_project_idea.md` → @00_project_idea.md
  - [x] `homework/00_planning/step_02_vision.md` → @vision.md
  - [x] `homework/00_planning/step_03_conventions.md` → @conventions.md
  - [x] `homework/00_planning/step_04_tasklist.md` → @tasklist.md
  - [x] `homework/00_planning/step_05_workflow.md` → @workflow.md
- [x] `homework/01_implementation/README.md` — обзор фазы реализации
- [x] Шаги реализации (отдельный файл на каждую итерацию 0–8):
  - [x] `iter_00_scaffold.md` … `iter_08_tests_readme.md`
- [x] В каждом step-файле: **что сделать**, **какие файлы**, **как проверить**, **ожидаемый результат**

**Проверка:**
```bash
uv run python -c "
from pathlib import Path
required = [
    'homework/README.md',
    'homework/00_planning/README.md',
    'homework/00_planning/step_01_project_idea.md',
    'homework/00_planning/step_05_workflow.md',
    'homework/01_implementation/README.md',
    'homework/01_implementation/iter_00_scaffold.md',
    'homework/01_implementation/iter_08_tests_readme.md',
]
for f in required:
    assert Path(f).exists(), f'нет файла: {f}'
print('OK:', len(required), 'файлов')
"
```

---

## Критерий «MVP готов»

- [x] Все итерации ✅ в таблице прогресса
- [x] 3 demo-вопроса — ответ с источником; 1 negative — отказ
- [x] Студент может пройти путь: `data/raw/` → index → Streamlit
- [x] `doc/DATA.md` описывает данные и назначение репозитория
- [x] `homework/` — студент может пройти задание шаг за шагом (планирование → итерации)
