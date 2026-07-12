# ZAutoBroadcast Arclight Fix

Патч для [ZAutoBroadcast](https://www.spigotmc.org/resources/zautobroadcast.113876/) **v1.3** (zepsizola), чтобы плагин работал на **Arclight** / **Spigot** гибридах (NeoForge + Bukkit), где нет Paper Adventure API.

Проверено на **Arclight NeoForge 1.21.1** (NoteBuns).

## Готовый JAR

Скачайте из [Releases](https://github.com/milkycloud-dev/zautobroadcast-arclight-fix/releases) или возьмите из папки:

```
jar/ZAutoBroadcast-1.3-arclight.jar
```

Установка: положите в `plugins/`, перезапустите сервер (**не** `plugman load` — нужен полный рестарт, чтобы Spigot LibraryLoader подтянул Adventure).

---

## Какие проблемы решены

### 1. `NoClassDefFoundError: MiniMessage`

**Симптом:** каждые ~5 минут в консоли:

```
java.lang.NoClassDefFoundError: net/kyori/adventure/text/minimessage/MiniMessage
```

Авто-рассылки и MiniMessage-формат не работали.

**Причина:** ZAutoBroadcast собран под Paper и ожидает Adventure MiniMessage в classpath. На **Paper** библиотека встроена в API. На **Arclight/Spigot** её нет, а в оригинальном `plugin.yml` не было секции `libraries:` — Spigot LibraryLoader не скачивал зависимости.

**Решение:** в `plugin.yml` добавлены Maven-зависимости Kyori Adventure 4.17.0:

- `adventure-api`
- `adventure-key`
- `adventure-text-minimessage`
- `adventure-text-serializer-legacy`
- `examination-api`, `examination-string`
- `jetbrains-annotations`

При **первом запуске** сервер кладёт JAR в `libraries/net/kyori/...`.

---

### 2. `NoSuchMethodError: Player.sendMessage(Component)`

**Симптом:** после исправления MiniMessage команды вроде `/zab broadcast Forced` всё ещё ничего не показывали; в логе:

```
java.lang.NoSuchMethodError: 'void org.bukkit.entity.Player.sendMessage(net.kyori.adventure.text.Component)'
```

**Причина:** плагин шлёт сообщения через Paper-метод `Player.sendMessage(Component)`. В Bukkit/Spigot/Arclight есть только `sendMessage(String)`.

**Решение:** ASM-патч `ZAutoBroadcast.class` — три вызова `sendMessage(Component)` заменены на цепочку:

1. `MiniMessage.deserialize(...)` → `Component`
2. `LegacyComponentSerializer.legacySection().serialize(component)` → `String` с §-кодами
3. `CommandSender.sendMessage(String)`

---

### 3. `IncompatibleClassChangeError` при первом патче отправки

**Симптом:**

```
IncompatibleClassChangeError: Method 'LegacyComponentSerializer.legacySection()' must be InterfaceMethodref constant
```

**Причина:** в Adventure 4.x `LegacyComponentSerializer` — **интерфейс**. Статический `legacySection()` в байткоде должен вызываться с флагом `isInterface=true`. Первая версия патча использовала `false`.

**Решение:** исправлен `ZabSendPatch.java` (`INVOKESTATIC … legacySection`, `isInterface=true`).

---

### 4. `plugman load` ломает classloader

**Симптом:** после `plugman unload/load` — `ClassNotFoundException: CommandUtils`, команды падают.

**Решение:** после замены JAR — только **полный рестарт** сервера.

---

## Использование команд

| Команда | Описание |
|---------|----------|
| `/zab broadcast Forced` | Ручная рассылка по ключу из `forced-broadcasts` в `broadcasts.yml` |
| `/zab custom <minimessage>` | Разовое сообщение, напр. `/zab custom <green>тест</green>` |
| `/zab reload` | Перечитать конфиг |

**Права:** `zautobroadcast.admin`

**Ключи:** регистр важен — `Forced`, не `forced` (если не добавлен свой ключ в YAML).

**Кому видно:** всем игрокам **онлайн** в момент отправки.

**Формат:** MiniMessage (`<green>`, `<bold>`, градиенты и т.д.), не `&` — см. [документацию MiniMessage](https://docs.advntr.dev/minimessage/format.html).

---

## Сборка из исходного JAR

1. Скачайте оригинальный **ZAutoBroadcast-1.3.jar** у автора.
2. Положите в `upstream/ZAutoBroadcast-1.3.jar` или передайте путь аргументом.
3. Нужны **JDK 17+** и **javac/java** в PATH.

```bash
cd patch
python build.py ../upstream/ZAutoBroadcast-1.3.jar
```

Результат: `jar/ZAutoBroadcast-1.3-arclight.jar`

ASM 9.7 скачивается автоматически в `patch/asm-9.7.jar`.

---

## Структура репозитория

```
jar/                          # готовый пропатченный плагин
patch/
  build.py                    # сборка из upstream JAR
  ZabSendPatch.java           # ASM-патч отправки сообщений
LICENSE                       # MIT (патч и tooling)
README.md
```

---

## Ограничения

- Патч **не** добавляет полноценный Paper Adventure API на Arclight — только обход для ZAutoBroadcast.
- Сложный MiniMessage (hover, click, gradient) частично теряется при конвертации в legacy §-строки; простые цвета и стили обычно работают.
- PlaceholderAPI поддерживается, если установлен (как в оригинале).
- Авторские права на **ZAutoBroadcast** принадлежат **zepsizola**. Этот репозиторий — неофициальный патч; используйте на свой риск.

---

## Лицензия

Патч, скрипты сборки и документация — **MIT** (см. [LICENSE](LICENSE)).

Оригинальный плагин ZAutoBroadcast — отдельный продукт; соблюдайте условия его распространения.

---

## Благодарности

- [ZAutoBroadcast](https://www.spigotmc.org/resources/zautobroadcast.113876/) — zepsizola  
- [Kyori Adventure](https://github.com/KyoriPowered/adventure)  
- [Arclight](https://github.com/IzzelAliz/Arclight)
