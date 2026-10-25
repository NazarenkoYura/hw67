# Сценарий видео для сдачи ДЗ 6+7 (5–8 минут)

Запись: экран + звук. Перед записией убедиться, что стек поднят:
`make up` → http://127.0.0.1:5006/health отвечает 200.

## 0:00–0:40. Контекст и репозиторий

- Открыть GitHub-репозиторий (`github.com/NazarenkoYura/hw67`), показать коммиты:
  «Старт ДЗ 6+7» (чистый hw67-broken) → «исправлены 4 дефекта» → «score и
  quality_gate» → sweep-коммиты → «Часть B завершена».
- Одной фразой: тема проекта — Q&A по статистике/ML (датасет Cross Validated
  из ДЗ 3), модель Qwen3-0.6B, продолжение ДЗ 4–5.

## 0:40–2:00. Часть A: 4 дефекта + sweep в MLflow

- Открыть `docs/defects.md`, коротко проговорить 4 дефекта: общий run всех
  кандидатов → отдельные дочерние runs; volume artifacts не примонтирован →
  примонтирован; хеши train/val выкидывались из тегов → полный provenance;
  promote без проверки порога → gate() до register_model.
- Перейти в UI MLflow (http://127.0.0.1:5006, эксперимент hw6-lora): показать
  родительский sweep и 6 отдельных FINISHED-рунов кандидатов; открыть лучший
  (all-r8-high, run 40fb010a): параметры r=8 / lr=3e-4 / все проекции, кривая
  val_loss (шаг 0 = базовая 3.2319 → 2.9584, ratio 0.915 < 1.0), теги
  data_train_sha256 / git_sha, артефакты: адаптер, manifest, samples.json.
- Показать `docs/comparison.csv` — 6 строк, сортировка по final_val_loss.

## 2:00–2:40. Реестр и candidate

- В MLflow → Models → my-qwen-adapter: версия 3, alias **candidate**
  (порождён `make candidate` через порог).
- Терминал: `make predict-candidate` — загрузка `models:/my-qwen-adapter@candidate`
  и ответ (можно заранее прогреть, чтобы не ждать загрузки на видео).

## 2:40–4:20. Часть B: данные, оценка, гейт

- Открыть `data/eval/golden.jsonl` (52 вопроса, 5 срезов, поле source),
  `behavioral.jsonl` (format / paraphrase / refusal), `training-index.jsonl`
  (4748 train-вопросов). Проговорить: DVC-версии, remote `../dvc_remote`,
  `dvc pull` восстанавливает (см. `docs/data-access.md`); контроль утечек:
  `exact_or_group_intersections: 0`.
- `evaluation/params.json`: критический срез probability закреплён ДО оценки,
  один system/лимит/seed/scorer для обеих версий.
- Метрики (можно из `docs/conclusion.md` или UI эксперимента hw67-evaluation,
  run feb3ec12): baseline 0/52 accuracy, 0/52 format; candidate 1/52 accuracy,
  42/52 format; behavioral 0/3 у обеих.
- Ключевой инсайт из разбора пар: единственный исправленный вопрос
  (golden-machine-036) — база «знала» ответ (D), но портила формат фенсами;
  кандидат выучил формат, но 41 из 42 валидных ответов — REFUSE на вопросах
  по теме: 4 шага LoRA на свободных ответах учат оформление, не задачу.

## 4:20–5:20. Отказ гейта и отрицательная проверка

- Терминал: `make eval` → показать отказ «candidate: пройдены не все
  behavioral-кейсы (0/3)», ненулевой код возврата; открыть
  `metrics/quality-gate.json` (passed=false).
- Подчеркнуть: порог не ослаблялся после просмотра результата; champion НЕ
  назначался (`make promote` пропущен по правилам), alias candidate доступен.
- `make check-negative` → PASS: испорченная копия ответов отклонена,
  `metrics/negative-gate.json`, alias не менялся.

## 5:20–6:20. Хранение и финальные проверки

- `make check-storage`: probe-артефакт, `--force-recreate` контейнера mlflow,
  SHA256 совпал (том artifacts пережил пересоздание — дефект 2).
- `make check` → 9/9 PASS (прогнать заранее; на видео показать хвост вывода).
- `make check-eval` → 24/24 OK. Упомянуть единственное изменение tests/
  (нормализация слэшей для Windows) и приложенный diff `docs/tests-diff.patch`.

## 6:20–7:00. Вывод

- Из `docs/conclusion.md`: кандидат выбран по loss честно, качество ответов
  не прошло behavioral-гейт → решение REFUSE, следующий шаг — MCQ-данные или
  больший бюджет, затем повторная оценка тем же протоколом. Отказ по качеству —
  допустимый итог работы.

## Чек-лист перед записью

- [ ] `make up` — стек поднят, UI открывается
- [ ] `make check` — 9/9, `make check-eval` — 24/24
- [ ] Терминал в корне репозитория, `uv` в PATH, кодировка UTF-8
- [ ] Открыты закладки: MLflow (exp 1, exp 2, Models), conclusion.md, metrics/
