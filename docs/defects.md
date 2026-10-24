# ДЗ 6+7. Разбор четырёх дефектов стартера

Формат: причина → исправление → доказательство. Отпечаток `tests/` не менялся
(`c42ac7788026`, проверяется `bash tests/check.sh`).

## Дефект 1. Один общий run для всех кандидатов

**Причина.** `src/sweep.py` оборачивал обучение всех шести кандидатов в один
вложенный run `all-candidates`: метрики шести разных моделей писались в один run,
у кандидатов не было собственных `run_id`. Сравнение и выбор (`select` в
`src/promote.py`) ищут отдельные runs с `tags.kind = 'candidate'` — находили один.

**Исправление.** Цикл по кандидатам вынесен из вложенного run: каждый кандидат
обучается в собственном `mlflow.start_run(run_name=candidate["name"], nested=True)`
внутри родительского sweep-run.

**Доказательство.** `make check`, проверка 1: `PASS — минимум шесть отдельных
законченных runs`; все шесть конфигураций из `params.yaml` находятся как отдельные
FINISHED-руны с `tags.candidate`. `docs/comparison.csv` содержит шесть строк
с шестью разными `run_id` (генерируется `src/report.py` из MLflow).

## Дефект 2. Потеря файлов после замены контейнера

**Причина.** `compose.yaml` объявлял volume `artifacts`, но не монтировал его:
`--artifacts-destination=/mlartifacts` указывал внутрь слоя контейнера.
`docker compose up --force-recreate` пересоздаёт контейнер — артефакты (адаптеры,
samples, probe) пропадали, ссылки `runs:/.../model` ломались.

**Исправление.** Сервису `mlflow` добавлена примонтированная файловая система:
`volumes: [artifacts:/mlartifacts]`. Артефакты живут в именованном volume,
который переживает пересоздание контейнера (и `make down`, который volumes не удаляет).

**Доказательство.** `make check-storage`: probe-артефакт со случайной строкой
логируется, контейнер mlflow пересоздаётся `--force-recreate --no-deps`, артефакт
скачивается из нового контейнера, SHA256 совпадает (`metrics/storage-check.json`,
проверка 8 в `make check`).

## Дефект 3. Отсутствие версий train/val в тегах runs

**Причина.** `src/sweep.py` собирал provenance и выкидывал из него хеши данных:
`versions = {k: v for k, v in provenance(p).items() if not k.startswith("data_")}`.
Теги `data_train_sha256` / `data_val_sha256` не попадали в runs — нельзя доказать,
на каких тензорах ДЗ 4 обучался кандидат.

**Исправление.** Фильтр убран, в теги пишется полный `provenance(p)`: git sha,
`code_sha256`, `config_sha256`, `data_train_sha256`, `data_val_sha256`.

**Доказательство.** `make check`, проверка 2: `PASS — код, данные, конфиг и база
имеют версии`; теги всех шести runs совпадают с текущими SHA256 `src/`,
`params.yaml`, `data/tokenized/train.pt`, `data/tokenized/val.pt`.

## Дефект 4. Обход порога по loss при продвижении

**Причина.** `src/promote.py` вычислял `ratio = final_val_loss / base_val_loss`
и сразу регистрировал модель: порог `registry.max_val_ratio` не проверялся.
Любой кандидат, даже ухудшивший val loss, попадал в реестр с тегом `validation: passed`.

**Исправление.** Перед `mlflow.register_model` вызывается `gate(run, threshold)`:
не конечные метрики, незавершённый run и превышение порога дают `ValueError`
до каких-либо записей в реестр.

**Доказательство.** `make check`, проверка 6: `PASS — запрет регистрации при
непройденном пороге`: `promote(..., max_ratio=0.0)` обязан упасть с `ValueError`
(проверяется во временном реестре, учебные alias не затрагиваются). Реальный
sweep: у всех шести кандидатов ratio < 1.0 (см. `docs/comparison.csv`).

## Дополнительные изменения вне дефектов

- `params.yaml`: demo-промпты пневмонии/ферритина заменены вопросами по теме
  проекта (статистика/ML, датасет Cross Validated из ДЗ 3); промпты и system —
  ASCII (английские): `python -I` в проверке 7 игнорирует `PYTHONUTF8`, и кириллица
  в stdout дочернего процесса ломает сравнение ответов.
- `params.yaml`: `dtype: float32` — bf16 на этом CPU без аппаратной поддержки
  медленнее в разы; тип одинаков для всех шести кандидатов, сравнение честное.
- `src/sweep.py`: путь адаптера в `log_model` передаётся с прямыми слэшами —
  с Windows-обратными MLmodel хранит `artifacts\adapter`, и скачивание
  `model/.../adapter_config.json` через REST-сервер артефактов падает с 500.
- `Makefile`: `PYTHONUTF8 := 1` — UTF-8 чтение конфигов с кириллицей на Windows.
