"""
Модуль для очистки скачанных файлов после завершения работы скрипта.
"""

import os
import time
from pathlib import Path
from loguru import logger


def cleanup_downloaded_files(download_dir: Path = None) -> None:
    """
    Удаляет все скачанные файлы из папки загрузок.

    Args:
        download_dir: Путь к папке загрузок. Если не указан, используется папка downloads в корне проекта
    """
    if download_dir is None:
        # Используем папку downloads в корне проекта
        project_root = Path(__file__).resolve().parent.parent
        download_dir = project_root / "downloads"

    if not download_dir.exists():
        logger.info(f"📁 Папка загрузок не существует: {download_dir}")
        return

    logger.info(f"🧹 Начинаем очистку папки загрузок: {download_dir}")

    try:
        # Получаем список всех файлов в папке
        all_files = list(download_dir.glob("*"))

        if not all_files:
            logger.info("✅ Папка загрузок уже пуста")
            return

        # Подсчитываем файлы по типам
        file_types = {}
        total_size = 0

        for file_path in all_files:
            if file_path.is_file():
                file_type = file_path.suffix.lower() or "без расширения"
                file_size = file_path.stat().st_size

                if file_type not in file_types:
                    file_types[file_type] = {"count": 0, "size": 0}

                file_types[file_type]["count"] += 1
                file_types[file_type]["size"] += file_size
                total_size += file_size

        # Логируем статистику
        logger.info(f"📊 Найдено файлов для удаления:")
        for file_type, stats in file_types.items():
            size_mb = stats["size"] / (1024 * 1024)
            logger.info(f"   {file_type}: {stats['count']} файлов ({size_mb:.2f} MB)")

        total_mb = total_size / (1024 * 1024)
        logger.info(f"📊 Общий размер: {total_mb:.2f} MB")

        # Удаляем файлы
        deleted_count = 0
        failed_count = 0

        for file_path in all_files:
            try:
                if file_path.is_file():
                    file_path.unlink()  # Удаляем файл
                    deleted_count += 1
                    logger.debug(f"🗑️ Удален файл: {file_path.name}")
                elif file_path.is_dir():
                    # Удаляем папки рекурсивно
                    import shutil
                    shutil.rmtree(file_path)
                    deleted_count += 1
                    logger.debug(f"🗑️ Удалена папка: {file_path.name}")
            except Exception as e:
                failed_count += 1
                logger.warning(f"⚠️ Не удалось удалить {file_path.name}: {e}")

        # Логируем результат
        if failed_count == 0:
            logger.info(f"✅ Очистка завершена успешно: удалено {deleted_count} файлов/папок")
        else:
            logger.warning(f"⚠️ Очистка завершена с ошибками: удалено {deleted_count}, не удалено {failed_count}")

        # Проверяем что папка действительно пуста
        remaining_files = list(download_dir.glob("*"))
        if remaining_files:
            logger.warning(f"⚠️ В папке остались файлы: {[f.name for f in remaining_files]}")
        else:
            logger.info("✅ Папка загрузок полностью очищена")

    except Exception as e:
        logger.error(f"❌ Ошибка при очистке папки загрузок: {e}")
        logger.exception("Полный traceback:")


def cleanup_old_files(download_dir: Path = None, max_age_hours: int = 24) -> None:
    """
    Удаляет старые файлы из папки загрузок (старше указанного возраста).

    Args:
        download_dir: Путь к папке загрузок
        max_age_hours: Максимальный возраст файлов в часах
    """
    if download_dir is None:
        project_root = Path(__file__).resolve().parent.parent
        download_dir = project_root / "downloads"

    if not download_dir.exists():
        return

    current_time = time.time()
    max_age_seconds = max_age_hours * 3600

    logger.info(f"🧹 Очистка старых файлов (старше {max_age_hours} часов) в папке: {download_dir}")

    old_files = []
    for file_path in download_dir.glob("*"):
        if file_path.is_file():
            file_age = current_time - file_path.stat().st_mtime
            if file_age > max_age_seconds:
                old_files.append(file_path)

    if not old_files:
        logger.info("✅ Старых файлов не найдено")
        return

    logger.info(f"📊 Найдено {len(old_files)} старых файлов для удаления")

    deleted_count = 0
    for file_path in old_files:
        try:
            file_path.unlink()
            deleted_count += 1
            logger.debug(f"🗑️ Удален старый файл: {file_path.name}")
        except Exception as e:
            logger.warning(f"⚠️ Не удалось удалить старый файл {file_path.name}: {e}")

    logger.info(f"✅ Удалено {deleted_count} старых файлов")
