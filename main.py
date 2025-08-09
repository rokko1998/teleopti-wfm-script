#!/usr/bin/env python3
"""
wfm_single.py — Рефакторированная версия скрипта выгрузки «потерянных» и «превышения» из Teleopti.

АКТУАЛЬНЫЕ КОМАНДЫ ДЛЯ ЗАПУСКА:

1. НОВЫЙ РЕЖИМ (рекомендуется) - автоматическое определение даты из первой строки:
   python main.py ваш_файл.xlsx --auto-date-processing

2. НОВЫЙ РЕЖИМ с дополнительными опциями:
   python main.py ваш_файл.xlsx --auto-date-processing --with-skills --no-headless

3. СТАНДАРТНЫЙ РЕЖИМ - обработка всех проблем:
   python main.py ваш_файл.xlsx --out-csv result.csv --no-headless

4. СТАНДАРТНЫЙ РЕЖИМ с навыками:
   python main.py ваш_файл.xlsx --with-skills --no-headless

ОПИСАНИЕ НОВОГО РЕЖИМА:
- Автоматически определяет дату из первой строки данных
- Обрабатывает только строки с этой датой
- Сохраняет результаты в исходный файл в колонки "Потерянные" и "Полученные"
- Создает эти колонки автоматически, если их нет

Модульная структура:
- modules/selenium_helpers.py - Настройка WebDriver и вспомогательные функции
- modules/date_time_utils.py - Работа с датами и временными интервалами
- modules/regions.py - Работа с регионами (рабочая нагрузка)
- modules/skills.py - Работа с навыками
- modules/data_processing.py - Обработка данных и вычисления
- modules/download_manager.py - Скачивание отчетов
- modules/excel_manager.py - Работа с Excel файлами
"""

from __future__ import annotations

import sys
import argparse
import yaml
from pathlib import Path
from loguru import logger

# Импорты из наших модулей
from modules.selenium_helpers import get_driver, setup_proxy, apply_cdp_download_settings
from modules.data_processing import (
    process_excel_data,
    validate_region_in_config,
    calc_metrics,
    create_result_record,
    save_results_to_csv
)
from modules.date_time_utils import windows_for_row, prepare_datetime_for_report
from modules.skills import setup_skills, prepare_skills_from_config, show_page_diagnostics
from modules.download_manager import download_report
from modules.excel_manager import (
    get_date_from_row_first_cell,
    calculate_time_window_for_date,
    save_single_result_to_original_file
)

# Константы
BASE_DIR = Path(__file__).resolve().parent


