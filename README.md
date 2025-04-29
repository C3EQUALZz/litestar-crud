# Общие сведения

<b>«litestar-crud»</b> представляет из себя пример реализации тестового задания для ИП по имени: <b>«Жушма Артём»</b>.

## Задание

### Описание

Необходимо разработать `REST API` для управления пользователями. 

### Цель

Создать `REST API` на базе `LiteStar (Python 3.12)` c `CRUD`-операциями для таблицы `user` в `PostgreSQL`. 

### Требования

> - `Swagger`
> - Создание пользователя
> - Получение списка пользователей
> - Получение данных одного пользователя
> - Обновление данных пользователя
> - Удаление пользователя 

### Стек технологий

> - `Backend`: `LiteStar` (версия 2.x)
> - `PostgreSQL` + `Advanced-SQLAlchemy`
> - `Docker`
> - `Poetry` (1.8.3)

## Принцип реализации

> [!IMPORTANT]
> Автор не полностью соблюдает все требования стека по той причине, что предложенные технологии являются батарейками, для которых невозможно нормально написать абстракцию!
> `Пожалуйста, не поленитесь почитать ниже принцип организации, чтобы понять почему мой выбар пал на другие чуть технологии`.
> Автор в предложенном тестовом задании добавил интеграцию со сторонними вещами, чтобы лучше обосновать свой выбор технологий! 

