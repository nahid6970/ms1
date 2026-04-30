content = open(r'C:\@delta\ms1\mypygui_qt.py', 'r', encoding='utf-8').read()
content = content.replace('\r\n', '\n')

# Fix 1: Start git status thread in _start_timers after git drain timer
old1 = '        self._git_timer.start(200)'
new1 = '        self._git_timer.start(200)\n        _repos = self._config.get("git_repos", [])\n        if _repos:\n            threading.Thread(target=_git_status_loop, args=(_repos, _git_queue), daemon=True).start()'
content = content.replace(old1, new1, 1)

# Fix 2: Add delete lock button after del_lbl section in _build_git
# Find the closing sep_r and add after it
old2 = '        sep_r = QLabel("]")\n        sep_r.setStyleSheet(f"color: {CP_CYAN}; font-family: \'JetBrainsMono NFP\'; font-size: 18pt; font-weight: bold;")\n        ll.addWidget(sep_r)'
if old2 in content:
    print('Found ] style sep_r')
else:
    # Try finding it differently
    idx = content.find('sep_r = QLabel')
    print(f'sep_r at index: {idx}')
    print(repr(content[idx:idx+150]))

open(r'C:\@delta\ms1\mypygui_qt.py', 'w', encoding='utf-8').write(content)
print('Done')
