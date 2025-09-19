# Автоматическое определение Python

## Проблема

У некоторых сотрудников Python установлен в нестандартные места (например, `C:\py\` вместо `C:\Program Files\Python313\`), что приводит к ошибке 103 при запуске скрипта через виртуальное окружение.

## Решение

Батник `run.bat` теперь автоматически:

1. **Находит Python** в различных местах установки
2. **Проверяет корректность** существующего venv
3. **Автоматически исправляет** пути в существующем venv
4. **Сохраняет все установленные библиотеки** при исправлении

## Алгоритм поиска Python

### 1. Поиск в PATH
- Проверяет доступность команды `python` в системном PATH
- Использует `where python` для определения полного пути

### 2. Проверка стандартных мест установки
- `C:\py\python.exe` (ваш случай)
- `C:\Python39\python.exe`
- `C:\Python310\python.exe`
- `C:\Python311\python.exe`
- `C:\Python312\python.exe`
- `C:\Python313\python.exe`
- `C:\Program Files\Python39\python.exe`
- `C:\Program Files\Python310\python.exe`
- `C:\Program Files\Python311\python.exe`
- `C:\Program Files\Python312\python.exe`
- `C:\Program Files\Python313\python.exe`
- `C:\Program Files (x86)\Python39\python.exe`
- `C:\Program Files (x86)\Python310\python.exe`
- `C:\Program Files (x86)\Python311\python.exe`
- `C:\Program Files (x86)\Python312\python.exe`
- `C:\Program Files (x86)\Python313\python.exe`

### 3. Поиск в реестре Windows
- `HKEY_LOCAL_MACHINE\SOFTWARE\Python\PythonCore`
- `HKEY_CURRENT_USER\SOFTWARE\Python\PythonCore`

## Обработка ошибок

### Ошибка 103
Если при запуске возникает ошибка 103 (не найден Python по пути), батник:
1. Выводит предупреждение
2. Исправляет пути в существующем venv (обновляет pyvenv.cfg и копирует правильный python.exe)
3. Повторно запускает скрипт

### Проверка venv
Перед запуском батник проверяет:
- Доступность `python.exe` в venv
- Наличие основных пакетов (selenium, pandas, openpyxl, loguru, tqdm)

## Логи работы

Батник выводит подробную информацию:
```
[INFO] Найден Python: "C:\py\python.exe"
[INFO] venv не найден, создаем новое окружение...
[INFO] Создаем venv с Python: "C:\py\python.exe"
[INFO] Устанавливаем зависимости...
[INFO] venv создан успешно
```

При ошибке 103:
```
[WARNING] Обнаружена ошибка 103 - проблема с путем к Python
[INFO] Исправляем пути в venv...
[INFO] Обновляем pyvenv.cfg...
[INFO] Копируем правильный Python в venv...
[INFO] Обновляем pip...
[INFO] Пути в venv исправлены успешно
[INFO] Повторный запуск после исправления...
```

## Преимущества

- ✅ **Автоматическое исправление** проблем с путями
- ✅ **Не требует переустановки** Python
- ✅ **Сохраняет все установленные библиотеки** при исправлении
- ✅ **Работает с любыми** местами установки Python
- ✅ **Подробное логирование** процесса
- ✅ **Обратная совместимость** со стандартными установками

## Использование

Просто запустите `run.bat` как обычно - все исправления произойдут автоматически!
