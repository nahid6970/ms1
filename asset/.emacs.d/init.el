;; Emacs Configuration with Beautiful UI and Org-mode Setup
;; Place this in ~/AppDate/Roaming/.emacs.d/init.el

;; Package management setup
(require 'package)
(setq package-archives
      '(("melpa" . "https://raw.githubusercontent.com/d12frosted/elpa-mirror/master/melpa/")
        ("org"   . "https://raw.githubusercontent.com/d12frosted/elpa-mirror/master/org/")
        ("gnu"   . "https://raw.githubusercontent.com/d12frosted/elpa-mirror/master/gnu/")))
;; (setq package-check-signature nil) ;; probably not necessary
(package-initialize)

;; Bootstrap use-package
(unless (package-installed-p 'use-package)
  (package-refresh-contents)
  (package-install 'use-package))

(eval-when-compile
  (require 'use-package))

;; ============================================================================
;; UI THEMING & APPEARANCE
;; ============================================================================

;; Remove UI clutter
(menu-bar-mode -1)
(tool-bar-mode -1)
(scroll-bar-mode -1)
(setq inhibit-startup-message t)
(setq ring-bell-function 'ignore)

;; Line numbers and basic UI
(global-display-line-numbers-mode 1)
(setq display-line-numbers-type 'relative)
(column-number-mode 1)
(show-paren-mode 1)

;; Font setup
(set-face-attribute 'default nil
                    :font "Consolas"
                    :height 110)

;; Theme - Doom Themes (popular choice)
(use-package doom-themes
  :ensure t
  :config
  (setq doom-themes-enable-bold t
        doom-themes-enable-italic t)
  (load-theme 'doom-one t)
  
  ;; Enable flashing mode-line on errors
  (doom-themes-visual-bell-config)
  
  ;; Corrects (and improves) org-mode's native fontification
  (doom-themes-org-config))

;; Doom Modeline - Beautiful status bar
(use-package doom-modeline
  :ensure t
  :init (doom-modeline-mode 1)
  :config
  (setq doom-modeline-height 25
        doom-modeline-bar-width 3
        doom-modeline-icon t
        doom-modeline-major-mode-icon t
        doom-modeline-buffer-file-name-style 'truncate-upto-project))

;; All the Icons (required for doom-modeline)
(use-package all-the-icons
  :ensure t
  :if (display-graphic-p))

;; Dashboard - Beautiful startup screen
(use-package dashboard
  :ensure t
  :config
  (dashboard-setup-startup-hook)
  (setq dashboard-startup-banner 'logo
        dashboard-center-content t
        dashboard-items '((recents  . 5)
                         (bookmarks . 5)
                         (projects . 5)
                         (agenda . 5))
        dashboard-set-heading-icons t
        dashboard-set-file-icons t))

;; Rainbow delimiters - Colorful parentheses
(use-package rainbow-delimiters
  :ensure t
  :hook (prog-mode . rainbow-delimiters-mode))

;; Highlight current line
(global-hl-line-mode 1)

;; Better scrolling
(setq scroll-margin 3
      scroll-conservatively 10000
      scroll-step 1
      auto-window-vscroll nil)

;; ============================================================================
;; ORG-MODE CONFIGURATION
;; ============================================================================

(use-package org
  :ensure t
  :config
  ;; Basic org settings
  (setq org-hide-emphasis-markers t      ; Hide markup characters like *bold*
        org-pretty-entities t            ; Show unicode symbols
        org-startup-indented t           ; Indent content under headers
        org-startup-with-inline-images t ; Show images by default
        org-image-actual-width '(400)   ; Resize images
        org-fontify-quote-and-verse-blocks t
        org-src-fontify-natively t       ; Syntax highlighting in code blocks
        org-src-tab-acts-natively t      ; Tab works normally in code blocks
        org-edit-src-content-indentation 0
        org-src-preserve-indentation t)
  
  ;; Org directories
  (setq org-directory "~/org/"
        org-default-notes-file (concat org-directory "notes.org"))
  
  ;; Agenda files
  (setq org-agenda-files '("~/org/"))
  
  ;; TODO keywords
  (setq org-todo-keywords
        '((sequence "TODO(t)" "IN-PROGRESS(i)" "WAITING(w)" "|" "DONE(d)" "CANCELLED(c)")))
  
  ;; Beautiful TODO keyword colors
  (setq org-todo-keyword-faces
        '(("TODO" . (:foreground "#ff6c6b" :weight bold))
          ("IN-PROGRESS" . (:foreground "#ECBE7B" :weight bold))
          ("WAITING" . (:foreground "#a9a1e1" :weight bold))
          ("DONE" . (:foreground "#98be65" :weight bold))
          ("CANCELLED" . (:foreground "#5B6268" :weight bold))))
  
  ;; Capture templates
  (setq org-capture-templates
        '(("t" "Todo" entry (file+headline "~/org/tasks.org" "Tasks")
           "* TODO %?\n  %i\n  %a")
          ("n" "Note" entry (file+headline "~/org/notes.org" "Notes")
           "* %?\nEntered on %U\n  %i\n  %a"))))

;; Beautiful org fonts and scaling
(custom-set-faces
 ;; Org-mode heading sizes
 '(org-document-title ((t (:height 2.0 :weight bold :foreground "#51afef"))))
 '(org-level-1 ((t (:height 1.6 :weight bold :foreground "#51afef"))))
 '(org-level-2 ((t (:height 1.4 :weight semi-bold :foreground "#c678dd"))))
 '(org-level-3 ((t (:height 1.2 :weight normal :foreground "#98be65"))))
 '(org-level-4 ((t (:height 1.1 :weight normal :foreground "#ECBE7B"))))
 '(org-level-5 ((t (:height 1.0 :weight normal :foreground "#46D9FF"))))
 
 ;; Code blocks
 '(org-block ((t (:background "#1e2029" :extend t))))
 '(org-block-begin-line ((t (:background "#1c1f24" :foreground "#5B6268" :extend t))))
 '(org-block-end-line ((t (:background "#1c1f24" :foreground "#5B6268" :extend t))))
 '(org-code ((t (:background "#1e2029" :foreground "#98be65"))))
 '(org-verbatim ((t (:background "#1e2029" :foreground "#c678dd"))))
 
 ;; Other org elements
 '(org-quote ((t (:background "#1e2029" :slant italic :extend t))))
 '(org-table ((t (:foreground "#51afef"))))
 '(org-link ((t (:foreground "#51afef" :underline t))))
 '(org-date ((t (:foreground "#ECBE7B"))))
 '(org-special-keyword ((t (:foreground "#5B6268"))))
 '(org-meta-line ((t (:foreground "#5B6268")))))

;; ============================================================================
;; ORG BABEL - CODE EXECUTION (FIXED)
;; ============================================================================

;; Enable code execution for multiple languages
(org-babel-do-load-languages
 'org-babel-load-languages
 '((python . t)
   (shell . t)
   (emacs-lisp . t)
   (js . t)          ; Fixed: was 'javascript', should be 'js'
   (sql . t)
   (C . t)))         ; Removed languages that might not be available

;; Don't ask for confirmation before executing code
(setq org-confirm-babel-evaluate nil)

;; Better code block templates
(require 'org-tempo)
(add-to-list 'org-structure-template-alist '("py" . "src python"))
(add-to-list 'org-structure-template-alist '("sh" . "src shell"))
(add-to-list 'org-structure-template-alist '("js" . "src js"))
(add-to-list 'org-structure-template-alist '("el" . "src emacs-lisp"))

;; ============================================================================
;; ORG ENHANCEMENTS
;; ============================================================================

;; Org Bullets - Beautiful bullet points
(use-package org-bullets
  :ensure t
  :hook (org-mode . org-bullets-mode)
  :config
  (setq org-bullets-bullet-list '("◉" "○" "●" "○" "●" "○" "●")))

;; Visual Line Mode for org files
(add-hook 'org-mode-hook 'visual-line-mode)

;; ============================================================================
;; ADDITIONAL UI ENHANCEMENTS
;; ============================================================================

;; Which Key - Shows available keybindings
(use-package which-key
  :ensure t
  :init (which-key-mode)
  :config
  (setq which-key-idle-delay 0.3))

;; Ivy/Counsel/Swiper - Better completion
(use-package ivy
  :ensure t
  :init (ivy-mode 1)
  :config
  (setq ivy-use-virtual-buffers t
        ivy-count-format "(%d/%d) "
        ivy-height 15))

(use-package counsel
  :ensure t
  :bind (("M-x" . counsel-M-x)
         ("C-x C-f" . counsel-find-file)
         ("C-x b" . counsel-switch-buffer)))

(use-package swiper
  :ensure t
  :bind ("C-s" . swiper))

;; Company - Auto-completion
(use-package company
  :ensure t
  :init (global-company-mode)
  :config
  (setq company-idle-delay 0.2
        company-minimum-prefix-length 2))

;; ============================================================================
;; KEY BINDINGS
;; ============================================================================

;; Org-mode specific bindings
(global-set-key (kbd "C-c l") 'org-store-link)
(global-set-key (kbd "C-c a") 'org-agenda)
(global-set-key (kbd "C-c c") 'org-capture)

;; Quick access to config file
(global-set-key (kbd "C-c e") (lambda () (interactive) (find-file "~/.emacs.d/init.el")))

;; ============================================================================
;; PERFORMANCE & MISC
;; ============================================================================

;; Increase garbage collection threshold
(setq gc-cons-threshold 100000000)

;; Increase the amount of data which Emacs reads from the process
(setq read-process-output-max (* 1024 1024))

;; Backup settings
(setq backup-directory-alist '(("." . "~/.emacs.d/backups")))
(setq delete-old-versions t
      kept-new-versions 6
      kept-old-versions 2
      version-control t)

;; Auto-save settings
(setq auto-save-file-name-transforms '((".*" "~/.emacs.d/auto-save-list/" t)))

;; Recent files
(recentf-mode 1)
(setq recentf-max-menu-items 25)
(global-set-key (kbd "C-x C-r") 'recentf-open-files)

;; ============================================================================
;; STARTUP MESSAGE
;; ============================================================================

(message "Emacs configuration loaded successfully! Enjoy your beautiful setup!")

;; End of configuration
