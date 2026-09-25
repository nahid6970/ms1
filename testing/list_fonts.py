
import tkinter
import tkinter.font

def list_fonts():
    root = tkinter.Tk()
    root.withdraw()  # Hide the main window
    fonts = list(tkinter.font.families())
    fonts.sort()
    root.destroy()
    return fonts

def search_fonts(fonts, query):
    matching_fonts = [font for font in fonts if query.lower() in font.lower()]
    return matching_fonts

if __name__ == "__main__":
    all_fonts = list_fonts()
    print("Available Fonts:")
    for font in all_fonts:
        print(font)

    while True:
        search_query = input("\nEnter a search term (or 'q' to quit): ")
        if search_query.lower() == 'q':
            break

        if search_query:
            results = search_fonts(all_fonts, search_query)
            if results:
                print(f"Fonts matching '{search_query}':")
                for font in results:
                    print(font)
            else:
                print(f"No fonts found matching '{search_query}'.")
