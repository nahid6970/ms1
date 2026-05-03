using System;
using System.Collections.Generic;
using System.Runtime.InteropServices;
using System.Threading;

[ComImport, Guid("EAB22AC1-30C1-11CF-A7EB-0000C05BAE0B"), InterfaceType(ComInterfaceType.InterfaceIsIDispatch)]
interface IWebBrowser2
{
    void GoBack(); void GoForward(); void GoHome(); void GoSearch();
    void Navigate(string url); void Refresh(); void Refresh2(ref object level); void Stop();
    object Application { get; } object Parent { get; } object Container { get; } object Document { get; }
    bool TopLevelContainer { get; } string Type { get; }
    int Left { get; set; } int Top { get; set; } int Width { get; set; } int Height { get; set; }
    string LocationName { get; } string LocationURL { get; } bool Busy { get; }
    void Quit();
    void ClientToWindow(ref int pcx, ref int pcy);
    void PutProperty(string property, object vtValue); object GetProperty(string property);
    string Name { get; } int HWND { get; } string FullName { get; } string Path { get; }
    bool Visible { get; set; } bool StatusBar { get; set; } string StatusText { get; set; }
    int ToolBar { get; set; } bool MenuBar { get; set; } bool FullScreen { get; set; }
    void Navigate2(ref object url, ref object flags, ref object targetFrameName, ref object postData, ref object headers);
}

class Program
{
    delegate void WinEventProc(IntPtr hWinEventHook, uint eventType, IntPtr hwnd,
        int idObject, int idChild, uint dwEventThread, uint dwmsEventTime);
    delegate bool EnumWindowsProc(IntPtr hwnd, IntPtr lParam);

    [DllImport("user32.dll")] static extern IntPtr SetWinEventHook(uint eventMin, uint eventMax, IntPtr hmodWinEventProc, WinEventProc lpfnWinEventProc, uint idProcess, uint idThread, uint dwFlags);
    [DllImport("user32.dll")] static extern bool UnhookWinEvent(IntPtr hWinEventHook);
    [DllImport("user32.dll")] static extern int GetMessage(out MSG lpMsg, IntPtr hWnd, uint wMsgFilterMin, uint wMsgFilterMax);
    [DllImport("user32.dll")] static extern bool TranslateMessage(ref MSG lpMsg);
    [DllImport("user32.dll")] static extern IntPtr DispatchMessage(ref MSG lpMsg);
    [DllImport("user32.dll")] static extern int GetClassName(IntPtr hWnd, System.Text.StringBuilder lpClassName, int nMaxCount);
    [DllImport("user32.dll")] static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
    [DllImport("user32.dll")] static extern bool SetForegroundWindow(IntPtr hWnd);
    [DllImport("user32.dll")] static extern bool IsWindow(IntPtr hWnd);
    [DllImport("user32.dll")] static extern bool EnumChildWindows(IntPtr hWndParent, EnumWindowsProc lpEnumFunc, IntPtr lParam);
    [DllImport("user32.dll")] static extern bool EnumWindows(EnumWindowsProc lpEnumFunc, IntPtr lParam);
    [DllImport("user32.dll")] static extern bool IsWindowVisible(IntPtr hWnd);
    [DllImport("user32.dll")] static extern IntPtr SendMessage(IntPtr hWnd, uint Msg, IntPtr wParam, IntPtr lParam);

    [StructLayout(LayoutKind.Sequential)]
    struct MSG { public IntPtr hwnd; public uint message; public IntPtr wParam; public IntPtr lParam; public uint time; public int x, y; }

    const uint EVENT_OBJECT_CREATE   = 0x8000;
    const uint EVENT_OBJECT_SHOW     = 0x8002;
    const uint WINEVENT_OUTOFCONTEXT = 0x0000;
    const int  SW_HIDE    = 0;
    const int  SW_RESTORE = 9;
    const uint WM_COMMAND = 0x0111;
    const int  NEW_TAB_CMD = 0xA21B;

    static readonly HashSet<IntPtr> _knownHwnds = [];
    static readonly object _lock = new();

    static string GetClass(IntPtr hwnd)
    {
        var sb = new System.Text.StringBuilder(256);
        GetClassName(hwnd, sb, sb.Capacity);
        return sb.ToString();
    }

    static IntPtr FindFirstChild(IntPtr parent, string className)
    {
        IntPtr found = IntPtr.Zero;
        EnumChildWindows(parent, (hwnd, _) =>
        {
            if (GetClass(hwnd) == className) { found = hwnd; return false; }
            return true;
        }, IntPtr.Zero);
        return found;
    }

    static HashSet<IntPtr> GetCabinetHwnds()
    {
        var set = new HashSet<IntPtr>();
        EnumWindows((hwnd, _) =>
        {
            if (IsWindowVisible(hwnd) && GetClass(hwnd) == "CabinetWClass") set.Add(hwnd);
            return true;
        }, IntPtr.Zero);
        return set;
    }

