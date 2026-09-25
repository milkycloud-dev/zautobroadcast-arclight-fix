<p align="center"><img src="assets/icon.png" width="128" height="128" alt="ZAutoBroadcast Arclight Fix icon"></p>

<h1 align="center">ZAutoBroadcast Arclight Fix</h1>

<p align="center">Unofficial patch kit that makes ZAutoBroadcast 1.3 work on Spigot and on NeoForge and Bukkit hybrids such as Arclight, which do not ship the Paper Adventure API. Tested on Arclight NeoForge 1.21.1.</p>

<p align="center"><a href="https://github.com/milkycloud-dev/zautobroadcast-arclight-fix/actions/workflows/release.yml"><img src="https://github.com/milkycloud-dev/zautobroadcast-arclight-fix/actions/workflows/release.yml/badge.svg" alt="Release"></a></p>

<p align="center"><a href="#english">English</a> | <a href="#русский">Русский</a></p>

<a id="english"></a>

## English

### Problems fixed

| Error on Spigot or Arclight | Cause | Fix |
|---|---|---|
| `NoClassDefFoundError: net/kyori/adventure/text/minimessage/MiniMessage` every broadcast | the plugin expects Adventure from Paper; `plugin.yml` has no `libraries:` | `plugin.yml` lists Adventure 4.17.0, examination and annotations, so the Bukkit library loader downloads them |
| `NoSuchMethodError: Player.sendMessage(Component)` | Paper-only method | ASM patch of `ZAutoBroadcast.class`: the three call sites deserialize MiniMessage, turn it into a legacy `§` string and call `sendMessage(String)` |
| `IncompatibleClassChangeError` on `LegacyComponentSerializer.legacySection()` | the interface call was emitted as a class call in an earlier patch | `ZabSendPatch.java` emits it with `isInterface=true` |
| `ClassNotFoundException: CommandUtils` after `plugman load` | the library loader needs a clean start | replace the jar and restart the server fully |

### Build the patched jar

You need the original `ZAutoBroadcast-1.3.jar` from its author and JDK 17 or newer.

```bash
cd patch
python build.py path/to/ZAutoBroadcast-1.3.jar
```

The script downloads ASM 9.7, compiles `ZabSendPatch.java`, rewrites the class, writes the new `plugin.yml` and saves `jar/ZAutoBroadcast-1.3-arclight.jar`. Put it in `plugins/` and restart the server; do not load it with PlugMan.

### Usage

| Command | Action |
|---|---|
| `/zab broadcast <key>` | send a broadcast from `forced-broadcasts` in `broadcasts.yml`; keys are case-sensitive |
| `/zab custom <minimessage>` | one-off message, for example `/zab custom <green>test</green>` |
| `/zab interval get`, `/zab interval set <seconds>` | read or change the interval |
| `/zab reload` | reload `broadcasts.yml` |

Permission: `zautobroadcast.admin`. Messages use MiniMessage tags, not `&` codes.

### Limitations

- It is a workaround for this plugin only; it does not add the Adventure API to the server.
- Hover, click and some gradients are lost when a message becomes a legacy string; colors and basic styles work.
- PlaceholderAPI works as in the original.

### Releases

A tag `v*` compiles the patch class on GitHub Actions and publishes the patch kit (`patch/`, README, license) with the notes from [CHANGELOG.md](CHANGELOG.md). The kit does not contain ZAutoBroadcast itself. The jar in `jar/` and in release 1.0.0 is the patched plugin from the first publication.

### License

The patch scripts and documentation are proprietary, all rights reserved; see [LICENSE](LICENSE). ZAutoBroadcast is the work of zepsizola ([SpigotMC](https://www.spigotmc.org/resources/zautobroadcast.113876/), [GitHub](https://github.com/ZepsiZola/ZAutoBroadcast)) and stays under its author's rights. This project is not affiliated with the author.

<a id="русский"></a>

## Русский

### Что исправлено

| Ошибка на Spigot или Arclight | Причина | Исправление |
|---|---|---|
| `NoClassDefFoundError: net/kyori/adventure/text/minimessage/MiniMessage` при каждой рассылке | плагин ждёт Adventure от Paper; в `plugin.yml` нет `libraries:` | в `plugin.yml` перечислены Adventure 4.17.0, examination и annotations, их скачивает загрузчик библиотек Bukkit |
| `NoSuchMethodError: Player.sendMessage(Component)` | метод есть только в Paper | ASM-патч `ZAutoBroadcast.class`: три места вызова разбирают MiniMessage, превращают в строку с `§` и вызывают `sendMessage(String)` |
| `IncompatibleClassChangeError` на `LegacyComponentSerializer.legacySection()` | в раннем патче вызов интерфейса был записан как вызов класса | `ZabSendPatch.java` пишет его с `isInterface=true` |
| `ClassNotFoundException: CommandUtils` после `plugman load` | загрузчику библиотек нужен чистый старт | заменить jar и полностью перезапустить сервер |

### Сборка патченого jar

Нужен оригинальный `ZAutoBroadcast-1.3.jar` от автора и JDK 17 или новее.

```bash
cd patch
python build.py path/to/ZAutoBroadcast-1.3.jar
```

Скрипт скачивает ASM 9.7, компилирует `ZabSendPatch.java`, переписывает класс, кладёт новый `plugin.yml` и сохраняет `jar/ZAutoBroadcast-1.3-arclight.jar`. Положите его в `plugins/` и перезапустите сервер; через PlugMan не загружать.

### Использование

| Команда | Действие |
|---|---|
| `/zab broadcast <ключ>` | отправить рассылку из `forced-broadcasts` в `broadcasts.yml`; регистр ключа важен |
| `/zab custom <minimessage>` | разовое сообщение, например `/zab custom <green>test</green>` |
| `/zab interval get`, `/zab interval set <секунды>` | узнать или поменять интервал |
| `/zab reload` | перечитать `broadcasts.yml` |

Право: `zautobroadcast.admin`. Сообщения пишутся тегами MiniMessage, не кодами `&`.

### Ограничения

- Это обход только для этого плагина; Adventure API на сервере не появляется.
- Наведение, клики и часть градиентов теряются при переводе в строку с `§`; цвета и простые стили работают.
- PlaceholderAPI работает как в оригинале.

### Релизы

Тег `v*` компилирует класс патча в GitHub Actions и публикует набор для патча (`patch/`, README, лицензия) с описанием из [CHANGELOG.md](CHANGELOG.md). Сам ZAutoBroadcast в набор не входит. Jar в `jar/` и в релизе 1.0.0 это патченый плагин из первой публикации.

### Лицензия

Скрипты патча и документация проприетарные, все права защищены; см. [LICENSE](LICENSE). ZAutoBroadcast это работа zepsizola ([SpigotMC](https://www.spigotmc.org/resources/zautobroadcast.113876/), [GitHub](https://github.com/ZepsiZola/ZAutoBroadcast)), права на него остаются у автора. Проект с автором не связан.
