using PcGuard.Core;

namespace PcGuard.Core.Tests;

public class MaintenanceUiStringsTests
{
    [Fact]
    public void LabelsExact()
    {
        Assert.Equal("Administrator", UiStrings.AdminLink(UiLang.Uz));
        Assert.Equal("Администратор", UiStrings.AdminLink(UiLang.Ru));
        Assert.Equal("Texnik rejim", UiStrings.AdminTitle(UiLang.Uz));
        Assert.Equal("Режим обслуживания", UiStrings.AdminTitle(UiLang.Ru));
        Assert.Equal("Texnik kod (6 raqam)", UiStrings.MaintenanceCodeLabel(UiLang.Uz));
        Assert.Equal("Код обслуживания (6 цифр)", UiStrings.MaintenanceCodeLabel(UiLang.Ru));
        Assert.Equal("Ochish", UiStrings.AdminUnlockButton(UiLang.Uz));
        Assert.Equal("Открыть", UiStrings.AdminUnlockButton(UiLang.Ru));
        Assert.Equal("Bekor qilish", UiStrings.AdminCancelButton(UiLang.Uz));
        Assert.Equal("Отмена", UiStrings.AdminCancelButton(UiLang.Ru));
        Assert.Equal("Tugatish", UiStrings.MaintenanceEndButton(UiLang.Uz));
        Assert.Equal("Завершить", UiStrings.MaintenanceEndButton(UiLang.Ru));
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
    [InlineData("invalid_code", 0, "Kod noto'g'ri yoki muddati o'tgan", "Неверный код или срок действия истёк")]
    [InlineData("offline", 0, "Serverga ulanib bo'lmadi", "Нет связи с сервером")]
    [InlineData("rate_limited", 0, "Juda ko'p urinish, keyinroq urinib ko'ring", "Слишком много попыток, повторите позже")]
    [InlineData("locked_out", 600, "Juda ko'p urinish. 600 soniyadan so'ng qayta urinib ko'ring", "Слишком много попыток. Повторите через 600 с")]
    [InlineData("locked_out", 1, "Juda ko'p urinish. 1 soniyadan so'ng qayta urinib ko'ring", "Слишком много попыток. Повторите через 1 с")]
    [InlineData("locked_out", -3, "Juda ko'p urinish. 0 soniyadan so'ng qayta urinib ko'ring", "Слишком много попыток. Повторите через 0 с")]
    [InlineData("error", 0, "Xatolik yuz berdi", "Произошла ошибка")]
    [InlineData("bad_credentials", 0, "Xatolik yuz berdi", "Произошла ошибка")]
    [InlineData("whatever", 0, "Xatolik yuz berdi", "Произошла ошибка")]
    [InlineData(null, 0, "Xatolik yuz berdi", "Произошла ошибка")]
    public void AdminErrorsExact(string? code, int retry, string uz, string ru)
    {
        Assert.Equal(uz, UiStrings.AdminError(UiLang.Uz, code, retry));
        Assert.Equal(ru, UiStrings.AdminError(UiLang.Ru, code, retry));
    }

    [Fact]
    public void EveryServiceErrorCodeHasItsOwnText()
    {
        var generic = UiStrings.AdminError(UiLang.Uz, AdminErrors.Error, 0);
        foreach (var code in new[] { AdminErrors.InvalidCode, AdminErrors.LockedOut, AdminErrors.RateLimited, AdminErrors.Offline })
            Assert.NotEqual(generic, UiStrings.AdminError(UiLang.Uz, code, 5));
    }

    [Fact]
    public void ParityEveryMaintenanceStringNonEmptyAndDifferentPerLanguage()
    {
        var getters = new Func<UiLang, string>[]
        {
            UiStrings.AdminLink, UiStrings.AdminTitle, UiStrings.MaintenanceCodeLabel,
            UiStrings.AdminUnlockButton, UiStrings.AdminCancelButton, UiStrings.MaintenanceEndButton,
            l => UiStrings.MaintenanceBanner(l, "10:00"),
            l => UiStrings.AdminError(l, "invalid_code", 0),
            l => UiStrings.AdminError(l, "offline", 0),
            l => UiStrings.AdminError(l, "rate_limited", 0),
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