    static dynamic? GetShellApp()
    {
        try { return Activator.CreateInstance(Type.GetTypeFromProgID("Shell.Application")!); }
        catch { return null; }
    }

    static IWebBrowser2? FindBlankTab(IntPtr cabinetHwnd)
    {
        var shell = GetShellApp();
        if (shell == null) return null;
        try
        {
            var windows = shell.Windows();
            for (int i = 0; i < (int)windows.Count; i++)
            {
                try
                {
                    var item = windows.Item(i) as IWebBrowser2;
                    if (item != null && (IntPtr)item.HWND == cabinetHwnd && string.IsNullOrEmpty(item.LocationURL))
                        return item;
                }
                catch { }
            }
        }
        catch { }
        return null;
    }

    static string? GetPathForHwnd(IntPtr hwnd)
    {
        var shell = GetShellApp();
        if (shell == null) return null;
        try
        {
            var windows = shell.Windows();
            for (int i = 0; i < (int)windows.Count; i++)
            {
                try
                {
                    var item = windows.Item(i) as IWebBrowser2;
                    if (item != null && (IntPtr)item.HWND == hwnd && !string.IsNullOrEmpty(item.LocationURL))
                        return Uri.UnescapeDataString(item.LocationURL.Replace("file:///", "").Replace("/", "\\"));
                }
                catch { }
            }
        }
        catch { }
        return null;
    }

    static void CloseShellWindow(IntPtr hwnd)
    {
        var shell = GetShellApp();
        if (shell == null) return;
        try
        {
            var windows = shell.Windows();
            for (int i = 0; i < (int)windows.Count; i++)
            {
                try
                {
                    var item = windows.Item(i) as IWebBrowser2;
                    if (item != null && (IntPtr)item.HWND == hwnd) { item.Quit(); return; }
                }
                catch { }
            }
        }
        catch { }
    }

    static bool OpenAsTab(IntPtr targetHwnd, string path)
    {
        IntPtr tabHwnd = FindFirstChild(targetHwnd, "ShellTabWindowClass");
        if (tabHwnd == IntPtr.Zero) return false;

        SendMessage(tabHwnd, WM_COMMAND, (IntPtr)NEW_TAB_CMD, IntPtr.Zero);
        Thread.Sleep(500);

        var blank = FindBlankTab(targetHwnd);
        if (blank == null) return false;

        object url = path, missing = Type.Missing;
        blank.Navigate2(ref url, ref missing, ref missing, ref missing, ref missing);
        return true;
    }

    static void HandleNewWindow(IntPtr hwnd)
    {
        // Retry until Shell COM registers the new window (up to 2s)
        string? path = null;
        for (int i = 0; i < 8; i++)
        {
            Thread.Sleep(250);
            if (!IsWindow(hwnd)) return;
            path = GetPathForHwnd(hwnd);
            if (path != null) break;
        }

        var existing = GetCabinetHwnds();
        existing.Remove(hwnd);
        lock (_lock) existing.IntersectWith(_knownHwnds);

        if (existing.Count == 0 || path == null)
        {
            ShowWindow(hwnd, SW_RESTORE);
            lock (_lock) _knownHwnds.Add(hwnd);
            return;
        }

        IntPtr target = System.Linq.Enumerable.First(existing);

        if (OpenAsTab(target, path))
        {
            Thread.Sleep(300);
            CloseShellWindow(hwnd);
            ShowWindow(target, SW_RESTORE);
            SetForegroundWindow(target);
        }
        else
        {
            ShowWindow(hwnd, SW_RESTORE);
            lock (_lock) _knownHwnds.Add(hwnd);
        }
    }

    static void Main()
    {
        foreach (var h in GetCabinetHwnds())
            _knownHwnds.Add(h);

        WinEventProc callback = (hook, evt, hwnd, idObj, idChild, thread, time) =>
        {
            if (hwnd == IntPtr.Zero || idObj != 0 || GetClass(hwnd) != "CabinetWClass") return;
            bool isNew;
            lock (_lock) isNew = _knownHwnds.Add(hwnd);
            if (isNew)
            {
                // Hide immediately in the callback (message pump thread) before Explorer paints it
                ShowWindow(hwnd, SW_HIDE);
                var t = new Thread(() => HandleNewWindow(hwnd));
                t.SetApartmentState(ApartmentState.STA);
                t.Start();
            }
        };

        // Hook both CREATE and SHOW to catch the window as early as possible
        var hook1 = SetWinEventHook(EVENT_OBJECT_CREATE, EVENT_OBJECT_SHOW,
            IntPtr.Zero, callback, 0, 0, WINEVENT_OUTOFCONTEXT);

        while (GetMessage(out MSG msg, IntPtr.Zero, 0, 0) > 0)
        {
            TranslateMessage(ref msg);
            DispatchMessage(ref msg);
        }

        UnhookWinEvent(hook1);
    }
}
