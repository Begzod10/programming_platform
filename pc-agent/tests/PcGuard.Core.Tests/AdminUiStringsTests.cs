using PcGuard.Core;

namespace PcGuard.Core.Tests;

public class AdminUiStringsTests
{
    [Fact]
    public void LabelsExact()
    {
        Assert.Equal("Administrator", UiStrings.AdminLink(UiLang.Uz));
        Assert.Equal("Администратор", UiStrings.AdminLink(UiLang.Ru));
        Assert.Equal("Administrator kirishi", UiStrings.AdminTitle(UiLang.Uz));
        Assert.Equal("Вход администратора", UiStrings.AdminTitle(UiLang.Ru));
        Assert.Equal("Windows akkaunti", UiStrings.AdminAccountLabel(UiLang.Uz));
        Assert.Equal("Учётная запись Windows", UiStrings.AdminAccountLabel(UiLang.Ru));
        Assert.Equal("Parol", UiStrings.AdminPasswordLabel(UiLang.Uz));
        Assert.Equal("Пароль", UiStrings.AdminPasswordLabel(UiLang.Ru));
        Assert.Equal("Muddat", UiStrings.AdminDurationLabel(UiLang.Uz));
        Assert.Equal("Длительность", UiStrings.AdminDurationLabel(UiLang.Ru));
        Assert.Equal("Ochish", UiStrings.AdminUnlockButton(UiLang.Uz));
        Assert.Equal("Открыть", UiStrings.AdminUnlockButton(UiLang.Ru));
        Assert.Equal("Bekor qilish", UiStrings.AdminCancelButton(UiLang.Uz));
        Assert.Equal("Отмена", UiStrings.AdminCancelButton(UiLang.Ru));
        Assert.Equal("Tugatish", UiStrings.MaintenanceEndButton(UiLang.Uz));
        Assert.Equal("Завершить", UiStrings.MaintenanceEndButton(UiLang.Ru));
        Assert.Equal("Parolni faqat o'zingiz ko'ra oladigan joyda kiriting", UiStrings.AdminWarning(UiLang.Uz));
        Assert.Equal("Вводите пароль так, чтобы его никто не видел", UiStrings.AdminWarning(UiLang.Ru));
    }

    [Theory]
    [InlineData(15, "15 daqiqa", "15 минут")]
    [InlineData(60, "1 soat", "1 час")]
    [InlineData(240, "4 soat", "4 часа")]
    public void DurationChoicesExact(int minutes, string uz, string ru)
    {
        Assert.Equal(uz, UiStrings.AdminDuration(UiLang.Uz, minutes));
        Assert.Equal(ru, UiStrings.AdminDuration(UiLang.Ru, minutes));
    }

    [Theory]
    [InlineData(0)]
    [InlineData(30)]
    [InlineData(241)]
    public void DurationOutsideTheFixedSetThrows(int minutes)
        => Assert.Throws<ArgumentOutOfRangeException>(() => UiStrings.AdminDuration(UiLang.Uz, minutes));

    [Fact]
    public void EveryAllowedDurationHasAChoice()
    {
        foreach (var lang in Enum.GetValues<UiLang>())
        foreach (var m in MaintenanceMode.AllowedMinutes)
            Assert.False(string.IsNullOrWhiteSpace(UiStrings.AdminDuration(lang, m)));
    }

    [Fact]
    public void BannerSubstitutesTime()
    {
        Assert.Equal("Texnik rejim 14:05 gacha", UiStrings.MaintenanceBanner(UiLang.Uz, "14:05"));
        Assert.Equal("Режим обслуживания до 14:05", UiStrings.MaintenanceBanner(UiLang.Ru, "14:05"));
    }

    [Fact]
    public void ClockTimeIs24HourHHmmOfTheGivenOffset()
    {
        Assert.Equal("14:05", UiStrings.ClockTime(new DateTimeOffset(2026, 10, 23, 14, 5, 59, TimeSpan.FromHours(5))));
        Assert.Equal("00:00", UiStrings.ClockTime(new DateTimeOffset(2026, 10, 23, 0, 0, 0, TimeSpan.Zero)));
        Assert.Equal("23:59", UiStrings.ClockTime(new DateTimeOffset(2026, 10, 23, 23, 59, 0, TimeSpan.Zero)));
    }

    [Theory]
    [InlineData("bad_credentials", 0, "Login yoki parol noto'g'ri", "Неверный логин или пароль")]
    [InlineData("not_admin", 0, "Bu akkaunt administrator emas", "Этот аккаунт не администратор")]
    [InlineData("locked_out", 600, "Juda ko'p urinish. 600 soniyadan so'ng qayta urinib ko'ring", "Слишком много попыток. Повторите через 600 с")]
    [InlineData("locked_out", 1, "Juda ko'p urinish. 1 soniyadan so'ng qayta urinib ko'ring", "Слишком много попыток. Повторите через 1 с")]
    [InlineData("locked_out", -3, "Juda ko'p urinish. 0 soniyadan so'ng qayta urinib ko'ring", "Слишком много попыток. Повторите через 0 с")]
    [InlineData("invalid_duration", 0, "Xatolik yuz berdi", "Произошла ошибка")]
    [InlineData("error", 0, "Xatolik yuz berdi", "Произошла ошибка")]
    [InlineData("whatever", 0, "Xatolik yuz berdi", "Произошла ошибка")]
    [InlineData(null, 0, "Xatolik yuz berdi", "Произошла ошибка")]
    public void AdminErrorsExact(string? code, int retry, string uz, string ru)
    {
        Assert.Equal(uz, UiStrings.AdminError(UiLang.Uz, code, retry));
        Assert.Equal(ru, UiStrings.AdminError(UiLang.Ru, code, retry));
    }

    [Fact]
    public void ParityEveryAdminStringNonEmptyAndDifferentPerLanguage()
    {
        var getters = new Func<UiLang, string>[]
        {
            UiStrings.AdminLink, UiStrings.AdminTitle, UiStrings.AdminAccountLabel, UiStrings.AdminPasswordLabel,
            UiStrings.AdminDurationLabel, UiStrings.AdminUnlockButton, UiStrings.AdminCancelButton,
            UiStrings.MaintenanceEndButton, UiStrings.AdminWarning,
            l => UiStrings.MaintenanceBanner(l, "10:00"),
            l => UiStrings.AdminError(l, "bad_credentials", 0),
            l => UiStrings.AdminError(l, "not_admin", 0),
            l => UiStrings.AdminError(l, "locked_out", 5),
            l => UiStrings.AdminError(l, "error", 0),
        };
        foreach (var g in getters)
        {
            var uz = g(UiLang.Uz);
            var ru = g(UiLang.Ru);
            Assert.False(string.IsNullOrWhiteSpace(uz));
            Assert.False(string.IsNullOrWhiteSpace(ru));
            Assert.NotEqual(uz, ru);
            Assert.DoesNotContain("{", uz + ru);
        }
    }
}
