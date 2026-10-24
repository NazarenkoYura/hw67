# Доступ к данным оценки (часть B)

Наборы оценки версионируются в DVC, в Git лежат только `.dvc`-указатели с MD5.

## Файлы

| Файл | Содержимое | Размер | Версия |
|---|---|---|---|
| `data/eval/golden.jsonl` | 52 авторских проверенных MCQ по статистике/ML, 5 срезов | 27 063 Б | `data/eval/golden.jsonl.dvc` |
| `data/eval/behavioral.jsonl` | 3 behavioral-кейса: format, paraphrase, refusal | 1 499 Б | `data/eval/behavioral.jsonl.dvc` |
| `data/eval/training-index.jsonl` | Полный индекс 4748 исходных train-вопросов (ДЗ 3, Cross Validated) для контроля утечки | 4.6 МБ | `data/eval/training-index.jsonl.dvc` |

## Remote

Локальная директория `../dvc_remote` относительно корня репозитория
(`C:\Users\user\Documents\GitHub\dvc_remote`), задана в `.dvc/config`:

```
['remote "storage"']
    url = ../../dvc_remote
```

## Как восстановить данные

```bash
dvc pull data/eval/golden.jsonl.dvc data/eval/behavioral.jsonl.dvc data/eval/training-index.jsonl.dvc
```

(объекты уже отправлены в remote командой `dvc push` с теми же целями;
проверено: удаление `golden.jsonl` и `dvc pull` восстанавливает файл байт-в-байт)

## Происхождение и разметка

- `golden.jsonl` и `behavioral.jsonl`: авторские вопросы, сгенерированы и
  проверены скриптом `scripts/prepare_eval.py` (он же печатает результат
  `validate_golden` — контроль точных пересечений и group_id с train).
  Источник фактов: стандартные учебники (Casella & Berger; ISLR; Wasserman).
  Поле `source` заполнено в каждой строке.
- `training-index.jsonl`: построен из `train.jsonl` ДЗ 3 (сплит по темам,
  seed 42) — поля `id`, `group_id` (тема), `input` (текст вопроса).
- Токенизированные тензоры обучения (`data/tokenized/*.pt`) — из ДЗ 4,
  в Git не входят (`.gitignore`), хеши зафиксированы в тегах MLflow-runs.

## Контроль утечки

`evaluation/contract.py:validate_golden` при каждом запуске оценки проверяет:
нет точных нормализованных совпадений вопросов golden ↔ train, нет общих
`group_id`, нет дублей внутри golden. Результат логируется в MLflow
(`evaluation/leakage.json`) и попадает в отчёты: `exact_or_group_intersections: 0`.