В проекте используется архитектурный подход [`DDD`](https://en.wikipedia.org/wiki/Domain-driven_design) и [`EDD`](https://en.wikipedia.org/wiki/Event-driven_programming).
За счет чего данное приложение можно с легкостью интегрировать с [`FastAPI`](https://fastapi.tiangolo.com/), [`Flask`](https://flask.palletsprojects.com/en/stable/), так как логика кода построена на ванильном [`Python 3.12`](https://www.python.org/doc/).

# Зависимости

В проекте используются следующие зависимости: 
- [`poetry`](https://python-poetry.org/)
- [`pytest`](https://docs.pytest.org/en/stable/)
- [`mypy`](https://www.mypy-lang.org/)
- [`ruff`](https://docs.astral.sh/ruff/linter/)
- [`dishka`](https://dishka.readthedocs.io/en/stable/)
- [`sqlalchemy`](https://www.sqlalchemy.org/)
- [`pre-commit`](https://pre-commit.com/)
- [`faststream + kafka`](https://faststream.airt.ai/latest/)
- [`pydantic`](https://docs.pydantic.dev/latest/)
- [`pydantic-settings`](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [`alembic`](https://alembic.sqlalchemy.org/en/latest/)
  
> [!IMPORTANT]
> Все зависимости можно найти в [`pyproject.toml`](pyproject.toml)

# Структура проекта

Сама логика приложения находится в `app`. Внутри данной директории есть 5 модулей.

- [`application`](app/application)
- [`domain`](app/domain)
- [`infrastructure`](app/infrastructure)
- [`logic`](app/logic)
- [`settings`](app/settings)

Рассмотрим каждый модуль по отдельности зачем он нужен за что отвечает. 

## Что такое `domain`? 

В основе `DDD` - Домен (Domain). Это модель предмета и его задач, под которые строится приложение. Счет, который оплачиваем, Сообщение, которое отправляем, или Пользователь, которому выставляем оценку. Домены строятся на сущностях из реального мира и ложатся в центр приложения. 

> [!NOTE]
> Например, по заданию у нас система управления пользователями, где нужно оперировать людьми, поэтому `domain` - это человек. 
> Если добавится логика работы с группами людей, то появится новый `domain` - `group` и т.п. 

### Что там находится внутри директории `domain`?

Там Вы найдете 2 директории, которые Вас должны заинтересовать `entities` и `values`. 

- [`entities`](https://blog.jannikwempe.com/domain-driven-design-entities-value-objects) - это и есть наши домены, про которые я говорил выше. Пример домена можете увидеть [здесь](app/domain/entities/user.py)
- [`values`](https://blog.jannikwempe.com/domain-driven-design-entities-value-objects) - здесь находятся, так называемые, `value objects`. Грубо говоря, это характеристики нашего домена, т.е поля (атрибуты) `domain`. Почему делается так? Все очень просто: для валидации данных. Пример value objects для книги [здесь](app/domain/values/user.py)

> [!NOTE]
> Если Вы хотите добавить новый `domain`, то создайте `Python` файл, который описывает его. Например, `group.py`. Ваш класс должен наследоваться от [`BaseEntity`](app/domain/entities/base.py). Пример прилагаю ниже: 

```python
@dataclass(eq=False)
class Group:
  """
  Domain which associated with the real human
  """
  name: GroupName
  description: str
  users: list[UserEntity] = field(default_factory=list)
```

> [!NOTE]
> Если Вы хотите добавить новый `value object`, то создайте `Python` файл, который будет иметь имя домена, чтобы обозначить принадлежность `value object` к `domain entity`.
> Например, `group.py`. Ваш класс должен наследоваться от [`BaseValueObject`](app/domain/values/base.py). Пример прилагаю ниже:

```python
@dataclass(frozen=True)
class GroupName(BaseValueObject[str]):
    """
    Value object which associated with the book name
    """
    value: str

    @override
    def validate(self) -> None:
        if not self.value:
            raise EmptyTextException()

        if len(self.value) > 15:
            raise ValueTooLongException(self.value)

    @override
    def as_generic_type(self) -> str:
        return self.value
```

## Что такое `application`?

Здесь обычно содержится `api` для работы с приложением. Различные [backend endpoints](https://dev.to/apidna/api-endpoints-a-beginners-guide-ief), [sockets](https://ru.wikipedia.org/wiki/%D0%A1%D0%BE%D0%BA%D0%B5%D1%82_(%D0%BF%D1%80%D0%BE%D0%B3%D1%80%D0%B0%D0%BC%D0%BC%D0%BD%D1%8B%D0%B9_%D0%B8%D0%BD%D1%82%D0%B5%D1%80%D1%84%D0%B5%D0%B9%D1%81)) и т.п. 
Каждая директория в `api` - это handlers для сущности (домен), с которой мы работаем.

> [!NOTE]
> Например, по заданию у нас система для работы с пользователями, где нужно оперировать людьми, поэтому директория называется `users`. 
> Если бы нужно было добавить функционал для работы с группами, то в `application/api` появилась бы директория `groups`.

### Что за файлы в `application/api/{domain}`?

- `handlers.py` - здесь находится та часть, которая выступает "мордой" нашего приложения. В данном случае здесь находятся `Controller` от `LiteStar`. 
- `schemas.py` - здесь находятся схемы валидации данных `Pydantic`.

## Что такое `infrastrucutre`?

На данном слое архитектуры реализована логика работы с данными посредством следующих паттернов:
 
- [`Unit Of Work`](https://qna.habr.com/q/574561)
- [`Repository`](https://www.cosmicpython.com/book/chapter_02_repository.html), 
- [`Service`](https://lyz-code.github.io/blue-book/architecture/service_layer_pattern/)
- [`Message Bus`](https://dev.to/billy_de_cartel/a-beginners-guide-to-understanding-message-bus-architecture-22ec)
- [`Dependecy Injection`](https://thinhdanggroup.github.io/python-dependency-injection/)

### Что там находится внутри директории `infrastrucutre`?

Здесь вы найдете директории и `Python` файлы для описания работ. Каждая директория также называется, как и паттерн, которые я указал выше. Давайте рассмотрим каждый из них по отдельности.  

#### `Repository`

Здесь реализована логика работы с базой данных на уровне объектов. Репозиторий управляет коллекцией доменов (моделей).
В случае данного тестового задания написана одна имплементация для работы с [людьми](app/infrastructure/repositories/users/alchemy.py).

Как можно написать свой репозиторий? Все очень просто: Вам нужно унаследоваться от интерфейса, который описывает ваш домен.
Пример интерфейса для репозитория управления с книгами можете увидеть [здесь](app/infrastructure/repositories/books/base.py).

Например, я приведу реализацию `SQLAlchemyGroupRepository`, где используется библиотека [`SQLAlchemy`](https://www.sqlalchemy.org/).
Создайте файл `alchemy.py`, вписав код, который ниже. 

```python
class SQLAlchemyGroupsRepository(SQLAlchemyAbstractRepository[GroupEntity], BooksRepository):

    def get(self, oid: str) -> Optional[GroupEntity]:
        result: Result = self._session.execute(select(GroupEntity).filter_by(id=id))
        return result.scalar_one_or_none()

    def get_by_title(self, group_name: str) -> Optional[GroupEntity]:
        result: Result = self._session.execute(select(GroupEntity).filter_by(name=group_name))
        return result.scalar_one_or_none()

    def add(self, model: GroupEntity) -> GroupEntity:
        result: Result = self._session.execute(
            insert(GroupEntity).values(**await model.to_dict(exclude={'oid'}, save_value_objects=True)).returning(GroupEntity)
        )

        return result.scalar_one()
```

> [!IMPORTANT]
> `oid` - это `object id`, выбрано было название с той целью, чтобы не конфликтовать с именем встроенной функции `id`

> [!IMPORTANT]
> Исходя из вышесказанного, автор отказался от `advanced sqlalchemy` по той причине, что там используются `generic repositories`, которые сами объявляют свои методы.
> Если использовать `advanced sqlalchemy`, то не получится ввести банальный интерфейс, который можно имплементировать в классе.
> Если вы настоятельно хотите использовать `advanced alchemy` то будет тяжело потом перейти на другую библиотеку или на `NoSQL` из-за таких особенностей.
> Автор отказался её в угоду чистоты архитектуры и масштабируемости. 

#### `Unit Of Work`

Название паттерна `Unit of Work` намекает на его задачу управлять атомарностью операций. 
В моем случае относительного тестового у меня есть [`SQLAlchemyAbstractUnitOfWork`](app/infrastructure/uow/base), который описывает логику работы `Unit Of Work`.

> [!IMPORTANT]
> `advanced sqlalchemy` позволяет управлять транзакциями, но из-за `generic repository` автор отказался от данной технологии.

Приведу пример того, как написать свой `Unit of Work` для групп, используя [`SQLAlchemy`](https://www.sqlalchemy.org/). 

```python
class SQLAlchemyAbstractUnitOfWork(AbstractUnitOfWork):
    """
    Unit of work interface for SQLAlchemy, from which should be inherited all other units of work,
    which would be based on SQLAlchemy logics.
    """

    def __init__(self, session_factory: sessionmaker = default_session_factory) -> None:
        super().__init__()
        self._session_factory: sessionmaker = session_factory

    def __enter__(self) -> Self:
        self._session: Session = self._session_factory()
        return super().__aenter__()

    def __exit__(self, *args, **kwargs) -> None:
        super().__exit__(*args, **kwargs)
        self._session.close()

    def commit(self) -> None:
        self._session.commit()

    def rollback(self) -> None:
        self._session.expunge_all()
        self._session.rollback()


class SQLAlchemyGroupsUnitOfWork(SQLAlchemyAbstractUnitOfWork, BooksUnitOfWork):

    def __enter__(self) -> Self:
        uow = super().__enter__()
        self.groups: GroupsRepository = SQLAlchemyGroupsRepository(session=self._session)
        return uow
```

### `Service`

Здесь агрегируется логика `UoW` и `Repository`. Именно из-под данного слоя идет работа с данными уже для обращения в командах.
Сервисы всегда пишутся на ванильном Python, они ничего не должны знать про то какой `ORM` используется и т.п.
В `advanced sqlalchemy` есть свои `Service`, но в таком случае появляется явная зависимость от данной библиотеки.   

> [!NOTE]
> Из-за того, что используется `CQRS` вся бизнес логика может не концентрироваться здесь. 

Приведу пример того, как написать новый сервис, если появилась сущность (домен) `GroupEntity`

```python
class GroupService:
    """
    Service layer core according to DDD, which using a unit of work, will perform operations on the domain model.
    """

    def __init__(self, uow: GroupUnitOfWork) -> None:
        self._uow = uow

    def add(self, group: GroupEntity) -> GroupEntity:
        with self._uow as uow:
            new_group: GroupEntity = uow.groups.add(model=group)
            uow.commit()
            return new_group

    def check_existence(self, oid: Optional[str] = None, name: Optional[str] = None) -> bool:
        if not (oid or name):
            raise AttributeException("Please provide oid or name for this method")

        with self._uow as uow:
            if oid and uow.groups.get(oid):
                return True

            if title and uow.groups.get_by_name(name):
                return True

        return False
```

## Что такое `logic`?

Здесь на данном слое собрана вся бизнес логика, где требуется реализовать наш функционал по тз. 
В `logic` у нас есть директории `commands` и `events`, `handlers`. 

События - это побочные действия, которые выполняются после определенной команды. Например, при создании пользователя отправить ему `email` об успешной регистрации. 

### `Commands`

Команды - это действие, которое должно выполнять наше приложение. Например, создать пользователя, создать книгу, удалить книгу. Обычно это оформляется в виде `DTO` класса. Примеры вот [здесь](app/logic/commands/users.py).
Но если команды это `DTO`, то как осуществлять бизнес логику? Здесь на помощь приходят `handlers`, которые вы можете увидеть ниже. Пока приведу пример того, как написать свою команды для регистрации условного человека в нашей библиотеке. 

```python
@dataclass(frozen=True)
class CreateGroupCommand(AbstractCommand):
    name: str
```

### `CommandHandlers`

Это как раз перехватчики наши команд, которые ожидают `DTO`, написанный вами ранее. Именно здесь идет логика уже. Приведу пример того, как написать `handler` для команд. 

```python

CT = TypeVar("CT", bound=AbstractCommand)

class GroupCommandHandler(AbstractCommandHandler[CT], ABC):
    """
    Abstract command handler class, from which every users command handler should be inherited from.
    """

    def __init__(self, uow: GroupUnitOfWork) -> None:
        self._uow = uow

class CreateGroupCommandHandler(HumanCommandHandler[CreateGroupCommand]):

    def __call__(self, command: RegisterHumanCommand) -> Human:
        """
        Registers a new user, if user with provided credentials doesn't exist, and creates event signaling that
        operation was successfully executed.
        """

        group_service: GroupService = GroupService(uow=self._uow)
        if group_service.check_existence(name=command.username):
            raise GroupAlreadyExistsError()

        new_group: GroupEntity = GroupEntity(name=GroupName(command.name))

        return group_service.add(group=new_group)
```

Но встает вопрос. Как это все связать, чтобы все заработало? Вам нужно добавить вот [здесь](app/logic/handlers/container.py) в словарике команду и её перехватчик.
Например, чтобы добавить команду и наш хендлер, нужно в конце добавить значение `CreateGroupCommand: CreateGroupCommandHandler`. В результате у Вас должен получится вот такой словарик. 

```python
@provide(scope=Scope.APP)
    async def get_mapping_and_command_handlers(self) -> CommandHandlerMapping:
        """
        Here you have to link commands and command handlers for future inject in Bootstrap
        """
        return cast(
            "CommandHandlerMapping",
            {
                CreateUserCommand: CreateUserCommandHandler,
                UpdateUserCommand: UpdateUserCommandHandler,
                DeleteUserCommand: DeleteUserCommandHandler,
                CreateGroupCommand: CreateGroupCommandHandler
            },
        )
``` 

## Что такое `settings`?

Здесь находятся параметры подключения к БД обычно, настройки логгирования и т.п.
В рамках тестового задания настройка логгирования и класс Settings.

Приведу пример ниже, как обычно оформляют класс `Settings` для backend приложений с использованием `pydantic` и `pydantic-settings`. 

```python
class MongoSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="MONGO_DB",
        extra="ignore"
    )

    url: MongoDsn = Field(alias="MONGO_DB_URL")
    chat_database: str = Field(default="chat", alias="MONGO_DB_CHAT_DATABASE")
    chat_collection: str = Field(default="chat", alias="MONGO_DB_CHAT_COLLECTION")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        extra="ignore"
    )

    database: MongoSettings = MongoSettings()
```

# Как можно улучшить проект? 

Для контроля управления транзакциями между микросервисами (в будущем) `SAGA` паттерн

# Установка проекта и запуск

## Запуск c `Docker`

Предполагается, что в Вашей системе уже установлены `git`, `Docker`.

Создайте в корне проекта файл `.env`, скопировав значения [`отсюда`](.env.example). 

```bash
git clone https://github.com/C3EQUALZz/library-console-app.git
docker compose up --build
```

Точка запуска приложения находится [`здесь`](app/main.py). 

## `Swagger`

![изображение](https://github.com/user-attachments/assets/59c3aeb6-ca49-4070-a1cc-34f8175d3af2)



