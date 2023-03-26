# Домашнее задание по КПО 3
### Мультиагентная система управления рестораном

### Разработчики
- **Шарапов Егор БПИ219** [(@Kratosterra)](https://github.com/Kratosterra)
- **Артемов Никита БПИ219** [(@nktrtmv)](https://github.com/nktrtmv)

### Запуск
> [Документация osBrain](https://osbrain.readthedocs.io/en/stable/introduction.html#installation) 

$ docker build . -t mas_app

$ docker run -p 4000:80 mas_app

### Архитектура
Приложение построено на мультиагентной архитектуре с поддержкой входных и выходных данных в формате **.json**
