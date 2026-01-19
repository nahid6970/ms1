using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Text;

namespace simple_csharp_project
{
    public static class PowerShellRunner
    {
        // Helper to encode string to Base64
        private static string EncodeToBase64(string toEncode)
        {
            byte[] toEncodeAsBytes = Encoding.Unicode.GetBytes(toEncode);
            return Convert.ToBase64String(toEncodeAsBytes);
        }

        public static void Execute(string shell, string command, bool asAdmin)
        {
            string encodedCommand = EncodeToBase64(command);

            if (asAdmin)
            {
                RunInNewWindow(shell, encodedCommand);
            }
            else
            {
                RunInline(shell, encodedCommand);
            }
        }

        private static void RunInNewWindow(string shell, string encodedCommand)
        {
            try
            {
                var process = new Process
                {
                    StartInfo = new ProcessStartInfo
                    {
                        FileName = shell,
                        Arguments = @$"-NoExit -EncodedCommand {encodedCommand}",
                        Verb = "runas",
                        UseShellExecute = true
                    }
                };
                Console.Clear();
                Console.WriteLine("Attempting to run command with administrator privileges in a new window...");
                process.Start();
                process.WaitForExit();
            }
            catch (Exception ex)
            {
                Console.Clear();
                Console.WriteLine($"Error trying to run elevated command: {ex.Message}");
                Console.WriteLine("\nPress any key to return to the menu...");
                Console.ReadKey();
            }
        }

        private static void RunInline(string shell, string encodedCommand)
        {
            var process = new Process
            {
                StartInfo = new ProcessStartInfo
                {
                    FileName = shell,
                    Arguments = $"-EncodedCommand {encodedCommand}",
                    RedirectStandardOutput = true,
                    RedirectStandardError = true,
                    UseShellExecute = false,
                    CreateNoWindow = true
                }
            };

            Console.Clear();
            Console.WriteLine("Running command...");
            Console.WriteLine("--------------------------------------------------");
            process.Start();
            Console.Write(process.StandardOutput.ReadToEnd());
            Console.ForegroundColor = ConsoleColor.Red;
            Console.Write(process.StandardError.ReadToEnd());
            Console.ResetColor();
            Console.WriteLine("--------------------------------------------------");
            Console.WriteLine("Command finished. Press any key to return to the menu.");
            Console.ReadKey();
        }
    }

    public class MenuItem
    {
        public string Title { get; }
        public Action Action { get; }
        public MenuItem(string title, Action action) { Title = title; Action = action; }
    }

    public class MainMenuCategory
    {
        public string Title { get; }
        public List<MenuItem> SubMenuItems { get; }
        public MainMenuCategory(string title, List<MenuItem> subMenuItems) { Title = title; SubMenuItems = subMenuItems; }
    }

    public class TwoPaneMenu
    {
        private readonly List<MainMenuCategory> _categories;
        private int _mainIndex = 0;
        private int _subIndex = 0;
        private bool _isSubMenuFocused = false;

        public TwoPaneMenu(List<MainMenuCategory> categories) { _categories = categories; }

        public void Run()
        {
            try { Console.CursorVisible = false; } catch { /* Ignore */ }
            while (true)
            {
                DrawLayout();
                HandleInput();
            }
        }

        private void DrawLayout()
        {
            try { Console.Clear(); } catch { /* Ignore */ }
            DrawMenuPane(1, "Main Menu", _categories.Select(c => c.Title).ToList(), _mainIndex, !_isSubMenuFocused);
            var currentCategory = _categories[_mainIndex];
            DrawMenuPane(40, currentCategory.Title, currentCategory.SubMenuItems.Select(i => i.Title).ToList(), _subIndex, _isSubMenuFocused);
        }

        private void DrawMenuPane(int left, string title, List<string> items, int selectedIndex, bool isFocused)
        {
            Console.SetCursorPosition(left, 1);
            Console.ForegroundColor = isFocused ? ConsoleColor.Cyan : ConsoleColor.White;
            Console.WriteLine($"===== {title} =====");
            Console.ResetColor();

            if (!items.Any())
            {
                Console.SetCursorPosition(left, 3);
                Console.ForegroundColor = ConsoleColor.DarkGray;
                Console.WriteLine("(No options here)");
                Console.ResetColor();
            }

            for (int i = 0; i < items.Count; i++)
            {
                Console.SetCursorPosition(left, 3 + i);
                if (isFocused && i == selectedIndex)
                {
                    Console.BackgroundColor = ConsoleColor.Gray;
                    Console.ForegroundColor = ConsoleColor.Black;
                    Console.Write(">> ");
                }
                else
                {
                    Console.Write("   ");
                }
                Console.WriteLine(items[i]);
                Console.ResetColor();
            }
        }

