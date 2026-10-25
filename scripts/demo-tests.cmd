@echo off
chcp 65001 >nul
title HW6-7: демонстрация тестов для видео
cd /d "%~dp0.."
set "PATH=%PATH%;C:\Users\user\.local\bin"
set PYTHONUTF8=1

echo ================================================================
echo  ДЗ 6+7. Демонстрация проверок (эквивалент make-целей, Windows)
echo  Репозиторий: %CD%
echo  Перед каждой секцией пауза: нажмите клавишу, когда запись идёт.
echo ================================================================
echo.
echo Стек MLflow (make up должен быть поднят):
curl -s -o NUL -w "  mlflow http://127.0.0.1:5006/health : %%{http_code}\n" http://127.0.0.1:5006/health
echo.
pause

echo ================================================================
echo  [1/5] Тесты оценки score / quality_gate  (make check-eval)
echo ================================================================
uv run python -m unittest discover -s tests -p "test_*.py" -v
echo.
pause

echo ================================================================
echo  [2/5] Хранение: артефакт переживает --force-recreate (make check-storage)
echo ================================================================
uv run python tests/check_storage.py
echo.
pause

echo ================================================================
echo  [3/5] 9 поведенческих проверок MLflow  (make check)
echo ================================================================
where bash >nul 2>nul
if %ERRORLEVEL%==0 (bash tests/check.sh) else (uv run python tests/check.py)
echo.
pause

echo ================================================================
echo  [4/5] Отрицательная проверка: испорченные ответы отклонены (make check-negative)
echo ================================================================
uv run python -m evaluation.cli negative
echo.
pause

echo ================================================================
echo  [5/5] Гейт качества: ожидаем честный REFUSE, код возврата 1 (make eval)
echo ================================================================
uv run python -m evaluation.cli gate
echo Код возврата гейта: %ERRORLEVEL%  ^(ожидается 1; champion не назначался^)
type metrics\quality-gate.json
echo.
echo ================================================================
echo  Демонстрация завершена. Окно можно закрыть.
echo ================================================================
pause
