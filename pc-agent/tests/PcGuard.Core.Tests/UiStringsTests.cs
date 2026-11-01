using PcGuard.Core;

namespace PcGuard.Core.Tests;

public class UiStringsTests
{
    [Fact]
    public void NoticeExact()
    {
        Assert.Equal("Dastur nomlari va foydalanish vaqti yozib boriladi. Ekran rasmlari va tugma bosishlar yozilmaydi.", UiStrings.Notice(UiLang.Uz));
        Assert.Equal("Записываются названия программ и время использования. Скриншоты и нажатия клавиш не записываются.", UiStrings.Notice(UiLang.Ru));
    }

    [Theory]
    [InlineData("bad_credentials", "Login yoki parol noto'g'ri", "Неверный логин или пароль")]
    [InlineData("not_a_student", "Bu kompyuterga faqat o'quvchilar kira oladi", "На этом компьютере могут работать только ученики")]
    [InlineData("rate_limited", "Juda ko'p urinish. Bir daqiqadan so'ng qayta urinib ko'ring", "Слишком много попыток. Повторите через минуту")]
    [InlineData("offline", "Serverga ulanib bo'lmadi", "Нет связи с сервером")]
    [InlineData("something_else", "Serverga ulanib bo'lmadi", "Нет связи с сервером")]
    [InlineData(null, "Serverga ulanib bo'lmadi", "Нет связи с сервером")]
    [InlineData("", "Serverga ulanib bo'lmadi", "Нет связи с сервером")]
    public void LoginErrors(string? code, string uz, string ru)
    {
        Assert.Equal(uz, UiStrings.LoginError(UiLang.Uz, code));
        Assert.Equal(ru, UiStrings.LoginError(UiLang.Ru, code));
    }

    [Fact]
    public void BannerSubstitutesN()
    {
        Assert.Equal("Yana 3 ta dars qoldi", UiStrings.Banner(UiLang.Uz, 3));
        Assert.Equal("Осталось уроков: 12", UiStrings.Banner(UiLang.Ru, 12));
        Assert.Equal("Yana 0 ta dars qoldi", UiStrings.Banner(UiLang.Uz, 0));
    }

    [Fact]
    public void NegativeRemainingClampedToZero()
        => Assert.Equal("Yana 0 ta dars qoldi", UiStrings.Banner(UiLang.Uz, -4));

    [Fact]
    public void SimpleLabelsExact()
    {
        Assert.Equal("Chiqish", UiStrings.SignOut(UiLang.Uz));
        Assert.Equal("Выйти", UiStrings.SignOut(UiLang.Ru));
        Assert.Equal("Kirish", UiStrings.LoginButton(UiLang.Uz));
        Assert.Equal("Войти", UiStrings.LoginButton(UiLang.Ru));
        Assert.Equal("Login", UiStrings.UsernameLabel(UiLang.Uz));
        Assert.Equal("Логин", UiStrings.UsernameLabel(UiLang.Ru));
        Assert.Equal("Parol", UiStrings.PasswordLabel(UiLang.Uz));
        Assert.Equal("Пароль", UiStrings.PasswordLabel(UiLang.Ru));
        Assert.Equal("Xizmatga ulanmoqda…", UiStrings.Connecting(UiLang.Uz));
        Assert.Equal("Подключение к службе…", UiStrings.Connecting(UiLang.Ru));
    }

    [Fact]
    public void EveryStringNonEmptyInBothLanguages()
    {
        foreach (var lang in Enum.GetValues<UiLang>())
        {
            Assert.False(string.IsNullOrWhiteSpace(UiStrings.Notice(lang)));
            Assert.False(string.IsNullOrWhiteSpace(UiStrings.SignOut(lang)));
            Assert.False(string.IsNullOrWhiteSpace(UiStrings.LoginButton(lang)));
            Assert.False(string.IsNullOrWhiteSpace(UiStrings.UsernameLabel(lang)));
            Assert.False(string.IsNullOrWhiteSpace(UiStrings.PasswordLabel(lang)));
            Assert.False(string.IsNullOrWhiteSpace(UiStrings.Connecting(lang)));
            Assert.DoesNotContain("{n}", UiStrings.Banner(lang, 1));
            foreach (var code in new[] { "bad_credentials", "not_a_student", "rate_limited", "offline", "x" })
                Assert.False(string.IsNullOrWhiteSpace(UiStrings.LoginError(lang, code)));
        }
    }

    [Fact]
    public void LanguageStringsDiffer()
    {
        Assert.NotEqual(UiStrings.Notice(UiLang.Uz), UiStrings.Notice(UiLang.Ru));
        Assert.NotEqual(UiStrings.LoginButton(UiLang.Uz), UiStrings.LoginButton(UiLang.Ru));
    }
}
