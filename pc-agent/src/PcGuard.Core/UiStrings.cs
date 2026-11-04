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
    public static string Connecting(UiLang l) => l == UiLang.Ru ? "Подключение к службе…" : "Xizmatga ulanmoqda…";

    // ---- administrator maintenance unlock (emergency) ----

    public static string AdminLink(UiLang l) => l == UiLang.Ru ? "Администратор" : "Administrator";
    public static string AdminTitle(UiLang l) => l == UiLang.Ru ? "Вход администратора" : "Administrator kirishi";
    public static string AdminAccountLabel(UiLang l) => l == UiLang.Ru ? "Учётная запись Windows" : "Windows akkaunti";
    public static string AdminPasswordLabel(UiLang l) => PasswordLabel(l);
    public static string AdminDurationLabel(UiLang l) => l == UiLang.Ru ? "Длительность" : "Muddat";
    public static string AdminUnlockButton(UiLang l) => l == UiLang.Ru ? "Открыть" : "Ochish";
    public static string AdminCancelButton(UiLang l) => l == UiLang.Ru ? "Отмена" : "Bekor qilish";
    public static string MaintenanceEndButton(UiLang l) => l == UiLang.Ru ? "Завершить" : "Tugatish";
    public static string AdminWarning(UiLang l) => l == UiLang.Ru
        ? "Вводите пароль так, чтобы его никто не видел"
        : "Parolni faqat o'zingiz ko'ra oladigan joyda kiriting";

    /// <summary>Label of one of the fixed durations (15, 60, 240 minutes); any other value throws.</summary>
    public static string AdminDuration(UiLang l, int minutes)
    {
        var ru = l == UiLang.Ru;
        return minutes switch
        {
            15 => ru ? "15 минут" : "15 daqiqa",
            60 => ru ? "1 час" : "1 soat",
            240 => ru ? "4 часа" : "4 soat",
            _ => throw new ArgumentOutOfRangeException(nameof(minutes), minutes, "Not an allowed maintenance duration"),
        };
    }

    /// <summary>Banner text; <paramref name="time"/> is the local end time (see <see cref="ClockTime"/>).</summary>
    public static string MaintenanceBanner(UiLang l, string time)
        => (l == UiLang.Ru ? "Режим обслуживания до {time}" : "Texnik rejim {time} gacha").Replace("{time}", time);

    /// <summary>24-hour "HH:mm" of the given time in its own offset (pass a local time).</summary>
    public static string ClockTime(DateTimeOffset t) => t.ToString("HH:mm", System.Globalization.CultureInfo.InvariantCulture);

    /// <summary>Maps an admin_result.error code; invalid_duration, error, null and unknown codes read as a generic error.</summary>
    public static string AdminError(UiLang l, string? code, int retrySeconds)
    {
        var ru = l == UiLang.Ru;
        var n = Math.Max(0, retrySeconds).ToString(System.Globalization.CultureInfo.InvariantCulture);
        return code switch
        {
            AdminErrors.BadCredentials => ru ? "Неверный логин или пароль" : "Login yoki parol noto'g'ri",
            AdminErrors.NotAdmin => ru ? "Этот аккаунт не администратор" : "Bu akkaunt administrator emas",
            AdminErrors.LockedOut => (ru ? "Слишком много попыток. Повторите через {n} с" : "Juda ko'p urinish. {n} soniyadan so'ng qayta urinib ko'ring").Replace("{n}", n),
            _ => ru ? "Произошла ошибка" : "Xatolik yuz berdi",
        };
    }
}
