using System;
using System.Collections.Generic;
using System.Linq;

namespace simple_csharp_project
{
    // Represents a single, selectable action item in a submenu
    public class MenuItem
    {
        public string Title { get; }
        public Action Action { get; }

        public MenuItem(string title, Action action)
        {
            Title = title;
            Action = action;
        }
    }

    // Represents a top-level category in the main menu
    public class MainMenuCategory
    {
        public string Title { get; }
        public List<MenuItem> SubMenuItems { get; }

        public MainMenuCategory(string title, List<MenuItem> subMenuItems)
        {
            Title = title;
            SubMenuItems = subMenuItems;
        }
    }

    // The main class that manages and renders the two-pane menu UI
    public class TwoPaneMenu
    {
        private readonly List<MainMenuCategory> _categories;
        private int _mainIndex = 0;
        private int _subIndex = 0;
        private bool _isSubMenuFocused = false;

        public TwoPaneMenu(List<MainMenuCategory> categories)
        { 
            _categories = categories;
        }

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

            // 1. Draw the main menu on the left
            DrawMenuPane(1, "Main Menu", _categories.Select(c => c.Title).ToList(), _mainIndex, !_isSubMenuFocused);

            // 2. Draw the corresponding submenu on the right
            var currentCategory = _categories[_mainIndex];
            DrawMenuPane(35, currentCategory.Title, currentCategory.SubMenuItems.Select(i => i.Title).ToList(), _subIndex, _isSubMenuFocused);
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
                    // Draw the highlighted selection only when the pane is focused
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
                    if (_isSubMenuFocused)
                        _subIndex = (_subIndex > 0) ? _subIndex - 1 : Math.Max(0, currentSubMenuItems.Count - 1);
                    else
                        _mainIndex = (_mainIndex > 0) ? _mainIndex - 1 : _categories.Count - 1;
                    break;

                case ConsoleKey.DownArrow:
                    if (_isSubMenuFocused)
                        _subIndex = (_subIndex < currentSubMenuItems.Count - 1) ? _subIndex + 1 : 0;
                    else
                        _mainIndex = (_mainIndex < _categories.Count - 1) ? _mainIndex + 1 : 0;
                    break;

                case ConsoleKey.Enter:
                    if (_isSubMenuFocused && currentSubMenuItems.Any())
                    {
                        currentSubMenuItems[_subIndex].Action?.Invoke();
                        // Return focus to the main menu after an action
                        _isSubMenuFocused = false;
                    }
                    else if (!currentSubMenuItems.Any())
                    {
                        // If main menu item has no submenu (like Exit), execute its action directly
                        _categories[_mainIndex].SubMenuItems.FirstOrDefault()?.Action?.Invoke();
                    }
                    else
                    {
                        // Focus the submenu if it has items
                        _isSubMenuFocused = true;
                        _subIndex = 0;
                    }
                    break;

                case ConsoleKey.Backspace:
                case ConsoleKey.Escape:
                case ConsoleKey.LeftArrow:
                    _isSubMenuFocused = false;
                    break;

                case ConsoleKey.RightArrow:
                    if (currentSubMenuItems.Any())
                        _isSubMenuFocused = true;
                    break;
            }
        }
    }

    public class Program
    {
        public static void Main(string[] args)
        {
            // Define the entire menu structure
            var menuCategories = new List<MainMenuCategory>
            {
                new MainMenuCategory("System Tools", new List<MenuItem>
                {
                    new MenuItem("Show System Info", () => RunPlaceholder("Showing system info...")),
                    new MenuItem("Check Disk Space", () => RunPlaceholder("Checking disk space..."))
                }),
                new MainMenuCategory("Network Tools", new List<MenuItem>
                {
                    new MenuItem("Ping a Host", () => RunPlaceholder("Pinging a host...")),
                    new MenuItem("Check Network Config", () => RunPlaceholder("Showing network configuration..."))
                }),
                new MainMenuCategory("Exit", new List<MenuItem>
                {
                    new MenuItem("Confirm Exit", () => Environment.Exit(0))
                })
            };

            var menu = new TwoPaneMenu(menuCategories);
            menu.Run();
        }

        static void RunPlaceholder(string message)
        {
            try { Console.Clear(); } catch { /* Ignore */ }
            Console.WriteLine($"{message} (Not implemented)");
            Console.WriteLine("\nPress any key to return to the menu...");
            try { Console.ReadKey(true); } catch { /* Ignore */ }
        }
    }
}