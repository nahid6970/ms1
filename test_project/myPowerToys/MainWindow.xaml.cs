using System;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Media;

namespace MyPowerTools;

public partial class MainWindow : Window
{
    public MainWindow()
    {
        InitializeComponent();
        LoadGeneralPage();
    }

    private void BtnGeneral_Click(object sender, RoutedEventArgs e) => LoadGeneralPage();
    private void BtnColorPicker_Click(object sender, RoutedEventArgs e) => LoadColorPickerPage();
    private void BtnTextTools_Click(object sender, RoutedEventArgs e) => LoadTextToolsPage();
    private void BtnSystemInfo_Click(object sender, RoutedEventArgs e) => LoadSystemInfoPage();

    private void LoadGeneralPage()
    {
        ContentPanel.Children.Clear();
        
        var title = new TextBlock { Text = "General Settings", FontSize = 24, FontWeight = FontWeights.Bold, Margin = new Thickness(0, 0, 0, 20) };
        ContentPanel.Children.Add(title);

        var desc = new TextBlock { Text = "Configure general application settings", FontSize = 14, Foreground = new SolidColorBrush(Color.FromRgb(100, 100, 100)), Margin = new Thickness(0, 0, 0, 30) };
        ContentPanel.Children.Add(desc);

        AddToggleSetting("Run at startup", false);
        AddToggleSetting("Show notifications", true);
    }

    private void LoadColorPickerPage()
    {
        ContentPanel.Children.Clear();
        
        var title = new TextBlock { Text = "Color Picker", FontSize = 24, FontWeight = FontWeights.Bold, Margin = new Thickness(0, 0, 0, 20) };
        ContentPanel.Children.Add(title);

        var btn = new Button { Content = "Pick Color", Width = 120, Height = 35, Margin = new Thickness(0, 10, 0, 0) };
        btn.Click += (s, e) => MessageBox.Show("Color picker feature - Add your implementation here!");
        ContentPanel.Children.Add(btn);
    }

    private void LoadTextToolsPage()
    {
        ContentPanel.Children.Clear();
        
        var title = new TextBlock { Text = "Text Tools", FontSize = 24, FontWeight = FontWeights.Bold, Margin = new Thickness(0, 0, 0, 20) };
        ContentPanel.Children.Add(title);

        var input = new TextBox { Width = 400, Height = 100, TextWrapping = TextWrapping.Wrap, AcceptsReturn = true, Margin = new Thickness(0, 10, 0, 10) };
        ContentPanel.Children.Add(input);

        var btnUpper = new Button { Content = "To Uppercase", Width = 120, Height = 35, Margin = new Thickness(0, 5, 0, 5) };
        btnUpper.Click += (s, e) => input.Text = input.Text.ToUpper();
        ContentPanel.Children.Add(btnUpper);

        var btnLower = new Button { Content = "To Lowercase", Width = 120, Height = 35, Margin = new Thickness(0, 5, 0, 5) };
        btnLower.Click += (s, e) => input.Text = input.Text.ToLower();
        ContentPanel.Children.Add(btnLower);
    }

    private void LoadSystemInfoPage()
    {
        ContentPanel.Children.Clear();
        
        var title = new TextBlock { Text = "System Information", FontSize = 24, FontWeight = FontWeights.Bold, Margin = new Thickness(0, 0, 0, 20) };
        ContentPanel.Children.Add(title);

        AddInfoRow("OS", Environment.OSVersion.ToString());
        AddInfoRow("Machine Name", Environment.MachineName);
        AddInfoRow("User", Environment.UserName);
        AddInfoRow(".NET Version", Environment.Version.ToString());
    }

    private void AddToggleSetting(string label, bool defaultValue)
    {
        var panel = new StackPanel { Orientation = Orientation.Horizontal, Margin = new Thickness(0, 0, 0, 15) };
        var text = new TextBlock { Text = label, FontSize = 14, VerticalAlignment = VerticalAlignment.Center, Width = 200 };
        var toggle = new CheckBox { IsChecked = defaultValue, VerticalAlignment = VerticalAlignment.Center };
        
        panel.Children.Add(text);
        panel.Children.Add(toggle);
        ContentPanel.Children.Add(panel);
    }

    private void AddInfoRow(string label, string value)
    {
        var panel = new StackPanel { Margin = new Thickness(0, 0, 0, 10) };
        var labelText = new TextBlock { Text = label, FontSize = 12, Foreground = new SolidColorBrush(Color.FromRgb(100, 100, 100)) };
        var valueText = new TextBlock { Text = value, FontSize = 14, FontWeight = FontWeights.SemiBold };
        
        panel.Children.Add(labelText);
        panel.Children.Add(valueText);
        ContentPanel.Children.Add(panel);
    }
}
