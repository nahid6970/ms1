import System.Directory
import System.Posix.User
import System.Process
--import Control.Monad.IO.Class (liftIO)
import Graphics.UI.Gtk

main :: IO ()
main = do
  initGUI

  home <- getHomeDirectory
  user <- getEffectiveUserName
  let source = "/usr/share/applications/dtos-hub.desktop"
  let dest = home ++ "/.config/autostart/dtos-hub.desktop"
  let settings = home ++ "/.config/dtos-hub/settings.conf"

  frame1 <- frameNew
  frameSetLabel frame1 "DTOS Hub"

  frame2 <- frameNew
  frameSetLabel frame2 "Video Tutorials"

  frame3 <- frameNew
  frameSetLabel frame3 ("Change " ++ user ++ "'s Shell")

  frame4 <- frameNew
  frameSetLabel frame4 "Change Color Scheme"

-- Two windows. The 'main menu' window and the 'video tutorials' window.
  window1 <- windowNew
  windowSetPosition window1 WinPosCenter

  window2 <- windowNew
  windowSetPosition window2 WinPosCenter

  window3 <- windowNew
  windowSetPosition window3 WinPosCenter

  window4 <- windowNew
  windowSetPosition window4 WinPosCenter


  -- Settings for window 1
  set window1 [ containerBorderWidth := 10
              , windowTitle          := "DTOS Hub"
              , windowResizable      := False
              , windowDefaultWidth   := 600
              , windowDefaultHeight  := 300
              ]

  set window2 [ containerBorderWidth := 10
              , windowTitle          := "DTOS Hub: Video Tutorials"
              , windowResizable      := False
              , windowDefaultWidth   := 600
              , windowDefaultHeight  := 300
              ]

  set window3 [ containerBorderWidth := 10
              , windowTitle          := "DTOS Hub: Change Shell"
              , windowResizable      := False
              , windowDefaultWidth   := 600
              , windowDefaultHeight  := 300
              ]

  set window4 [ containerBorderWidth := 10
              , windowTitle          := "DTOS Hub: Change Color Scheme"
              , windowResizable      := False
              , windowDefaultWidth   := 600
              , windowDefaultHeight  := 300
              ]

  -- IMPORTANT! Ensures that program quits when window is destroyed.
  on window1 objectDestroy mainQuit
  on window2 objectDestroy mainQuit
  on window3 objectDestroy mainQuit
  on window4 objectDestroy mainQuit

  -- ALTERNATIVE: The following also ensure program quits on destroy.
  -- This requires importing Control.Monad.IO.Class (liftIO)
  -- window1 `on` deleteEvent $ liftIO mainQuit >> return False
  -- window2 `on` deleteEvent $ liftIO mainQuit >> return False

  -- Our windows will use the 'grid' widget
  grid1  <- gridNew  -- The grid for window 1
  gridSetColumnSpacing grid1 10
  gridSetRowSpacing grid1 10
  gridSetColumnHomogeneous grid1 True

  grid2 <- gridNew  -- The grid for window 2
  gridSetColumnSpacing grid2 10
  gridSetRowSpacing grid2 10
  gridSetColumnHomogeneous grid2 True

  grid3 <- gridNew  -- The grid for window 3
  gridSetColumnSpacing grid3 10
  gridSetRowSpacing grid3 10
  gridSetColumnHomogeneous grid3 True

  grid4 <- gridNew  -- The grid for window 4
  gridSetColumnSpacing grid4 10
  gridSetRowSpacing grid4 10
  gridSetColumnHomogeneous grid4 True

  image1 <- imageNewFromFile (home ++ "/nc/gitlab-repos/dtos-hub/image1.png")
  image2 <- imageNewFromFile (home ++ "/nc/gitlab-repos/dtos-hub/image1.png")
  image3 <- imageNewFromFile (home ++ "/nc/gitlab-repos/dtos-hub/image1.png")
  image4 <- imageNewFromFile (home ++ "/nc/gitlab-repos/dtos-hub/image1.png")

  label1  <- labelNew $ Just "Welcome to DTOS! Need help using DTOS or customizing it?"
  --widgetSetSizeRequest label1 400 50
  --labelSetLineWrap label1 True

  label2  <- labelNew $ Just "Or maybe you just want to learn more about Linux? We've got you covered."
  label3  <- labelNew $ Just "Video tutorials are organized into playlists by topic."
  label4  <- labelNew $ Just ("Change the default shell for user: " ++ user)
  label5  <- labelNew $ Just "Change the color scheme used by some programs."
  label6  <- labelNew $ Just "Affects: Xmonad, xmobar, trayer, conky, alacritty."

  -- a few empty labels for spacing.
  eLabel1  <- labelNew $ Just ""
  eLabel2  <- labelNew $ Just ""
  eLabel3  <- labelNew $ Just ""
  eLabel4  <- labelNew $ Just ""
  eLabel5  <- labelNew $ Just ""
  eLabel6  <- labelNew $ Just ""
  eLabel7  <- labelNew $ Just ""
  eLabel8  <- labelNew $ Just ""

  button1 <- buttonNewWithLabel "About DTOS"
  --widgetSetSizeRequest button1 800 30
  on button1 buttonActivated $ do
    putStrLn "User chose: About DTOS"
    callCommand "xdg-open https://distro.tube/dtos/ &"

  button2 <- buttonNewWithLabel "Knowledge Base"
  on button2 buttonActivated $ do
    putStrLn "User chose: Knowledge Base"
    callCommand "xdg-open https://distro.tube/kb/ &"

  button3 <- buttonNewWithLabel "Video Tutorials"
  on button3 buttonActivated $ do
    putStrLn "User chose: Video Tutorials"
    widgetHide window1
    widgetShowAll window2

  button4 <- buttonNewWithLabel "Contribute"
  on button4 buttonActivated $ do
    putStrLn "User chose: Donate"
    callCommand "xdg-open https://distro.tube/contribute/ &"

  button5 <- buttonNewWithLabel "Change Shell"
  on button5 buttonActivated $ do
    putStrLn "User chose: Change Shell"
    widgetHide window1
    widgetShowAll window3

  button6 <- buttonNewWithLabel "Change Color Scheme"
  on button6 buttonActivated $ do
    putStrLn "User chose: Change Color Scheme"
    widgetHide window1
    widgetShowAll window4

   -- idleAdd (putStrLn "Hi." >> return True) priorityDefaultIdle
   --widgetDestroy  window1

  button7 <- buttonNewWithLabel "Exit"
  on button7 buttonActivated $ do
    putStrLn "User chose: Exit"
    widgetDestroy  window1

  vBtn1 <- buttonNewWithLabel "Arch Linux"
  on vBtn1 buttonActivated $ do
    putStrLn "Video Tutorials: Arch Linux"
    callCommand "xdg-open https://www.youtube.com/playlist?list=PL5--8gKSku16Ncr9H_BAZSzWecjaSWlvY &"

  vBtn2 <- buttonNewWithLabel "Command Line"
  on vBtn2 buttonActivated $ do
    putStrLn "Video Tutorials: Command Line"
    callCommand "xdg-open https://www.youtube.com/playlist?list=PL5--8gKSku174EnRTbP4DzU2W80Q1vqtm &"

  vBtn3 <- buttonNewWithLabel "Customization"
  on vBtn3 buttonActivated $ do
    putStrLn "Video Tutorials: Customization"
    callCommand "xdg-open https://www.youtube.com/playlist?list=PL5--8gKSku161_sqWcKCc2USL4LcSJ_kq &"

  vBtn4 <- buttonNewWithLabel "Dmscripts"
  on vBtn4 buttonActivated $ do
    putStrLn "Video Tutorials: Dmscripts"
    callCommand "xdg-open https://www.youtube.com/playlist?list=PL5--8gKSku15ur-I5LiVnBacrKD29Lv1-"

  vBtn5 <- buttonNewWithLabel "Doom Emacs"
  on vBtn5 buttonActivated $ do
    putStrLn "Video Tutorials: Doom Emacs"
    callCommand "xdg-open https://www.youtube.com/playlist?list=PL5--8gKSku15uYCnmxWPO17Dq6hVabAB4 &"

  vBtn6 <- buttonNewWithLabel "FOSS Games"
  on vBtn6 buttonActivated $ do
    putStrLn "Video Tutorials: FOSS Games"
    callCommand "xdg-open https://www.youtube.com/playlist?list=PL5--8gKSku15eRaNDc1kFgHVQOgzKjife"

  vBtn7 <- buttonNewWithLabel "GUI Apps"
  on vBtn7 buttonActivated $ do
    putStrLn "Video Tutorials: GUI Apps"
    callCommand "xdg-open https://www.youtube.com/playlist?list=PL5--8gKSku14oJ3sn9D5zpvSLVG0y2Nss &"

  vBtn8 <- buttonNewWithLabel "Haskell"
  on vBtn8 buttonActivated $ do
    putStrLn "Video Tutorials: Haskell"
    callCommand "xdg-open https://www.youtube.com/watch?v=fJRBeWwdby8 &"

  vBtn9 <- buttonNewWithLabel "Shell Scripting"
  on vBtn9 buttonActivated $ do
    putStrLn "Video Tutorials: Shell Scripting"
    callCommand "xdg-open https://www.youtube.com/playlist?list=PL5--8gKSku15YdkGmHjW2A31oPaQ5pEUw &"

  vBtn10 <- buttonNewWithLabel "Vim"
  on vBtn10 buttonActivated $ do
    putStrLn "Video Tutorials: Vim"
    callCommand "xdg-open https://www.youtube.com/playlist?list=PL5--8gKSku15tivUyt0D-mERePLEzrWUz &"

  vBtn11 <- buttonNewWithLabel "Virtual Machines"
  on vBtn11 buttonActivated $ do
    putStrLn "Video Tutorials: Virtual Machines"
    callCommand "xdg-open https://www.youtube.com/playlist?list=PL5--8gKSku16N_IpNYzdWTNogpoe1O3TC &"

  vBtn12 <- buttonNewWithLabel "Xmonad"
  on vBtn12 buttonActivated $ do
    putStrLn "Video Tutorials: XMonad"
    callCommand "xdg-open https://www.youtube.com/playlist?list=PL5--8gKSku144jIsizdhdxq_fKTmBBGBA &"

  vBtn13 <- buttonNewWithLabel "Back To Main Menu"
  on vBtn13 buttonActivated $ do
    putStrLn "User chose: Back To Main Menu"
    widgetHide window2
    widgetShowAll window1

  vBtn14 <- buttonNewWithLabel "Exit"
  on vBtn14 buttonActivated $ do
    putStrLn "User chose: Exit"
    widgetDestroy window2

  ------------------------------------------------------
  -- The checkButton with the autostart functionality --
  ------------------------------------------------------
  check <- checkButtonNewWithLabel "Autostart"
  s <- readFile settings
  if s == "autostart=True"
     then do
         putStrLn s
         toggleButtonSetActive check True
     else do
         putStrLn s
         toggleButtonSetActive check False
  fileExists <- doesFileExist dest -- Check if .desktop is already in autostart dir.
  on check buttonActivated $ do
    state <- toggleButtonGetActive check
    if state
       then do putStrLn "Autostart set to TRUE"
               writeFile settings "autostart=True"
               copyFile source dest
       else do putStrLn "Autostart set to FALSE"
               writeFile settings "autostart=False"
               if fileExists then removeFile dest else putStrLn "No need."

  bashExists <- doesFileExist "/bin/bash" -- Check if /bin/bash exists
  fishExists <- doesFileExist "/bin/fish" -- Check if /bin/fish exists
  zshExists  <- doesFileExist "/bin/zsh"  -- Check if /bin/zsh exists

  shellBtn0 <- radioButtonNewWithLabel "Don't change"
  shellBtn1 <- radioButtonNewWithLabelFromWidget shellBtn0 "Bash"
  shellBtn2 <- radioButtonNewWithLabelFromWidget shellBtn1 "Fish"
  shellBtn3 <- radioButtonNewWithLabelFromWidget shellBtn2 "Zsh"

  on shellBtn0 buttonActivated $ do
    setRadioState shellBtn0
    putStrLn "Default Button Selected: Don't change"

  on shellBtn1 buttonActivated $ do
    setRadioState shellBtn1

  on shellBtn2 buttonActivated $ do
    setRadioState shellBtn2

  on shellBtn3 buttonActivated $ do
    setRadioState shellBtn3

  shellBtn4 <- buttonNewWithLabel "Save Choice"
  on shellBtn4 buttonActivated $ do
    stateBash <- toggleButtonGetActive shellBtn1
    stateFish <- toggleButtonGetActive shellBtn2
    stateZsh  <- toggleButtonGetActive shellBtn3
    if stateBash
       then do
           if bashExists
             then do callCommand ("pkexec chsh " ++ user ++ " -s /bin/bash")
                     putStrLn ("Bash is now " ++ user ++ "'s default shell")
           else putStrLn "Can't change shell. Bash does not exist."
    else putStrLn "Bash was not chosen."
    if stateFish
       then do
           if fishExists
             then do callCommand ("pkexec chsh " ++ user ++ " -s /bin/fish")
                     putStrLn ("Fish is now " ++ user ++ "'s default shell")
           else putStrLn "Can't change shell. Fish does not exist."
    else putStrLn "Fish was not chosen."
    if stateZsh
       then do
           if zshExists
             then do callCommand ("pkexec chsh " ++ user ++ " -s /bin/zsh")
                     putStrLn ("Zsh is now " ++ user ++ "'s default shell")
           else putStrLn "Can't change shell. Zsh does not exist."
    else putStrLn "Zsh was not chosen."

  shellBtn5 <- buttonNewWithLabel "Back To Main Menu"
  on shellBtn5 buttonActivated $ do
    putStrLn "User chose: Back To Main Menu"
    widgetHide window3
    widgetShowAll window1

  shellBtn6 <- buttonNewWithLabel "Exit"
  on shellBtn6 buttonActivated $ do
    putStrLn "User chose: Exit"
    widgetDestroy window3

  colorBtn0  <- radioButtonNewWithLabel "Don't change"
  colorBtn1  <- radioButtonNewWithLabelFromWidget colorBtn0 "DoomOne"
  colorBtn2  <- radioButtonNewWithLabelFromWidget colorBtn1 "Dracula"
  colorBtn3  <- radioButtonNewWithLabelFromWidget colorBtn2 "GruvboxDark"
  colorBtn4  <- radioButtonNewWithLabelFromWidget colorBtn3 "MonokaiPro"
  colorBtn5  <- radioButtonNewWithLabelFromWidget colorBtn4 "Nord"
  colorBtn6  <- radioButtonNewWithLabelFromWidget colorBtn5 "OceanicNext"
  colorBtn7  <- radioButtonNewWithLabelFromWidget colorBtn6 "Palenight"
  colorBtn8  <- radioButtonNewWithLabelFromWidget colorBtn7 "SolarizedDark"
  colorBtn9  <- radioButtonNewWithLabelFromWidget colorBtn8 "SolarizedLight"
  colorBtn10 <- radioButtonNewWithLabelFromWidget colorBtn9 "TomorrowNight"

  colorBtn11 <- buttonNewWithLabel "Save Choice"
  on colorBtn11 buttonActivated $ do
    checkActive0  <- toggleButtonGetActive colorBtn0
    checkActive1  <- toggleButtonGetActive colorBtn1
    checkActive2  <- toggleButtonGetActive colorBtn2
    checkActive3  <- toggleButtonGetActive colorBtn3
    checkActive4  <- toggleButtonGetActive colorBtn4
    checkActive5  <- toggleButtonGetActive colorBtn5
    checkActive6  <- toggleButtonGetActive colorBtn6
    checkActive7  <- toggleButtonGetActive colorBtn7
    checkActive8  <- toggleButtonGetActive colorBtn8
    checkActive9  <- toggleButtonGetActive colorBtn9
    checkActive10 <- toggleButtonGetActive colorBtn10

    let c | checkActive1  = "DoomOne"
          | checkActive2  = "Dracula"
          | checkActive3  = "GruvboxDark"
          | checkActive4  = "MonokaiPro"
          | checkActive5  = "Nord"
          | checkActive6  = "OceanicNext"
          | checkActive7  = "Palenight"
          | checkActive8  = "SolarizedDark"
          | checkActive9  = "SolarizedLight"
          | checkActive10 = "TomorrowNight"
          | otherwise     = "None"

    let editXmonadReadme = "sed -i 's/import Colors.*/import Colors." ++ c ++ "/g' $HOME/.xmonad/README.org || echo 'Cannot modify README.org'"
    let editXmonadHs     = "sed -i 's/import Colors.*/import Colors." ++ c ++ "/g' $HOME/.xmonad/xmonad.hs || echo 'Cannot modify xmonad.hs'"
    let editAlacritty    = "sed -i 's/^colors: .*/colors: \\*" ++ c ++ "/g' $HOME/.config/alacritty/alacritty.yml"

    if not checkActive0 
      then do callCommand editXmonadReadme
              callCommand editXmonadHs
              callCommand editAlacritty
              callCommand "xmonad --restart"
    else putStrLn "No color scheme was selected."

  colorBtn12 <- buttonNewWithLabel "Back To Main Menu"
  on colorBtn12 buttonActivated $ do
    putStrLn "User chose: Back To Main Menu"
    widgetHide window4
    widgetShowAll window1

  colorBtn13 <- buttonNewWithLabel "Exit"
  on colorBtn13 buttonActivated $ do
    putStrLn "User chose: Exit"
    widgetDestroy window4

