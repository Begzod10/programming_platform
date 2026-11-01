using PcGuard.Service;

// PC Guard service: runs as LocalSystem in session 0 (installed by Task 13 with recovery options).
var builder = Host.CreateApplicationBuilder(new HostApplicationBuilderSettings
{
    Args = args,
    ContentRootPath = AppContext.BaseDirectory, // appsettings.json next to the exe, not the SCM's cwd (System32)
});
builder.Services.AddWindowsService(o => o.ServiceName = "PcGuard");
builder.Services.AddHostedService<GuardWorker>();

var host = builder.Build();
await host.RunAsync();
