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
    [DllImport("user32.dll")] static extern int GetWindowLong(IntPtr hWnd, int nIndex);
    [DllImport("user32.dll")] static extern int SetWindowLong(IntPtr hWnd, int nIndex, int dwNewLong);
    [DllImport("user32.dll")] static extern bool SetLayeredWindowAttributes(IntPtr hWnd, uint crKey, byte bAlpha, uint dwFlags);
    [DllImport("user32.dll", CharSet = CharSet.Unicode)] static extern int GetWindowTextW(IntPtr hWnd, System.Text.StringBuilder lpString, int nMaxCount);
    [DllImport("user32.dll")] static extern IntPtr SendMessage(IntPtr hWnd, uint Msg, IntPtr wParam, IntPtr lParam);

    [StructLayout(LayoutKind.Sequential)]
    struct MSG { public IntPtr hwnd; public uint message; public IntPtr wParam; public IntPtr lParam; public uint time; public int x, y; }

    const uint EVENT_OBJECT_CREATE   = 0x8000;
    const uint EVENT_OBJECT_SHOW     = 0x8002;
    const uint WINEVENT_OUTOFCONTEXT = 0x0000;
    const int  SW_HIDE    = 0;
    const int  SW_RESTORE = 9;
    const int  GWL_EXSTYLE    = -20;
    const int  WS_EX_LAYERED  = 0x80000;
    const uint LWA_ALPHA      = 0x2;
    const uint WM_COMMAND = 0x0111;
    const int  NEW_TAB_CMD = 0xA21B;

    static readonly HashSet<IntPtr> _knownHwnds = [];
    static readonly object _lock = new();

    // Make window fully transparent (invisible but still exists for COM)
    static void MakeInvisible(IntPtr hwnd)
    {
        int exStyle = GetWindowLong(hwnd, GWL_EXSTYLE);
        SetWindowLong(hwnd, GWL_EXSTYLE, exStyle | WS_EX_LAYERED);
        SetLayeredWindowAttributes(hwnd, 0, 0, LWA_ALPHA);
    }

    static string GetWindowText(IntPtr hwnd)
    {
        var sb = new System.Text.StringBuilder(512);
        GetWindowTextW(hwnd, sb, sb.Capacity);
        return sb.ToString();
    }

    // Wait until ShellTabWindowClass child has a real title (folder loaded)
    static bool WaitForTabTitle(IntPtr hwnd, int timeoutMs = 2000)
    {
        int elapsed = 0;
        while (elapsed < timeoutMs)
        {
            Thread.Sleep(50);
            elapsed += 50;
            if (!IsWindow(hwnd)) return false;
            IntPtr tabHwnd = FindFirstChild(hwnd, "ShellTabWindowClass");
            if (tabHwnd == IntPtr.Zero) continue;
            string title = GetWindowText(tabHwnd);
            if (!string.IsNullOrEmpty(title) && title != "File Explorer") return true;
        }
        return false;
    }

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
        // Wait for folder to load (tab title changes from "File Explorer" to folder name)
        if (!WaitForTabTitle(hwnd)) return;
        if (!IsWindow(hwnd)) return;

        string? path = GetPathForHwnd(hwnd);

        var existing = GetCabinetHwnds();
        existing.Remove(hwnd);
        lock (_lock) existing.IntersectWith(_knownHwnds);

        if (existing.Count == 0 || path == null)
        {
            // Restore visibility: remove layered style then show
            int exStyle = GetWindowLong(hwnd, GWL_EXSTYLE);
            SetWindowLong(hwnd, GWL_EXSTYLE, exStyle & ~WS_EX_LAYERED);
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
            int exStyle = GetWindowLong(hwnd, GWL_EXSTYLE);
            SetWindowLong(hwnd, GWL_EXSTYLE, exStyle & ~WS_EX_LAYERED);
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
                // Make fully transparent immediately in the callback before Explorer paints it
                MakeInvisible(hwnd);
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
