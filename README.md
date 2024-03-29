<div id="header" align="center">
  <img src="https://media.giphy.com/media/FdHzfvQyyIzBaXi7lM/giphy.gif" width="100" align="left"/>
</div>

# My_net 

---

## Стек технологий

[![Python](https://img.shields.io/badge/-Python-464646?style=flat-square&logo=Python)](https://www.python.org/)
[![Django](https://img.shields.io/badge/-Django-464646?style=flat-square&logo=Django)](https://www.djangoproject.com/)

## Описание проекта

Социальная сеть, предоставляющая пользователям возможность создать учетную запись, публиковать записи, подписываться на любимых авторов и отмечать понравившиеся записи.

## Установка проекта локально

* Склонировать репозиторий на локальную машину:
```bash
git clone https://github.com/Kinin812/My_net.git
```

* Cоздать и активировать виртуальное окружение:

```bash
python -m venv env
```

```bash
source env/bin/activate
```

* Перейти в директирию и установить зависимости из файла requirements.txt:

```bash
cd my_net/
pip install -r requirements.txt
```

* Выполните миграции:

```bash
python manage.py migrate
```

* Запустите сервер:
```bash
python manage.py runserver
```

* Запущенный проект доступен по адресу: [http://localhost:8000](http://localhost:8000)
