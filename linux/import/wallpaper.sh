wallpaper(){
    # Step 1: Define wallpaper directory and path
    WALLPAPER_DIR="$HOME/Pictures/wallpapers"
    mkdir -p "$WALLPAPER_DIR"
    WALLPAPER_PATH="$WALLPAPER_DIR/wallpaper1.jpg"
    
    # Step 2: Download wallpaper
    echo -e "🌐 Downloading wallpaper..."
    curl -L -o "$WALLPAPER_PATH" "https://www.skyweaver.net/images/media/wallpapers/wallpaper1.jpg"
    echo 'Downloading WallPaper Complete'
}