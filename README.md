# Google Translate CLI

![googletranslate_logo.png](googletranslate_logo.png)

Этот проект предоставляет простой интерфейс командной строки (CLI) для перевода текста с использованием Google Translate API. Скрипт позволяет переводить текст с автоматическим определением исходного языка или с указанием языков вручную.

## Установка

---

### Шаг 1: Клонирование репозитория

Сначала клонируйте репозиторий в директорию `~/.local/bin`:

```bash
cd ~/.local/bin
git clone https://github.com/morington/googletranslation.git
```

### Шаг 2: Создание виртуального окружения (опционально)

Если вы не хотите устанавливать зависимости в системный Python, что правильно,
создайте виртуальное окружение в директории репозитория:

```bash
cd googletranslation
python3 -m venv venv
source venv/bin/activate
```

### Шаг 3: Установка зависимостей

Установите необходимые зависимости, используя `pip`:

```bash
pip install -r requirements.txt
```

### Шаг 4: Настройка `trans.sh`

Откройте файл `trans.sh` в директории репозитория и убедитесь, 
что путь к интерпретатору Python указан правильно. Если вы 
используете виртуальное окружение, путь будет выглядеть так:

```bash
#!/bin/bash
~/.local/bin/googletranslation/venv/bin/python ~/.local/bin/googletranslation/trans.py "$@"
```

Если вы используете системный Python, измените путь на:

```bash
#!/bin/bash
/usr/bin/python3 ~/.local/bin/googletranslation/trans.py "$@"
```

### Шаг 5: Создание символической ссылки

Создайте символическую ссылку на `trans.sh` в директории `~/.local/bin`:

```bash
ln -s ~/.local/bin/googletranslation/trans.sh ~/.local/bin/trans
```

### Шаг 6: Добавление пути в переменную окружения

Добавьте директорию `~/.local/bin` в переменную окружения `PATH`.
Откройте файл `~/.bashrc` или `~/.zshrc` и добавьте следующую строку в самый конец файла:

```bash
export PATH=$PATH:~/.local/bin
```

Затем обновите конфигурацию командной строки:

```bash
source ~/.bashrc  # или source ~/.zshrc
```

## Использование

---
Теперь вы можете использовать команду `trans` для перевода текста из командной строки.

**Примеры использования:**

```bash
# Перевод текста с автоматическим определением исходного языка на русский
trans -t "Hello, world!" -a

# Перевод текста с английского на русский
trans -t "Hello, world!" -sl en

# Перевод текста с русского на английский
trans -t "Привет, мир!" -sl ru -tl en

# Справка --help
# Параметры
#   -t, --text: Текст для перевода [обязательный параметр].
#   -a, --auto: Автоматически определить исходный язык.
#   -sl, --source-language: Исходный язык [по умолчанию: en].
#   -tl, --target-language: Целевой язык [по умолчанию: ru].
```

## Лицензия

---
**Этот проект распространяется под лицензией MIT. Подробности смотрите в файле [LICENSE](LICENSE).**

## Авторы

---
<a href="https://github.com/morington/googletranslate/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=morington/googletranslate"/>
</a>

## Благодарности

---
**Спасибо [Google](https://google.com) за предоставление API для перевода текста.**