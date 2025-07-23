# 🚀 Настройка ChromeDriver

## Автоматическая установка (рекомендуется)

Скрипт использует библиотеку `webdriver-manager`, которая **автоматически**:
1. Определяет версию вашего Chrome
2. Скачивает подходящий ChromeDriver
3. Размещает его в нужном месте
4. Настраивает путь к драйверу

**Никаких дополнительных действий не требуется!** Просто запустите скрипт.

## Ручная установка (если автоматическая не работает)

### 1. Узнайте версию Chrome
- Откройте Chrome → Меню → Справка → О браузере Google Chrome
- Запомните номер версии (например: `120.0.6099.216`)

### 2. Скачайте ChromeDriver
- Перейдите на https://chromedriver.chromium.org/downloads
- Выберите версию, соответствующую вашему Chrome
- Скачайте архив для вашей ОС (Windows/Mac/Linux)

### 3. Установка ChromeDriver

#### Вариант A: В папку проекта (рекомендуется)
```bash
# Извлеките chromedriver в папку проекта
unzip chromedriver_mac64.zip  # для Mac
# или
unzip chromedriver_win32.zip  # для Windows

# Структура проекта должна быть:
job/
  - main.py
  - chromedriver      # для Mac/Linux
  - chromedriver.exe  # для Windows
  - region_skills.yml
  - ...
```

#### Вариант B: В системный PATH
```bash
# Mac/Linux
sudo mv chromedriver /usr/local/bin/
sudo chmod +x /usr/local/bin/chromedriver

# Windows
# Поместите chromedriver.exe в любую папку
# Добавьте эту папку в переменную окружения PATH
```

### 4. Проверка установки
```bash
# Проверьте, что драйвер работает
chromedriver --version
# Должно вывести что-то вроде: ChromeDriver 120.0.6099.109

# Проверьте скрипт
python main.py --help
```

## Возможные проблемы

### Ошибка "chromedriver not found"
**Решение:**
1. Убедитесь, что Chrome установлен
2. Перезапустите скрипт (webdriver-manager попробует снова)
3. Используйте ручную установку

### Ошибка версии ChromeDriver
**Решение:**
1. Обновите Chrome до последней версии
2. Удалите кэш webdriver-manager: `~/.wdm/` (Mac/Linux) или `%USERPROFILE%\.wdm\` (Windows)
3. Перезапустите скрипт

### Проблемы с правами доступа
**Решение (Mac/Linux):**
```bash
chmod +x chromedriver
```

**Решение (Windows):**
- Запустите командную строку от имени администратора

## Альтернативные браузеры

Если Chrome недоступен, можно переписать скрипт на Firefox:
1. Установите Firefox
2. Замените в коде `ChromeDriver` на `GeckoDriver`
3. Используйте `webdriver-manager` для Firefox

Но Chrome работает стабильнее с корпоративными сайтами.