-- Widgets on window1 attached to grid1
  gridAttach grid1 image1  0 0 3 2
  gridAttach grid1 label1  0 2 3 2
  gridAttach grid1 label2  0 4 3 2
  gridAttach grid1 eLabel1 0 6 3 1
  gridAttach grid1 button1 0 7 1 1
  gridAttach grid1 button2 1 7 1 1
  gridAttach grid1 button3 2 7 1 1
  gridAttach grid1 button4 0 8 1 1
  gridAttach grid1 button5 1 8 1 1
  gridAttach grid1 button6 2 8 1 1
  gridAttach grid1 button7 1 9 1 1
  gridAttach grid1 eLabel2 0 10 3 1
  gridAttach grid1 check   2 11 1 1

  -- Widgets on window2 attached to grid2
  gridAttach grid2 image2  0 0 4 2
  gridAttach grid2 label3  0 2 4 2
  gridAttach grid2 eLabel3 0 4 4 2
  gridAttach grid2 vBtn1   0 6 1 1
  gridAttach grid2 vBtn2   1 6 1 1
  gridAttach grid2 vBtn3   2 6 1 1
  gridAttach grid2 vBtn4   3 6 1 1
  gridAttach grid2 vBtn5   0 7 1 1
  gridAttach grid2 vBtn6   1 7 1 1
  gridAttach grid2 vBtn7   2 7 1 1
  gridAttach grid2 vBtn8   3 7 1 1
  gridAttach grid2 vBtn9   0 8 1 1
  gridAttach grid2 vBtn10  1 8 1 1
  gridAttach grid2 vBtn11  2 8 1 1
  gridAttach grid2 vBtn12  3 8 1 1
  gridAttach grid2 eLabel4 0 9 4 1
  gridAttach grid2 vBtn13  0 10 2 1
  gridAttach grid2 vBtn14  2 10 2 1

  gridAttach grid3 image3    0 0 4 2
  gridAttach grid3 label4    0 2 4 2
  gridAttach grid3 eLabel5   0 4 4 2
  gridAttach grid3 shellBtn0 0 6 1 1
  gridAttach grid3 shellBtn1 1 6 1 1
  gridAttach grid3 shellBtn2 2 6 1 1
  gridAttach grid3 shellBtn3 3 6 1 1
  gridAttach grid3 eLabel6   0 7 3 1
  gridAttach grid3 shellBtn4 1 8 2 1
  gridAttach grid3 shellBtn5 0 9 2 1
  gridAttach grid3 shellBtn6 2 9 2 1

  gridAttach grid4 image4     0 0 4 2
  gridAttach grid4 label5     0 2 4 2
  gridAttach grid4 eLabel7    0 4 4 2
  gridAttach grid4 colorBtn0  0 6 1 1
  gridAttach grid4 colorBtn1  1 6 1 1
  gridAttach grid4 colorBtn2  2 6 1 1
  gridAttach grid4 colorBtn3  3 6 1 1
  gridAttach grid4 colorBtn4  0 7 1 1
  gridAttach grid4 colorBtn5  1 7 1 1
  gridAttach grid4 colorBtn6  2 7 1 1
  gridAttach grid4 colorBtn7  3 7 1 1
  gridAttach grid4 colorBtn8  0 8 1 1
  gridAttach grid4 colorBtn9  1 8 1 1
  gridAttach grid4 colorBtn10 2 8 1 1
  gridAttach grid4 eLabel8    0 9 4 1
  gridAttach grid4 colorBtn11 1 10 2 1
  gridAttach grid4 colorBtn12 0 11 2 1
  gridAttach grid4 colorBtn13 2 11 2 1

  containerAdd window1 frame1
  containerAdd frame1  grid1
  containerAdd window2 frame2
  containerAdd frame2  grid2
  containerAdd window3 frame3
  containerAdd frame3  grid3
  containerAdd window4 frame4
  containerAdd frame4  grid4

  widgetShowAll window1
  mainGUI -- main loop

setRadioState :: RadioButton -> IO ()
setRadioState b = do
  state <- toggleButtonGetActive b
  label <- get b buttonLabel
  putStrLn ("State " ++ label ++ " now is " ++ (show state))

testDialog = do
   fd <- fileChooserDialogNew Nothing
           Nothing
           FileChooserActionOpen
           [ ("gtk-open", ResponseAccept)
           , ("gtk-cancel", ResponseCancel)]
   dialogRun fd
   widgetDestroy fd

whileIdle b= do
  idleAdd (buttonSetLabel b "Please wait..." >> return True) priorityDefaultIdle