        private void HandleInput()
        {
            ConsoleKeyInfo keyInfo;
            try { keyInfo = Console.ReadKey(true); } catch { return; }

            var currentSubMenuItems = _categories[_mainIndex].SubMenuItems;

            switch (keyInfo.Key)
            {
                case ConsoleKey.UpArrow:
                    if (_isSubMenuFocused) _subIndex = (_subIndex > 0) ? _subIndex - 1 : Math.Max(0, currentSubMenuItems.Count - 1);
                    else _mainIndex = (_mainIndex > 0) ? _mainIndex - 1 : _categories.Count - 1;
                    break;
                case ConsoleKey.DownArrow:
                    if (_isSubMenuFocused) _subIndex = (_subIndex < currentSubMenuItems.Count - 1) ? _subIndex + 1 : 0;
                    else _mainIndex = (_mainIndex < _categories.Count - 1) ? _mainIndex + 1 : 0;
                    break;
                case ConsoleKey.Enter:
                    if (_isSubMenuFocused && currentSubMenuItems.Any())
                    {
                        currentSubMenuItems[_subIndex].Action?.Invoke();
                    }
                    else if (currentSubMenuItems.Any())
                    {
                        _isSubMenuFocused = true;
                        _subIndex = 0;
                    }
                    break;
                case ConsoleKey.Backspace: case ConsoleKey.Escape: case ConsoleKey.LeftArrow:
                    _isSubMenuFocused = false;
                    break;
                case ConsoleKey.RightArrow:
                    if (currentSubMenuItems.Any()) _isSubMenuFocused = true;
                    break;
            }
        }
    }

