# ZAutoBroadcast Arclight Fix

Unofficial patch for [ZAutoBroadcast](https://www.spigotmc.org/resources/zautobroadcast.113876/) **v1.3** (zepsizola) so the plugin runs on **Arclight** / **Spigot** hybrids (NeoForge + Bukkit) that do not ship the Paper Adventure API.

Tested on **Arclight NeoForge 1.21.1**.

## Ready-to-use JAR

Download from [Releases](https://github.com/milkycloud-dev/zautobroadcast-arclight-fix/releases) or use the file in this repo:

```
jar/ZAutoBroadcast-1.3-arclight.jar
```

**Install:** drop into `plugins/` and **fully restart** the server. Do **not** use `plugman load` — Spigot LibraryLoader must fetch Adventure libraries on a clean plugin load.

---

## Problems fixed

### 1. `NoClassDefFoundError: MiniMessage`

**Symptom:** console spam every ~5 minutes:

```
java.lang.NoClassDefFoundError: net/kyori/adventure/text/minimessage/MiniMessage
```

Auto-broadcasts and MiniMessage formatting did not work.

**Cause:** ZAutoBroadcast targets Paper and expects Adventure MiniMessage on the classpath. Paper bundles it; **Arclight/Spigot** does not. The original `plugin.yml` had no `libraries:` section, so LibraryLoader never downloaded Kyori jars.

**Fix:** added Maven dependencies (Adventure **4.17.0**) to `plugin.yml`:

- `adventure-api`
- `adventure-key`
- `adventure-text-minimessage`
- `adventure-text-serializer-legacy`
- `examination-api`, `examination-string`
- `jetbrains-annotations`

On first boot, jars land under `libraries/net/kyori/...`.

---

### 2. `NoSuchMethodError: Player.sendMessage(Component)`

**Symptom:** after MiniMessage was fixed, commands like `/zab broadcast Forced` still showed nothing; log:

```
java.lang.NoSuchMethodError: 'void org.bukkit.entity.Player.sendMessage(net.kyori.adventure.text.Component)'
```

**Cause:** the plugin sends chat via Paper’s `Player.sendMessage(Component)`. Bukkit/Spigot/Arclight only expose `sendMessage(String)`.

**Fix:** ASM patch on `ZAutoBroadcast.class` — all three `sendMessage(Component)` call sites become:

1. `MiniMessage.deserialize(...)` → `Component`
2. `LegacyComponentSerializer.legacySection().serialize(component)` → legacy `String` with § codes
3. `CommandSender.sendMessage(String)`

---

### 3. `IncompatibleClassChangeError` (first send patch)

**Symptom:**

```
IncompatibleClassChangeError: Method 'LegacyComponentSerializer.legacySection()' must be InterfaceMethodref constant
```

**Cause:** in Adventure 4.x, `LegacyComponentSerializer` is an **interface**. The static `legacySection()` call must use `isInterface=true` in bytecode. An earlier patch used `false`.

**Fix:** corrected `ZabSendPatch.java` (`INVOKESTATIC … legacySection`, `isInterface=true`).

---

### 4. `plugman load` breaks the classloader

**Symptom:** after `plugman unload/load` → `ClassNotFoundException: CommandUtils`, commands fail.

**Fix:** replace the JAR and do a **full server restart** only.

---

## Commands

| Command | Description |
|---------|-------------|
| `/zab broadcast Forced` | Manual broadcast by key from `forced-broadcasts` in `broadcasts.yml` |
| `/zab custom <minimessage>` | One-off message, e.g. `/zab custom <green>test</green>` |
| `/zab reload` | Reload config |

**Permission:** `zautobroadcast.admin`

**Keys:** case-sensitive — `Forced`, not `forced` (unless you add your own key in YAML).

**Audience:** all players **online** when the broadcast runs.

**Format:** MiniMessage (`<green>`, `<bold>`, gradients, etc.), not `&` — see [MiniMessage docs](https://docs.advntr.dev/minimessage/format.html).

---

## Build from upstream JAR

1. Obtain original **ZAutoBroadcast-1.3.jar** from the author.
2. Place at `upstream/ZAutoBroadcast-1.3.jar` or pass the path as an argument.
3. Requires **JDK 17+** with `javac` / `java` on PATH.

```bash
cd patch
python build.py ../upstream/ZAutoBroadcast-1.3.jar
```

Output: `jar/ZAutoBroadcast-1.3-arclight.jar`

ASM 9.7 is downloaded automatically to `patch/asm-9.7.jar`.

---

## Repository layout

```
jar/                          # patched plugin
patch/
  build.py                    # build from upstream JAR
  ZabSendPatch.java           # ASM send-path patch
LICENSE                       # MIT (patch + tooling)
README.md
```

---

## Limitations

- Does **not** add full Paper Adventure API to Arclight — only a workaround for ZAutoBroadcast.
- Rich MiniMessage (hover, click, some gradients) may degrade when converted to legacy § strings; basic colors/styles usually work.
- PlaceholderAPI works when installed (same as upstream).
- **ZAutoBroadcast** copyright remains with **zepsizola**. This is an unofficial patch; use at your own risk.

---

## License

Patch, build scripts, and documentation — **MIT** ([LICENSE](LICENSE)).

The upstream ZAutoBroadcast plugin is a separate product; respect its distribution terms.

---

## Credits

- [ZAutoBroadcast](https://www.spigotmc.org/resources/zautobroadcast.113876/) — zepsizola  
- [Kyori Adventure](https://github.com/KyoriPowered/adventure)  
- [Arclight](https://github.com/IzzelAliz/Arclight)

---
---

# ZAutoBroadcast Arclight Fix (RU)

Неофициальный патч для [ZAutoBroadcast](https://www.spigotmc.org/resources/zautobroadcast.113876/) **v1.3** (zepsizola), чтобы плагин работал на **Arclight** / **Spigot** гибридах (NeoForge + Bukkit), где нет Paper Adventure API.

Проверено на **Arclight NeoForge 1.21.1**.

## Готовый JAR

Скачайте из [Releases](https://github.com/milkycloud-dev/zautobroadcast-arclight-fix/releases) или возьмите из репозитория:

```
jar/ZAutoBroadcast-1.3-arclight.jar
```

**Установка:** положите в `plugins/` и сделайте **полный рестарт** сервера. **Не** используйте `plugman load` — LibraryLoader должен подтянуть Adventure при чистой загрузке плагина.

---

## Какие проблемы решены

### 1. `NoClassDefFoundError: MiniMessage`

**Симптом:** каждые ~5 минут в консоли:

```
java.lang.NoClassDefFoundError: net/kyori/adventure/text/minimessage/MiniMessage
```

Авто-рассылки и MiniMessage-формат не работали.

**Причина:** ZAutoBroadcast собран под Paper и ожидает Adventure MiniMessage в classpath. На Paper библиотека встроена; на **Arclight/Spigot** её нет, а в оригинальном `plugin.yml` не было `libraries:` — Spigot LibraryLoader не скачивал зависимости.

**Решение:** в `plugin.yml` добавлены Maven-зависимости Kyori Adventure **4.17.0**:

- `adventure-api`
- `adventure-key`
- `adventure-text-minimessage`
- `adventure-text-serializer-legacy`
- `examination-api`, `examination-string`
- `jetbrains-annotations`

При первом запуске JAR попадают в `libraries/net/kyori/...`.

---

### 2. `NoSuchMethodError: Player.sendMessage(Component)`

**Симптом:** после исправления MiniMessage команды вроде `/zab broadcast Forced` всё ещё ничего не показывали; в логе:

```
java.lang.NoSuchMethodError: 'void org.bukkit.entity.Player.sendMessage(net.kyori.adventure.text.Component)'
```

**Причина:** плагин шлёт сообщения через Paper-метод `Player.sendMessage(Component)`. В Bukkit/Spigot/Arclight есть только `sendMessage(String)`.

**Решение:** ASM-патч `ZAutoBroadcast.class` — три вызова `sendMessage(Component)` заменены на:

1. `MiniMessage.deserialize(...)` → `Component`
2. `LegacyComponentSerializer.legacySection().serialize(component)` → `String` с §-кодами
3. `CommandSender.sendMessage(String)`

---

### 3. `IncompatibleClassChangeError` (первый патч отправки)

**Симптом:**

```
IncompatibleClassChangeError: Method 'LegacyComponentSerializer.legacySection()' must be InterfaceMethodref constant
```

**Причина:** в Adventure 4.x `LegacyComponentSerializer` — **интерфейс**. Статический `legacySection()` в байткоде должен вызываться с `isInterface=true`. Первая версия патча использовала `false`.

**Решение:** исправлен `ZabSendPatch.java` (`INVOKESTATIC … legacySection`, `isInterface=true`).

---

### 4. `plugman load` ломает classloader

**Симптом:** после `plugman unload/load` — `ClassNotFoundException: CommandUtils`, команды падают.

**Решение:** после замены JAR — только **полный рестарт** сервера.

---

## Команды

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
3. Нужны **JDK 17+** и `javac` / `java` в PATH.

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
- Авторские права на **ZAutoBroadcast** принадлежат **zepsizola**. Неофициальный патч — на ваш риск.

---

## Лицензия

Патч, скрипты сборки и документация — **MIT** ([LICENSE](LICENSE)).

Оригинальный ZAutoBroadcast — отдельный продукт; соблюдайте условия его распространения.

---

## Благодарности

- [ZAutoBroadcast](https://www.spigotmc.org/resources/zautobroadcast.113876/) — zepsizola  
- [Kyori Adventure](https://github.com/KyoriPowered/adventure)  
- [Arclight](https://github.com/IzzelAliz/Arclight)
