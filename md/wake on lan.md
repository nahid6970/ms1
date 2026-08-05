# How to Configure Windows 11 PC for Wake on LAN (WoL)

Follow these steps on your Windows 11 PC to enable remote wake-up capabilities over your local network.

---

## Prerequisites
* Ensure your PC is connected to your local network using a **wired Ethernet connection** (Wake on LAN generally requires a wired connection).

---

## Step 1: Configure Network Adapter Power Settings

1. Open **Device Manager** on Windows 11.
2. Expand **Network adapters**, right-click your network card (or USB network adapter), and select **Properties**.
3. Click the **Power Management** tab.
4. Check the box: **"Allow the computer to turn off this device to save power"**.
5. Check the box: **"Allow this device to wake the computer"**.
6. Click **OK** to save changes.

---

## Step 2: Set a Static IP Address

To ensure your Android app can reliably locate your computer, assign a static IP address to your PC:

1. Go to **Settings > Network & internet > Ethernet**.
2. Edit your **IP assignment** settings to **Manual** (IPv4).
3. Set a static IP address within your router's IP range (e.g., `192.168.10.181`).
4. Enter the appropriate Subnet Mask, Gateway, and DNS settings, then save.

---

## Step 3: Enable Ping via Windows Firewall

By default, Windows 11 blocks incoming network pings. Enable ICMP echo requests so the Android app can detect your PC status:

1. Open **Windows Defender Firewall with Advanced Security**.
2. Click on **Inbound Rules** in the left panel.
3. Scroll down and locate the following rule:
   `File and Printer Sharing (Echo Request – ICMPv4-In)`
4. Right-click the rule and select **Enable Rule**.

---

## Step 4: Enable Wake on LAN in UEFI / BIOS

1. Restart your computer and press the designated key (usually `DEL` or `F2`) during startup to enter the **UEFI / BIOS** menu.
2. Navigate to the Power Management or Advanced settings (menu locations vary by motherboard, e.g., ASUS).
3. Locate the **Wake on LAN (WoL)** or **Power On By PCI-E/LAN** option and set it to **Enabled**.
4. Save your changes and exit BIOS (usually `F10`), then boot into Windows.

---

## Step 5: Find Your PC's MAC Address

You will need your PC's MAC address to configure the Wake on LAN app on your Android phone:

1. Open **Command Prompt** (`cmd`).
2. Type `ipconfig /all` or `getmac` and press **Enter**.
3. Note down the **Physical Address (MAC Address)** of your active Ethernet adapter.