    public class Program
    {
        public static void Main(string[] args)
        {
            var menuCategories = new List<MainMenuCategory>
            {
                new MainMenuCategory("Initial Setup", new List<MenuItem>
                {
                    new MenuItem("PKG Manager & Must Apps", () => PowerShellRunner.Execute("powershell.exe", "if (-not (Get-Command scoop -ErrorAction SilentlyContinue)) { Invoke-Expression (New-Object Net.WebClient).DownloadString('https://get.scoop.sh') } else { Write-Host 'Scoop is already installed.' -ForegroundColor Yellow }; scoop config cache_path D:\\@install\\scoop\\cache; scoop install git; scoop bucket add nonportable; scoop bucket add extras; scoop bucket add versions; scoop bucket add games; scoop install sudo python312 oh-my-posh fzf komorebi rclone ditto text-grab yt-dlp ffmpeg highlight zoxide; winget upgrade --source msstore; winget upgrade --source winget; winget upgrade --all; winget export C:\\Users\\nahid\\OneDrive\\backup\\installed_apps\\list_winget.txt | Out-File -FilePath C:\\Users\\nahid\\OneDrive\\backup\\installed_apps\\ex_wingetlist.txt; winget install Microsoft.PowerShell; winget install Notepad++.Notepad++; winget install 9NQ8Q8J78637;", false)),
                    new MenuItem("Policies", () => PowerShellRunner.Execute("powershell.exe", "Set-ExecutionPolicy RemoteSigned -Scope CurrentUser; Set-ExecutionPolicy RemoteSigned; Install-Module -Name Microsoft.WinGet.Client -Force -AllowClobber", false)),
                    new MenuItem("Install Scoop Packages", () => PowerShellRunner.Execute("powershell.exe", "scoop install ack adb bat capture2text ditto ffmpeg highlight kitty neovim putty rssguard rufus ventoy winaero-tweaker yt-dlp", false)),
                    new MenuItem("Install Pwsh Modules", () => PowerShellRunner.Execute("pwsh.exe", "Install-Module -Name BurntToast -Scope CurrentUser", true)),
                    new MenuItem("Font Setup", () => PowerShellRunner.Execute("powershell.exe", "oh-my-posh font install", true)),
                    new MenuItem("pip Packages", () => PowerShellRunner.Execute("pwsh.exe", "$su = 'C:\\Users\\nahid\\scoop\\shims\\sudo.ps1'; & $su C:\\Users\\nahid\\scoop\\apps\\python312\\current\\python.exe -m pip install -r C:\\@delta\\ms1\\asset\\pip\\pip_required.txt", false)),
                    new MenuItem("Update Packages", () => PowerShellRunner.Execute("pwsh.exe", "scoop status; scoop update; scoop update *; scoop export | Out-File -FilePath C:\\Users\\nahid\\OneDrive\\backup\\installed_apps\\list_scoop.txt; scoop cleanup *; winget upgrade --all; winget export C:\\Users\\nahid\\OneDrive\\backup\\installed_apps\\list_winget.txt | Out-File -FilePath C:\\Users\\nahid\\OneDrive\\backup\\installed_apps\\ex_wingetlist.txt", false))
                }),
                new MainMenuCategory("Application Setup", new List<MenuItem>
                {
                    new MenuItem("jackett + qbittorrent", () => PowerShellRunner.Execute("powershell.exe", "Write-Host 'Step 1: open qbittorrent -> view -> search engine -> Go To search engine tab -> search plugin -> check for updates'; Write-Host 'Step 2: Start Jackett and add the necessary indexes'; Write-Host 'Step 3: Copy jacket api from webui to jackett.json'; Start-Process 'C:\\Users\\nahid\\AppData\\Local\\qBittorrent\\nova3\\engines'", false)),
                    new MenuItem("Ldplayer", () => PowerShellRunner.Execute("powershell.exe", "Remove-Item 'C:\\Users\\nahid\\AppData\\Roaming\\XuanZhi9\\cache\\*' -Recurse; New-NetFirewallRule -DisplayName '@Block_Ld9BoxHeadless_OutInbound' -Direction Outbound -Program 'C:\\LDPlayer\\LDPlayer9\\dnplayer.exe' -Action Block -Enabled True", true)),
                    new MenuItem(
                        "Neovim_1.conf",
                        () => PowerShellRunner.Execute(
                            "pwsh.exe",
                            @"
                                Remove-Item -Force -Recurse -Verbose C:\Users\nahid\AppData\Local\nvim;
                                Remove-Item -Force -Recurse -Verbose C:\Users\nahid\AppData\Local\nvim-data;
                                New-Item -ItemType SymbolicLink `
                                        -Path C:\Users\nahid\AppData\Local\nvim\init.lua `
                                        -Target C:\@delta\ms1\asset\linux\neovim\init.lua `
                                        -Force
                            ",
                            true
                        )
                    ),
                    new MenuItem("Neovim_2.conf", () => PowerShellRunner.Execute("pwsh.exe", "Remove-Item -Force -Recurse -Verbose C:\\Users\\nahid\\AppData\\Local\\nvim; Remove-Item -Force -Recurse -Verbose C:\\Users\\nahid\\AppData\\Local\\nvim-data; New-Item -ItemType SymbolicLink -Path C:\\Users\\nahid\\AppData\\Local\\nvim\\init.lua -Target C:\\@delta\\ms1\\asset\\linux\\neovim\\init2.lua -Force", false)),
                    new MenuItem("Notepad++ Theme Setup", () => PowerShellRunner.Execute("powershell.exe", "cd C:\\Users\\nahid; git clone https://github.com/dracula/notepad-plus-plus.git; Start-Process \"C:\\Users\\nahid\\notepad-plus-plus\"; Start-Process \"$env:AppData\\Notepad++\\themes\"; Write-Host 'Copy Dracula.xml to the themes folder and restart Notepad++'", false)),
                    new MenuItem("PotPlayer Register", () => PowerShellRunner.Execute("pwsh.exe", "Start-Process 'C:\\@delta\\ms1\\asset\\potplayer\\PotPlayerMini64.reg' -Verbose", false))
                }),
                new MainMenuCategory("Clone Projects", new List<MenuItem>
                {
                    new MenuItem("clone ms1", () => PowerShellRunner.Execute("powershell.exe", "cd c:\\; git clone https://github.com/nahid6970/ms1", false)),
                    new MenuItem("clone ms2", () => PowerShellRunner.Execute("powershell.exe", "cd c:\\; git clone https://github.com/nahid6970/ms2", false)),
                    new MenuItem("clone ms3", () => PowerShellRunner.Execute("powershell.exe", "cd c:\\; git clone https://github.com/nahid6970/ms3", false))
                }),
                new MainMenuCategory("Backup & Restore", new List<MenuItem>
                {
                    new MenuItem("decrypt rclone.conf & move", () => PowerShellRunner.Execute("powershell.exe", "Write-Host 'Not Implemented'", false)),
                    new MenuItem("msBackups [rs]", () => PowerShellRunner.Execute("powershell.exe", "Write-Host 'Not Implemented'", false)),
                    new MenuItem("msBackups [bk]", () => PowerShellRunner.Execute("powershell.exe", "Write-Host 'Not Implemented'", false)),
                    new MenuItem("nilesoft nss [bk]", () => PowerShellRunner.Execute("powershell.exe", "Copy-Item -Path 'C:\\Program Files\\Nilesoft Shell\\shell.nss' -Destination 'C:\\@delta\\ms1\\asset\\nilesoft_shell\\shell.nss' -Force -Verbose; Copy-Item -Path 'C:\\Program Files\\Nilesoft Shell\\imports' -Destination 'C:\\@delta\\ms1\\asset\\nilesoft_shell\\' -Recurse -Force -Verbose", false)),
                    new MenuItem("song [rclone] [bk]", () => PowerShellRunner.Execute("pwsh.exe", "rclone sync D:/song/ gu:/song/ -P --check-first --transfers=1 --track-renames --fast-list", false))
                }),
                new MainMenuCategory("Port", new List<MenuItem>
                {
                    new MenuItem("22 [SSH]", () => PowerShellRunner.Execute("pwsh.exe", "New-NetFirewallRule -DisplayName 'Allow_Port_22' -Direction Inbound -Protocol TCP -LocalPort 22 -Action Allow -Profile Any", true)),
                    new MenuItem("5000", () => PowerShellRunner.Execute("pwsh.exe", "New-NetFirewallRule -DisplayName 'Allow_Port_5000' -Direction Inbound -Protocol TCP -LocalPort 5000 -Action Allow -Profile Any", true)),
                    new MenuItem("5001", () => PowerShellRunner.Execute("pwsh.exe", "New-NetFirewallRule -DisplayName 'Allow_Port_5001' -Direction Inbound -Protocol TCP -LocalPort 5001 -Action Allow -Profile Any", true)),
                    new MenuItem("5002", () => PowerShellRunner.Execute("pwsh.exe", "New-NetFirewallRule -DisplayName 'Allow_Port_5002' -Direction Inbound -Protocol TCP -LocalPort 5002 -Action Allow -Profile Any", true))
                }),
                new MainMenuCategory("mklink", new List<MenuItem>
                {
                    new MenuItem("Komorebi", () => PowerShellRunner.Execute("pwsh.exe", "Komorebic quickstart; Remove-Item 'C:\\Users\\nahid\\komorebi.json'; New-Item -ItemType SymbolicLink -Path 'C:\\Users\\nahid\\komorebi.json' -Target 'C:\\@delta\\ms1\\asset\\komorebi\\komorebi.json' -Force", false)),
                    new MenuItem("Reference", () => PowerShellRunner.Execute("pwsh.exe", "New-Item -ItemType SymbolicLink -Path 'C:\\Users\\nahid\\scoop\\apps\\python312\\current\\Lib\\Reference.py' -Target 'C:\\@delta\\ms1\\Reference.py' -Force", false)),
                    new MenuItem("PowerShell Profile", () => PowerShellRunner.Execute("pwsh.exe", "New-Item -ItemType SymbolicLink -Path C:\\Users\\nahid\\Documents\\PowerShell\\Microsoft.PowerShell_profile.ps1 -Target C:\\@delta\\ms1\\asset\\Powershell\\Microsoft.PowerShell_profile.ps1 -Force", false)),
                    new MenuItem("Prowlarr", () => PowerShellRunner.Execute("pwsh.exe", "Winget install TeamProwlarr.Prowlarr; Write-Host 'Manual restore required.' -ForegroundColor Yellow; Start-Process 'C:\\Users\\nahid\\ms\\msBackups\\ARR_timely'", false)),
                    new MenuItem("Radarr", () => PowerShellRunner.Execute("pwsh.exe", "Winget install TeamRadarr.Radarr; Write-Host 'Manual restore required.' -ForegroundColor Yellow; Start-Process 'C:\\Users\\nahid\\ms\\msBackups\\ARR_timely'", false)),
                    new MenuItem("RssGuard", () => PowerShellRunner.Execute("powershell.exe", "scoop install rssguard; Stop-Process -Name 'rssguard'; Remove-Item 'C:\\Users\\nahid\\scoop\\apps\\rssguard\\current\\data4\\database' -Recurse; Remove-Item 'C:\\Users\\nahid\\scoop\\apps\\rssguard\\current\\data4\\config' -Recurse; New-Item -ItemType SymbolicLink -Path 'C:\\Users\\nahid\\scoop\\apps\\rssguard\\current\\data4\\config' -Target 'C:\\Users\\nahid\\ms\\msBackups\\@mklink\\rssguard\\config' -Force; New-Item -ItemType SymbolicLink -Path 'C:\\Users\\nahid\\scoop\\apps\\rssguard\\current\\data4\\database' -Target 'C:\\Users\\nahid\\ms\\msBackups\\@mklink\\rssguard\\database' -Force", true)),
                    new MenuItem("Sonarr", () => PowerShellRunner.Execute("pwsh.exe", "Winget install TeamSonarr.Sonarr; Write-Host 'Manual restore required.' -ForegroundColor Yellow; Start-Process 'C:\\Users\\nahid\\ms\\msBackups\\ARR_timely'", false)),
                    new MenuItem("Terminal Profile", () => PowerShellRunner.Execute("pwsh.exe", "New-Item -ItemType SymbolicLink -Path C:\\Users\\nahid\\AppData\\Local\\Packages\\Microsoft.WindowsTerminal_8wekyb3d8bbwe\\LocalState\\settings.json -Target C:\\@delta\\ms1\\asset\\terminal\\settings.json -Force", false)),
                    new MenuItem("VSCode", () => PowerShellRunner.Execute("pwsh.exe", "New-Item -ItemType SymbolicLink -Path C:\\Users\\nahid\\AppData\\Roaming\\Code\\User\\keybindings.json -Target C:\\@delta\\ms1\\asset\\vscode\\keybindings.json -Force; New-Item -ItemType SymbolicLink -Path C:\\Users\\nahid\\AppData\\Roaming\\Code\\User\\settings.json -Target C:\\@delta\\ms1\\asset\\vscode\\settings.json -Force", false))
                }),
                new MainMenuCategory("Github Projects", new List<MenuItem>
                {
                    new MenuItem("Microsoft Activation Scripts (MAS)", () => PowerShellRunner.Execute("powershell.exe", "irm https://get.activated.win | iex", true)),
                    new MenuItem("ChrisTitus WinUtility", () => PowerShellRunner.Execute("powershell.exe", "iwr -useb https://christitus.com/win | iex", true)),
                    new MenuItem("WIMUtil", () => PowerShellRunner.Execute("powershell.exe", "irm 'https://github.com/memstechtips/WIMUtil/raw/main/src/WIMUtil.ps1' | iex", true)),
                    new MenuItem("AppControl Manager", () => PowerShellRunner.Execute("pwsh.exe", "(irm 'https://raw.githubusercontent.com/HotCakeX/Harden-Windows-Security/main/Harden-Windows-Security.ps1')+'AppControl'|iex", true)),
                    new MenuItem("Harden Windows Security Using GUI", () => PowerShellRunner.Execute("powershell.exe", "(irm 'https://raw.githubusercontent.com/HotCakeX/Harden-Windows-Security/main/Harden-Windows-Security.ps1')+'P'|iex", true)),
                    new MenuItem("Winhance", () => PowerShellRunner.Execute("powershell.exe", "irm 'https://github.com/memstechtips/Winhance/raw/main/Winhance.ps1' | iex", true))
                })
            };

            var menu = new TwoPaneMenu(menuCategories);
            menu.Run();
        }
    }
}