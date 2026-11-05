namespace PcGuard.Core;

public enum UiLang { Uz, Ru }

/// <summary>All user-visible shell strings (Uzbek default, Russian second). Pure, no UI dependencies.</summary>
public static class UiStrings
{
    private const string BannerUz = "Yana {n} ta dars qoldi";
    private const string BannerRu = "Осталось уроков: {n}";

    public static string Notice(UiLang l) => l == UiLang.Ru
        ? "Записываются названия программ и время использования. Скриншоты и нажатия клавиш не записываются."
        : "Dastur nomlari va foydalanish vaqti yozib boriladi. Ekran rasmlari va tugma bosishlar yozilmaydi.";

    /// <summary>Maps a login_result.error code; null, empty and unknown codes read as "offline".</summary>
    public static string LoginError(UiLang l, string? code)
    {
        var ru = l == UiLang.Ru;
        return code switch
        {
            "bad_credentials" => ru ? "Неверный логин или пароль" : "Login yoki parol noto'g'ri",
            "not_a_student" => ru ? "На этом компьютере могут работать только ученики" : "Bu kompyuterga faqat o'quvchilar kira oladi",
            "rate_limited" => ru ? "Слишком много попыток. Повторите через минуту" : "Juda ko'p urinish. Bir daqiqadan so'ng qayta urinib ko'ring",
            _ => ru ? "Нет связи с сервером" : "Serverga ulanib bo'lmadi",
        };
    }

    /// <summary>Banner text; <c>{n}</c> is replaced by the remaining lessons (negative clamps to 0).</summary>
    public static string Banner(UiLang l, int remaining)
        => (l == UiLang.Ru ? BannerRu : BannerUz).Replace("{n}", Math.Max(0, remaining).ToString(System.Globalization.CultureInfo.InvariantCulture));

    public static string SignOut(UiLang l) => l == UiLang.Ru ? "Выйти" : "Chiqish";
    public static string LoginButton(UiLang l) => l == UiLang.Ru ? "Войти" : "Kirish";
    public static string UsernameLabel(UiLang l) => l == UiLang.Ru ? "Логин" : "Login";
    public static string PasswordLabel(UiLang l) => l == UiLang.Ru ? "Пароль" : "Parol";
    /// <summary>Text of the minimal fallback lock window (both languages at once: it has no language
    /// switch, see <see cref="ShellUiFallback"/>).</summary>
    public static string FallbackLock() =>
        "Kompyuter bloklangan. Kirish oynasini ochib bo'lmadi: o'qituvchi yoki administratorga murojaat qiling."
        + "\n\n"
        + "Компьютер заблокирован. Не удалось открыть окно входа: обратитесь к преподавателю или администратору.";

    public static string Connecting(UiLang l) => l == UiLang.Ru ? "Подключение к службе…" : "Xizmatga ulanmoqda…";

    // ---- maintenance mode (one-time teacher code) ----
    // Durations are not chosen on the PC: the teacher picks 15, 60 or 240 minutes when issuing the code.

    public static string AdminLink(UiLang l) => l == UiLang.Ru ? "Код обслуживания" : "Texnik kod";
    public static string AdminTitle(UiLang l) => l == UiLang.Ru ? "Режим обслуживания" : "Texnik rejim";
    public static string MaintenanceCodeLabel(UiLang l) => l == UiLang.Ru ? "Код обслуживания (6 цифр)" : "Texnik kod (6 raqam)";
    public static string AdminUnlockButton(UiLang l) => l == UiLang.Ru ? "Открыть" : "Ochish";
    public static string AdminCancelButton(UiLang l) => l == UiLang.Ru ? "Отмена" : "Bekor qilish";
    public static string MaintenanceEndButton(UiLang l) => l == UiLang.Ru ? "Завершить" : "Tugatish";

    /// <summary>Banner text; <paramref name="time"/> is the local end time (see <see cref="ClockTime"/>).</summary>
    public static string MaintenanceBanner(UiLang l, string time)
        => (l == UiLang.Ru ? "Режим обслуживания до {time}" : "Texnik rejim {time} gacha").Replace("{time}", time);

