# YandexSnoop

Этот проект позволяет автоматически загружать файлы, отправленные Telegram-боту, на ваше хранилище Yandex.Disk, очищать корзину и искать файлы по запросу пользователя. Функционал постепенно расширяется.

## Требования

- Python 3.8+
- git
- Docker (опционально, для запуска в контейнере)
- Docker Compose (опционально, для запуска в контейнере)

## Установка и настройка

1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/noreox/YandexSnoop.git
   cd YandexSnoop
   ```

2. Создайте и активируйте виртуальное окружение:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Для Linux/macOS
   # или
   venv\Scripts\activate  # Для Windows
   ```

3. Установите зависимости:
   ```bash
   chmod +x scripts/install_req.sh
   ./scripts/install_req.sh
   ```

4. Создайте Telegram-бота:
   - Откройте Telegram и найдите @BotFather.
   - Следуйте инструкциям для создания нового бота и получите API-токен.

5. Создайте приложение на Yandex:
   - Перейдите на [Yandex OAuth](https://oauth.yandex.ru/).
   - Создайте новое приложение, выберите "Веб-сервисы".
   - В качестве "Redirect URL" укажите: `https://oauth.yandex.ru/verification_code`.
   - Предоставьте приложению следующие права:
     - Чтение событий аудит лога Диска: `ya360_security:audit_log_disk`
     - Доступ к папке приложения на Диске: `cloud_api:disk.app_folder`
     - Чтение всего Диска: `cloud_api:disk.read`
     - Запись в любом месте на Диске: `cloud_api:disk.write`
     - Доступ к информации о Диске: `cloud_api:disk.info`
     - Доступ к Яндекс.Диску для приложений: `yadisk:disk`

   - Получите токен, перейдя по ссылке:
     `https://oauth.yandex.ru/authorize?response_type=token&client_id=ВАШ_CLIENTID`

6. Настройте переменные окружения:
   - Скопируйте файл `.env.example` в `.env`:
     ```bash
     cp .env.example .env
     ```
   - Отредактируйте файл `.env`, вставив полученные ранее токены:
     ```
     TELEGRAM_API_BOT_TOKEN=your_bot_token_here
     YANDEX_OAUTH_API_APP_ID=your_yandex_oauth_app_id_here
     ```
   - Сохраните файл для следующего шага.

7. Получите Chat ID:
   - Отправьте сообщение вашему боту в Telegram.
   - Запустите скрипт:
     ```bash
     chmod +x scripts/get_chatid.sh
     ./scripts/get_chatid.sh
     ```
   - Добавьте полученный `chat_id` в файл `.env`.

8. Запустите бота:
   ```bash
   chmod +x scripts/start_bot.sh
   ./scripts/start_bot.sh
   ```

Теперь ваш бот готов к работе.

## Использование Docker (опционально)

Если вы предпочитаете использовать Docker:

1. Убедитесь, что Docker и Docker Compose установлены на вашей системе.

2. Соберите и запустите контейнер:
   ```bash
   # Выполните, находясь в корне проекта
   docker-compose -f docker/docker-compose.yml up -d
   ```

3. Для остановки бота используйте:
   ```bash
   # Выполните, находясь в корне проекта
   docker-compose -f docker/docker-compose.yml down
   ```

## Лицензия

© 2024 noreox

Этот проект лицензирован под Apache License, Version 2.0. Подробности см. в файле LICENSE.
