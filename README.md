# ![InDreams FastAPI App](logo.png)

## Настройка и запуск

Есть два пути: _uv-way_ и _old-way_. Если есть проблемы с установкой библиотек, выбирайте _old-way_. Если у вас есть проблемы с `uv` - также выбирайте _old-way_. Иначе - выбирайте _uv-way_.

### uv-way

#### Установка `uv`

```powershell
# windows

powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

```sh
# unix

curl -LsSf https://astral.sh/uv/install.sh | sh
```

Перезапустите терминал (либо редактор кода), проверьте работоспособность

```sh
# windows / unix

uv
```

Если `uv` откликнулся, продолжайте двигаться по пути. Иначе переходите на _old-way_.

#### Виртуальное окружение и зависимости

Удалите директорию `venv`, выполните следующие команды

```sh
# windows / unix

uv sync # установка зависимостей
uv venv # активация виртуального окружения
```

#### Переменные окружения

Переменные окружения служат для задания конфигураций и чувствительных данных. В этом проекте к ним относятся путь к файловой базе данных, соли для хеширования и шифрования, а также флаг для режима отладки. Чтобы разработчик знал, какие именно поля ему нужно заполнить, обычно в репозитории находится файл с примером, здесь это `.env.example`.

Скопируйте его содержимое в файлы `.env.local` и `.env.testing` следующими командами

```powershell
# windows

copy .env.example .env.local # создание файла для окружения разработки
copy .env.example .env.testing # создание файла для окружения тестирования
```

```sh
# unix

cp .env.example .env.local # создание файла для окружения разработки
cp .env.example .env.testing # создание файла для окружения тестирования
```

Теперь внесите в созданные файлы настройки для `DATABASE_URI`, `JWT_SECRET_KEY`, `PASSWORD_SALT`, `DEBUG`.

Рекомендации:

- используйте разные `DATABASE_URI` для окружений разработки и тестирования;
- `JWT_SECRET_KEY` и `PASSWORD_SALT` генерируйте командой, указанной в `.env.example` (под `windows` она будет работать через `git bash`);
- флаг `DEBUG` установите в `true` для окружения разработки, в `false` для окружения тестирования.

#### Инициализация базы данных и наполнение данными

```sh
# windows / unix
uv run python -m app.database.seed
```

#### Запуск сервера

```sh
# windows / unix
uv run uvicorn app.main:app --reload
```

Добро пожаловать в документацию по ссылке <http://localhost:8000/docs>!

### old-way

#### Виртуальное окружение и зависимости

**Создайте виртуальное окружение** (если редактор кода не создал его автоматически).

```powershell
# windows

python -m venv .venv
```

```sh
# unix

python3 -m venv .venv
```

**Активируйте его**

```powershell
# windows

.venv\Scripts\activate
```

```sh
# unix

source .venv\bin\activate
```

**Установите зависимости**

```powershell
# windows

(.venv) pip install -r requirements.txt
```

```sh
# unix

(.venv) python3-pip install -r requirements.txt
```

Если наблюдаются проблемы со скачиванием библиотек и вы не знаете / не можете их обойти, скопируйте содержимое директории `site-packages` в `.venv\Lib\site-packages` на Windows либо `.venv\lib\...\site-packages` на Unix.

#### Переменные окружения

Переменные окружения служат для задания конфигураций и чувствительных данных. В этом проекте к ним относятся соли для хеширования и шифрования. Чтобы разработчик знал, какие именно поля ему нужно заполнить, обычно в репозитории находится файл с примером, здесь это `.env.example`.

Скопируйте его содержимое в файл `.env` следующей командой

```powershell
# windows

(.venv) copy .env.example .env
```

```sh
# unix

(.venv) cp .env.example .env
```

Теперь внесите в созданные файлы настройки для `JWT_SECRET_KEY` и `PASSWORD_SALT`. Генерируйте их командой, указанной в `.env.example` (под `windows` она будет работать через `git bash`).

#### Инициализация базы данных и наполнение данными

```sh
# windows
(.venv) python -m app.database.seed

# unix
(.venv) python3 -m app.database.seed
```

#### Запуск сервера

```sh
# windows / unix
(.venv) fastapi dev
```

Если сервер не запустился, попробуйте альтернативную команду

```powershell
# windows
(.venv) py -m fastapi dev
```

```sh
# unix
(.venv) python3 -m fastapi dev
```

Добро пожаловать в документацию по ссылке <http://localhost:8000/docs>!

## Тестирование

### API-тесты с Newman

```sh
# windows / unix

npx newman run postman_collection.json --global-var "API_URL=http://127.0.0.1:8000" --global-var="USERNAME=john.doe" --global-var="PASSWORD=password"
```

### Автотесты с Pytest

```sh
# uv-way
pytest

# old-way
uv run pytest
```

## Форматирование

```sh
# uv-way
uv run ruff format app

# old-way
ruff format app
```

## Линтинг

### Рафф-линтинг

```sh
# uv-way
uv run ruff check app

# old-way
ruff check app
```

### Статический анализ

```sh
# uv-way
uv run mypy app

# old-way
mypy app
```
