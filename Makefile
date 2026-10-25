# Windows: конфиги и JSON содержат кириллицу; без UTF-8 Python читает их в cp1251.
export PYTHONUTF8 := 1
# Git Bash / VS Code: uv живёт в ~/.local/bin и не всегда есть в PATH терминала.
export PATH := $(HOME)/.local/bin:$(PATH)

.PHONY: install up down sweep promote predict check check-storage mlflow-up
install:
	uv sync --frozen
up:
	docker compose -p mlops-hw6 up --build -d --wait
down:
	docker compose -p mlops-hw6 down
mlflow-up:
	@curl -s -o /dev/null --max-time 5 http://127.0.0.1:5006/health \
	  || { echo 'MLflow (127.0.0.1:5006) недоступен: запустите Docker Desktop, затем make up'; exit 1; }
sweep:
	uv run python -m src.sweep
promote:
	uv run python -m evaluation.cli promote
predict:
	uv run python -m src.predict --uri models:/my-qwen-adapter@champion --prompt "Which measure of central tendency is most robust to outliers? A - mean, B - median, C - mode, D - range. choices: A, B, C, D."
check: mlflow-up
	bash tests/check.sh
check-storage: mlflow-up
	uv run python tests/check_storage.py

.PHONY: report candidate baseline-init evaluate eval check-eval check-negative check-all baseline-update predict-candidate
report:
	uv run python -m src.report
candidate:
	uv run python -m evaluation.cli candidate
baseline-init:
	uv run python -m evaluation.cli baseline-init
evaluate:
	uv run python -m evaluation.cli evaluate
eval:
	uv run python -m evaluation.cli gate
check-eval:
	uv run python -m unittest discover -s tests -p 'test_*.py' -v
check-negative:
	uv run python -m evaluation.cli negative
check-all: check check-eval
baseline-update:
	uv run python -m evaluation.cli baseline-update
predict-candidate:
	uv run python -m src.predict --uri models:/my-qwen-adapter@candidate --prompt "Какая мера центральной тенденции наиболее устойчива к выбросам? A - среднее, B - медиана, C - мода, D - размах. choices: A, B, C, D."
