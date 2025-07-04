using System.Windows;

namespace MiniToys
{
    /// <summary>
    /// Interaction logic for App.xaml
    /// </summary>
    public partial class App : Application
    {
        protected override void OnStartup(StartupEventArgs e)
        {
            base.OnStartup(e);

            // Create the main window, but don't show it immediately
            MainWindow mainWindow = new MainWindow();
            // mainWindow.Show(); // We'll show it via the tray icon
        }
    }
}