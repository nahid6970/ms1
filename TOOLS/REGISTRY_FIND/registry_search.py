import winreg
import sys

def search_registry(search_term, hive=winreg.HKEY_LOCAL_MACHINE, path=""):
    results = []
    try:
        key = winreg.OpenKey(hive, path, 0, winreg.KEY_READ)
        i = 0
        while True:
            try:
                subkey_name = winreg.EnumKey(key, i)
                subkey_path = f"{path}\\{subkey_name}" if path else subkey_name
                
                if search_term.lower() in subkey_name.lower():
                    results.append(f"KEY: {hive_name(hive)}\\{subkey_path}")
                
                results.extend(search_registry(search_term, hive, subkey_path))
                i += 1
            except OSError:
                break
        
        j = 0
        while True:
            try:
                value_name, value_data, _ = winreg.EnumValue(key, j)
                if search_term.lower() in str(value_name).lower() or search_term.lower() in str(value_data).lower():
                    results.append(f"VALUE: {hive_name(hive)}\\{path}\\{value_name}")
                j += 1
            except OSError:
                break
        
        winreg.CloseKey(key)
    except:
        pass
    
    return results

def hive_name(hive):
    names = {
        winreg.HKEY_LOCAL_MACHINE: "HKEY_LOCAL_MACHINE",
        winreg.HKEY_CURRENT_USER: "HKEY_CURRENT_USER",
        winreg.HKEY_CLASSES_ROOT: "HKEY_CLASSES_ROOT",
        winreg.HKEY_USERS: "HKEY_USERS",
        winreg.HKEY_CURRENT_CONFIG: "HKEY_CURRENT_CONFIG"
    }
    return names.get(hive, "UNKNOWN")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python registry_search.py <search_term>")
        sys.exit(1)
    
    search_term = sys.argv[1]
    print(f"Searching for: {search_term}\n")
    
    hives = [
        winreg.HKEY_CURRENT_USER,
        winreg.HKEY_LOCAL_MACHINE,
        winreg.HKEY_CLASSES_ROOT
    ]
    
    for hive in hives:
        print(f"Searching {hive_name(hive)}...")
        results = search_registry(search_term, hive)
        for result in results:
            print(result)
    
    print("\nSearch complete.")