def main():
    """Основная функция."""
    parser = argparse.ArgumentParser(description="WFM script for extracting lost calls and excess traffic from Teleopti")
    parser.add_argument("input_xlsx", help="Файл Power Query (Свод.xlsx)")
    parser.add_argument("--yaml-cfg", help="region_skills.yml", default=None)
    parser.add_argument("--out-csv", help="Файл вывода", default="wfm_metrics_daily.csv")
    parser.add_argument("--headless", help="Запуск в headless режиме", action="store_true", default=True)
    parser.add_argument("--no-headless", help="Запуск с видимым браузером", action="store_true")
    parser.add_argument("--with-skills", help="Включить работу с навыками (добавление без очистки)", action="store_true")
    parser.add_argument("--auto-date-processing", help="Автоматически определять дату из первой строки и обрабатывать только строки с этой датой", action="store_true")

    args = parser.parse_args()

    input_xlsx_path = Path(args.input_xlsx)
    yaml_path = Path(args.yaml_cfg) if args.yaml_cfg else BASE_DIR / "region_skills.yml"
    out_csv_path = Path(args.out_csv)
    headless = args.headless and not args.no_headless

    # Настраиваем прокси
    setup_proxy()

    # Загружаем конфигурацию
    cfg = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))

    # Подготавливаем навыки, если включен флаг --with-skills
    skills_ids = None
    if args.with_skills:
        logger.info("🎯 Включена работа с навыками (флаг --with-skills)")
        skills_ids = prepare_skills_from_config(cfg)
    else:
        logger.info("ℹ️ Работа с навыками отключена (добавьте флаг --with-skills для включения)")

    # Обрабатываем Excel данные
    df = process_excel_data(input_xlsx_path)

    # Определяем режим работы
    use_auto_date_processing = args.auto_date_processing

    if use_auto_date_processing:
        logger.info("🆕 Включен новый режим автоматической обработки по дате")
        logger.info("📅 Дата будет автоматически определена из первой строки данных")
        logger.info("💾 Результаты будут сохранены в исходный Excel файл")
        logger.info("⚠️ ВАЖНО: Убедитесь, что файл {input_xlsx_path.name} закрыт в Excel перед запуском!")
    else:
        logger.info("📋 Используется стандартный режим работы (обработка всех проблем)")

    # Инициализируем WebDriver
    driver = get_driver(headless=headless)
    results = []

    try:
        # --- НАВЫКИ: Добавляем ОДИН РАЗ В НАЧАЛЕ (если включены) ----------------------------
        if skills_ids:
            logger.info(f"🎯 Настраиваем навыки (БЕЗ ОЧИСТКИ): {skills_ids}")
            logger.info("🔍 Переходим на страницу отчета для настройки навыков...")

            # Переходим на страницу отчета для настройки навыков
            from modules.selenium_helpers import REPORT_URL
            driver.get(REPORT_URL)

            # Применяем CDP настройки
            apply_cdp_download_settings(driver)

            # Ждем загрузки страницы (простое ожидание)
            logger.info("⏳ Ждем загрузки страницы...")
            import time
            time.sleep(5)  # Просто ждем 5 секунд

            # Показываем диагностику что загрузилось
            show_page_diagnostics(driver)

            logger.info("✅ Продолжаем к поиску навыков...")

            # Настраиваем навыки
            if not setup_skills(driver, skills_ids):
                logger.error("❌ КРИТИЧЕСКАЯ ОШИБКА: Не удалось настроить навыки!")
                return

        logger.info("🚀 Начинаем обработку данных из Excel...")

        if use_auto_date_processing:
            # Новый режим: обрабатываем все строки подряд,
            # а дату берём из первой ячейки каждой строки
            logger.info("🆕 Режим: дата берётся из каждой строки (первая ячейка)")

            # Обрабатываем каждую строку исходного DataFrame
            for idx, row in df.iterrows():
                # Дата для конкретной строки
                try:
                    target_date = get_date_from_row_first_cell(row)
                except Exception:
                    logger.warning(f"⚠️ Пропускаем строку #{idx}: не удалось извлечь дату из первой ячейки")
                    continue

                region = row["Регион"]
                mass_number = row["Номер массовой"]
                logger.info(f"🔄 Обрабатываем строку #{idx}: {mass_number} - {region} (дата: {target_date.strftime('%d.%m.%Y')})")

                # Проверяем есть ли регион в конфигурации
                if not validate_region_in_config(region, cfg):
                    logger.warning(f"⚠️ Регион '{region}' не найден в конфигурации, пропускаем")
                    continue

                workload_params = cfg["regions"][region]

                # ОТЛАДКА: Показываем исходные времена из Excel
                logger.info(f"📅 Исходные данные из Excel:")
                logger.info(f"   Старт: {row['Старт']} (тип: {type(row['Старт'])})")
                logger.info(f"   Окончание: {row['Окончание']} (тип: {type(row['Окончание'])})")

                # Получаем временное окно для даты этой строки
                win_start, win_end = calculate_time_window_for_date(row, target_date)

                logger.info(f"🕒 Временное окно (исходное):")
                logger.info(f"   win_start: {win_start} (тип: {type(win_start)})")
                logger.info(f"   win_end: {win_end} (тип: {type(win_end)})")

                # Преобразуем в datetime без изменения часового пояса
                # Время уже в МСК как в Excel файле - НЕ МЕНЯЕМ часовой пояс!
                win_start = prepare_datetime_for_report(win_start)
                win_end = prepare_datetime_for_report(win_end)

                logger.info(f"🕒 Временное окно (финальное МСК):")
                logger.info(f"   win_start: {win_start}")
                logger.info(f"   win_end: {win_end}")

                try:
                    logger.info(f"🚀 Запускаем download_report для {mass_number} {win_start.date()}")
                    xlsx_path = download_report(driver, workload_params, win_start, win_end)
                    logger.info(f"📊 Обрабатываем метрики из файла: {xlsx_path}")
                    lost, excess = calc_metrics(xlsx_path)

                    # Сохраняем результат сразу в исходный файл (в ту же строку)
                    try:
                        save_single_result_to_original_file(
                            mass_number=mass_number,
                            lost_calls=lost,
                            excess_traffic=excess,
                            original_file_path=input_xlsx_path,
                            row_index=idx
                        )
                        logger.info(f"✅ Результат сохранен в файл: {mass_number} → lost={lost}, excess={excess}")
                    except PermissionError as pe:
                        logger.error(f"❌ ОШИБКА ДОСТУПА: Файл {input_xlsx_path} открыт в Excel или заблокирован")
                        logger.error(f"   Закройте файл в Excel и попробуйте снова")
                        logger.error(f"   Детали: {pe}")
                        # Продолжаем выполнение, но не добавляем в results
                        continue
                    except Exception as save_exc:
                        logger.error(f"❌ ОШИБКА СОХРАНЕНИЯ для {mass_number}: {save_exc}")
                        logger.error(f"   Продолжаем выполнение без сохранения в файл")
                        # Продолжаем выполнение, но не добавляем в results
                        continue

                    # Создаем запись результата для возможного сохранения в CSV
                    result = create_result_record(
                        mass_number,
                        win_start.date().isoformat(),
                        lost,
                        excess
                    )
                    results.append(result)

                    logger.info(f"✅ Успешно обработан {mass_number} - {region}: lost={lost}, excess={excess}")
                except Exception as exc:
                    logger.error(f"❌ ОШИБКА для строки #{idx} MassID {mass_number} {region}")
                    try:
                        logger.error(f"   Период: {win_start.date()} - {win_end.date()}")
                    except:
                        logger.error(f"   Период: не удалось определить")
                    logger.error(f"   Детали ошибки: {exc}")
                    logger.exception("   Полный traceback:")
                    continue

            logger.info(f"🎉 Обработка завершена! Обработано {len(results)} проблем")
            logger.info(f"💾 Результаты сохранены в исходный файл: {input_xlsx_path}")

        else:
            # Стандартный режим: обработка всех проблем
            logger.info("📋 Используется стандартный режим обработки всех проблем")

            # Обрабатываем каждую строку
            for idx, row in df.iterrows():
                region = row["Регион"]
                logger.info(f"🔄 Обрабатываем строку #{idx}: {row['Номер массовой']} - {region}")

                # Проверяем есть ли регион в конфигурации
                if not validate_region_in_config(region, cfg):
                    continue

                workload_params = cfg["regions"][region]

                # Разбиваем на дневные окна
                time_windows = list(windows_for_row(row))
                logger.info(f"📊 Создано временных окон: {len(time_windows)}")

                for window_idx, (win_start, win_end) in enumerate(time_windows):
                    logger.info(f"🔸 Обрабатываем окно #{window_idx + 1}/{len(time_windows)}")
                    logger.info(f"🕒 Временное окно (исходное):")
                    logger.info(f"   win_start: {win_start} (тип: {type(win_start)})")
                    logger.info(f"   win_end: {win_end} (тип: {type(win_end)})")

                    # Преобразуем в datetime без изменения часового пояса
                    win_start = prepare_datetime_for_report(win_start)
                    win_end = prepare_datetime_for_report(win_end)

                    logger.info(f"🕒 Временное окно (финальное МСК):")
                    logger.info(f"   win_start: {win_start}")
                    logger.info(f"   win_end: {win_end}")

                    try:
                        logger.info(f"🚀 Запускаем download_report для {row['Номер массовой']} {win_start.date()}")
                        xlsx_path = download_report(driver, workload_params, win_start, win_end)
                        logger.info(f"📊 Обрабатываем метрики из файла: {xlsx_path}")
                        lost, excess = calc_metrics(xlsx_path)

                        # Создаем запись результата
                        result = create_result_record(
                            row["Номер массовой"],
                            win_start.date().isoformat(),
                            lost,
                            excess
                        )
                        results.append(result)

                        logger.info(f"✅ Успешно обработан {row['Номер массовой']} - {region}: lost={lost}, excess={excess}")
                    except Exception as exc:
                        logger.error(f"❌ ОШИБКА для строки #{idx} MassID {row['Номер массовой']} {region}")
                        try:
                            logger.error(f"   Период: {win_start.date()} - {win_end.date()}")
                        except:
                            logger.error(f"   Период: не удалось определить")
                        logger.error(f"   Детали ошибки: {exc}")
                        logger.exception("   Полный traceback:")
                        continue

            # Сохраняем в CSV файл (стандартный режим)
            save_results_to_csv(results, out_csv_path)

    finally:
        # Закрываем браузер
        driver.quit()


if __name__ == "__main__":
    main()