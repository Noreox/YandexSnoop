# YandexSnoop Bot

Этот мини-проект позволяет автоматически загружать файлы, отправленные в Telegram-бота, на ваш аккаунт Yandex.Disk. Файлы будут загружаться в автоматически создаваемые папки по типу 'August_2024'.

## Установка и настройка

### Шаг 1: Создание Telegram-бота

1. Откройте Telegram и найдите @BotFather.
2. Создайте по инструкции нового бота и получите API-токен вашего бота.

### Шаг 2: Создание приложения на Yandex

1. Перейдите на [Yandex OAuth](https://oauth.yandex.ru/).
2. Создайте новое приложение.
3. Выберите пункт "Веб-сервисы".
4. В качестве "Redirect URL" укажите: `https://oauth.yandex.ru/verification_code`.
5. Затем предоставьте приложению следующие разрешения для управления Yandex.Disk:
    - Доступ к папке приложения на Диске: `cloud_api:disk.app_folder`
    - Чтение всего Диска: `cloud_api:disk.read`
    - Запись в любом месте на Диске: `cloud_api:disk.write`
    - Доступ к информации о Диске: `cloud_api:disk.info`
6. Получите токен:
    - Скопируйте ClientID вашего созданного приложения и получите токен по ссылке:
      `https://oauth.yandex.ru/authorize?response_type=token&client_id=ВАШ_CLIENTID`.

### Шаг 3: Установка Python:
Для пользователей Linux данный шаг можно пропустить, т.к в большинстве современных дистрибутивов он установлен по умолчанию

Если вы пользователь Windows, то можете легко установить через [официальный сайт](https://www.python.org/downloads/)
Перед установкой обязательно поставьте 'Add Python3.1x to PATH'

### Шаг 4: Клонирование репозитория

Клонируйте этот репозиторий на вашу систему:

Для пользователей Windows:
1. Установите [Git для Windows](https://gitforwindows.org/).
2. Откройте Git Bash и выполните команды ниже:
    ```bash
    # По желанию перейдите в нужную директорию перед клонированием:
    # Пример: cd Документы
    git clone https://github.com/Noreox/YandexSnoop.git
    cd YandexSnoop
    ```

Для пользователей Linux (Ubuntu):
1. Установите необходимые пакеты:
    ```bash
    sudo apt-get install git python3.1x-venv # Где x - последняя доступная версия Python в вашей системе
    ```
2. Клонируйте репозиторий:
    ```bash
    # По желанию перейдите в нужную директорию перед клонированием:
    # Пример: cd Документы/
    git clone https://github.com/Noreox/YandexSnoop.git
    cd YandexSnoop
    ```
    
### Шаг 5: Настройка виртуального окружения

1. Создайте и активируйте виртуальное окружение:
    ```bash
    python -m venv myenv

    # В некоторых случаях переменная PATH может быть установлена по другому, в таком случае пробуйте:
    python3 -m venv venv
    ```
2. Активируйте созданное окружение:
    - На Linux:
        ```bash
        source myenv/bin/activate
        ```
    - На Windows:
        ```bash
        source myenv\Scripts\activate
        ```

### Шаг 6: Установка зависимостей

Установите необходимые зависимости, находясь в виртуальном окружении:
```bash
pip install aiogram yadisk requests
```

### Шаг 7: Настройка переменных

Откройте в вашем редакторе `YandexSnoop.py` и замените `YOUR_BOT_API_TOKEN` и `YOUR_YANDEX_DISK_TOKEN` на полученные ранее HTTP API токен у @BotFather и OAuth-токен у Yandex.

### Шаг 8: Получение Chat ID

1. Отредактируйте файл `get_chatid.py`, заменив `YOUR_BOT_API_TOKEN` на токен вашего бота Telegram.
2. Отправьте сообщение вашему боту
3. Запустите скрипт `get_chatid.py`:
    ```bash
    python get_chatid.py
    ```
4. Скопируйте полученный `chat_id` и вставьте его в `YandexSnoop.py` в переменную `chat_id`.

### Шаг 9: Запуск бота

Теперь почти всё готово, осталось запустить бота:
```bash
python YandexSnoop.py
```

Теперь ваш бот готов к работе. Отправляйте файлы боту в Telegram, и они будут автоматически загружены на ваш Yandex.Disk.
