from libqtile.widget import base
from libqtile import qtile
import subprocess

class GitStatusWidget(base.ThreadPoolText):
    defaults = [
        ('update_interval', 10, 'Update interval in seconds'),
        ('path', '~/ms1', 'Path to the Git repository'),
        ('clean_icon', '', 'Icon when repo is clean'),
        ('dirty_icon', '', 'Icon when repo has changes'),
        ('clean_color', '00ff00', 'Color when repo is clean'),
        ('dirty_color', 'ff0000', 'Color when repo has changes'),
    ]

    def __init__(self, **config):
        base.ThreadPoolText.__init__(self, '', **config)
        self.add_defaults(GitStatusWidget.defaults)

    def poll(self):
        try:
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=self.path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            if result.returncode != 0:
                return f'Git: Error'

            if result.stdout == '':
                self.foreground = self.clean_color
                return self.clean_icon
            else:
                self.foreground = self.dirty_color
                return self.dirty_icon
        except Exception as e:
            return f'Git: {str(e)}'

# Add the widget to your bar in the Qtile configuration file
# widget.GitStatusWidget(path="~/ms1", update_interval=10)
