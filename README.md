# Домашнее задание по КПО 3
### Мультиагентная система управления рестораном
### В двух подходах смотрите на ответвление **main2**
### Разработчики
- **Шарапов Егор БПИ219** [(@Kratosterra)](https://github.com/Kratosterra)
- **Артемов Никита БПИ219** [(@nktrtmv)](https://github.com/nktrtmv)

### Запуск
> [Документация osBrain](https://osbrain.readthedocs.io/en/stable/introduction.html#installation) 

$ docker build . -t mas_app

$ docker run -p 4000:80 mas_app

> Ну или можно запустить сам [**main.py**](./src/main.py) и при этом установить 'osbrain'

- Входные данные задаются в [**data**](./src/data)
- Выходные данные выводятся в [**log**](./src/log) и информация о работе других агентов в консоль.
### Архитектура
Приложение построено на мультиагентной архитектуре с поддержкой входных и выходных данных в формате **.json**
