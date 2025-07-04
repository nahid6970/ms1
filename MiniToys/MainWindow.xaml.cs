using System.ComponentModel;
using System.Windows;
using System.Windows.Controls;
using Hardcodet.Wpf.TaskbarNotification;

namespace MiniToys
{
    /// <summary>
    /// Interaction logic for MainWindow.xaml
    /// </summary>
    public partial class MainWindow : Window
    {
        private TaskbarIcon _notifyIcon = null!;

        public MainWindow()
        {
            InitializeComponent();
            SetupNotifyIcon();
        }

        private void SetupNotifyIcon()
        {
            _notifyIcon = new TaskbarIcon();
            _notifyIcon.Icon = System.Drawing.SystemIcons.Application; // Using a default system icon
            _notifyIcon.ToolTipText = "MiniToys";

            // Create a context menu
            ContextMenu contextMenu = new ContextMenu();
            MenuItem showMenuItem = new MenuItem { Header = "Show" };
            showMenuItem.Click += (s, args) => ShowMainWindow();
            contextMenu.Items.Add(showMenuItem);

            MenuItem exitMenuItem = new MenuItem { Header = "Exit" };
            exitMenuItem.Click += (s, args) => ExitApplication();
            contextMenu.Items.Add(exitMenuItem);

            _notifyIcon.ContextMenu = contextMenu;

            _notifyIcon.TrayMouseDoubleClick += (s, args) => ShowMainWindow();
        }

        private void ShowMainWindow()
        {
            this.Show();
            this.WindowState = WindowState.Normal;
            this.Activate();
        }

        private void ExitApplication()
        {
            _notifyIcon.Dispose();
            System.Windows.Application.Current.Shutdown();
        }

        private void Window_Closing(object sender, CancelEventArgs e)
        {
            // Hide the window to tray instead of closing
            e.Cancel = true;
            this.Hide();
        }

        private void MainMenuListBox_SelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            if (MainMenuListBox.SelectedItem is ListBoxItem selectedItem)
            {
                switch (selectedItem.Content.ToString())
                {
                    case "General":
                        SubMenuContentControl.Content = new GeneralSettingsControl();
                        break;
                    case "Appearance":
                        SubMenuContentControl.Content = new AppearanceSettingsControl();
                        break;
                    case "About":
                        SubMenuContentControl.Content = new AboutControl();
                        break;
                    default:
                        SubMenuContentControl.Content = null;
                        break;
                }
            }
        }
    }
}
