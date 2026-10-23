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
}