    /// <summary>24-hour "HH:mm" of the given time in its own offset (pass a local time).</summary>
    public static string ClockTime(DateTimeOffset t) => t.ToString("HH:mm", System.Globalization.CultureInfo.InvariantCulture);

    /// <summary>Maps an admin_result.error code; error, null and unknown codes read as a generic error.</summary>
    public static string AdminError(UiLang l, string? code, int retrySeconds)
    {
        var ru = l == UiLang.Ru;
        var n = Math.Max(0, retrySeconds).ToString(System.Globalization.CultureInfo.InvariantCulture);
        return code switch
        {
            AdminErrors.InvalidCode => ru ? "Неверный код или срок действия истёк" : "Kod noto'g'ri yoki muddati o'tgan",
            AdminErrors.Offline => ru ? "Нет связи с сервером" : "Serverga ulanib bo'lmadi",
            AdminErrors.RateLimited => ru ? "Слишком много попыток, повторите позже" : "Juda ko'p urinish, keyinroq urinib ko'ring",
            AdminErrors.LockedOut => (ru ? "Слишком много попыток. Повторите через {n} с" : "Juda ko'p urinish. {n} soniyadan so'ng qayta urinib ko'ring").Replace("{n}", n),
            _ => ru ? "Произошла ошибка" : "Xatolik yuz berdi",
        };
    }

    // ---- recovery code (offline, set at install; stops and disables PC Guard on this PC) ----

    public static string RecoveryLink(UiLang l) => l == UiLang.Ru ? "Код восстановления" : "Tiklash kodi";
    public static string RecoveryTitle(UiLang l) => l == UiLang.Ru ? "Отключение PC Guard" : "PC Guard'ni o'chirish";
    public static string RecoveryCodeLabel(UiLang l) => l == UiLang.Ru ? "Код восстановления (задан при установке)" : "Tiklash kodi (o'rnatishda berilgan)";
    public static string RecoveryHint(UiLang l) => l == UiLang.Ru
        ? "Код действует один раз: если он верный, PC Guard будет остановлен и отключён на этом компьютере. Снова включить его может администратор, переустановив PC Guard с новым кодом."
        : "Kod faqat bir marta ishlaydi: to'g'ri bo'lsa, PC Guard bu kompyuterda to'xtatiladi va o'chiriladi. Uni administrator yangi kod bilan qayta o'rnatib yoqishi mumkin.";

    /// <summary>
    /// Sent by the service as a "message" popup when the recovery code was accepted but the service
    /// could not set its own start type to Disabled (both languages, the student's choice is unknown there).
    /// </summary>
    public static string RecoveryDisableFailedNotice() =>
        "PC Guard bu kompyuterda to'xtatildi, lekin uni o'chirib bo'lmadi: kompyuter qayta yoqilsa, u yana ishga tushishi mumkin. Administratorga xabar bering.\n"
        + "PC Guard на этом компьютере остановлен, но отключить его не удалось: после перезагрузки он может снова запуститься. Сообщите администратору.";

    /// <summary>Maps a recovery_result.error code; error, null and unknown codes read as a generic error.</summary>
    public static string RecoveryError(UiLang l, string? code, int retrySeconds)
    {
        var ru = l == UiLang.Ru;
        return code switch
        {
            AdminErrors.InvalidCode => ru ? "Неверный код восстановления" : "Tiklash kodi noto'g'ri",
            RecoveryErrors.NotConfigured => ru ? "На этом компьютере код восстановления не задан" : "Bu kompyuterda tiklash kodi o'rnatilmagan",
            RecoveryErrors.WrongLayout => ru
                ? "Код состоит только из латинских букв, цифр и знаков. Переключите раскладку клавиатуры на английскую (EN) и введите код снова"
                : "Kod faqat lotin harflari, raqamlar va belgilardan iborat. Klaviaturani inglizcha (EN) tartibga o'tkazib, kodni qayta kiriting",
            AdminErrors.LockedOut => AdminError(l, AdminErrors.LockedOut, retrySeconds),
            _ => AdminError(l, AdminErrors.Error, 0),
        };
    }
}
