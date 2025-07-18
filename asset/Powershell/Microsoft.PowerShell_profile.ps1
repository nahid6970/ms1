using namespace System.Management.Automation
using namespace System.Management.Automation.Language

#* This is an example profile for PSReadLine.
#* This is roughly what I use so there is some emphasis on emacs bindings,
#* but most of these bindings make sense in Windows mode as well.

Import-Module PSReadLine

Set-PSReadLineOption -EditMode Emacs

#* Searching for commands with up/down arrow is really handy.  The
#* option "moves to end" is useful if you want the cursor at the end
#* of the line while cycling through history like it does w/o searching,
#* without that option, the cursor will remain at the position it was
#* when you used up arrow, which can be useful if you forget the exact
#* string you started the search on.
Set-PSReadLineOption -HistorySearchCursorMovesToEnd
Set-PSReadLineKeyHandler -Key UpArrow -Function HistorySearchBackward
Set-PSReadLineKeyHandler -Key DownArrow -Function HistorySearchForward

#* This key handler shows the entire or filtered history using Out-GridView. The
#* typed text is used as the substring pattern for filtering. A selected command
#* is inserted to the command line without invoking. Multiple command selection
#* is supported, e.g. selected by Ctrl + Click.
Set-PSReadLineKeyHandler -Key F7 `
                         -BriefDescription History `
                         -LongDescription 'Show command history' `
                         -ScriptBlock {
    $pattern = $null
    [Microsoft.PowerShell.PSConsoleReadLine]::GetBufferState([ref]$pattern, [ref]$null)
    if ($pattern)
    {
        $pattern = [regex]::Escape($pattern)
    }
    $history = [System.Collections.ArrayList]@(
        $last = ''
        $lines = ''
        foreach ($line in [System.IO.File]::ReadLines((Get-PSReadLineOption).HistorySavePath))
        {
            if ($line.EndsWith('`'))
            {
                $line = $line.Substring(0, $line.Length - 1)
                $lines = if ($lines)
                {
                    "$lines`n$line"
                }
                else
                {
                    $line
                }
                continue
            }
            if ($lines)
            {
                $line = "$lines`n$line"
                $lines = ''
            }
            if (($line -cne $last) -and (!$pattern -or ($line -match $pattern)))
            {
                $last = $line
                $line
            }
        }
    )
    $history.Reverse()
    $command = $history | Out-GridView -Title History -PassThru
    if ($command)
    {
        [Microsoft.PowerShell.PSConsoleReadLine]::RevertLine()
        [Microsoft.PowerShell.PSConsoleReadLine]::Insert(($command -join "`n"))
    }
}

#* This is an example of a macro that you might use to execute a command.
#* This will add the command to history.
Set-PSReadLineKeyHandler -Key Ctrl+b `
                         -BriefDescription BuildCurrentDirectory `
                         -LongDescription "Build the current directory" `
                         -ScriptBlock {
    [Microsoft.PowerShell.PSConsoleReadLine]::RevertLine()
    [Microsoft.PowerShell.PSConsoleReadLine]::Insert("msbuild")
    [Microsoft.PowerShell.PSConsoleReadLine]::AcceptLine()
}

#* In Emacs mode - Tab acts like in bash, but the Windows style completion
#* is still useful sometimes, so bind some keys so we can do both
Set-PSReadLineKeyHandler -Key Ctrl+q -Function TabCompleteNext
Set-PSReadLineKeyHandler -Key Ctrl+Q -Function TabCompletePrevious

#* Clipboard interaction is bound by default in Windows mode, but not Emacs mode.
Set-PSReadLineKeyHandler -Key Ctrl+C -Function Copy
Set-PSReadLineKeyHandler -Key Ctrl+v -Function Paste

#* CaptureScreen is good for blog posts or email showing a transaction
#* of what you did when asking for help or demonstrating a technique.
Set-PSReadLineKeyHandler -Chord 'Ctrl+d,Ctrl+c' -Function CaptureScreen

#* The built-in word movement uses character delimiters, but token based word
#* movement is also very useful - these are the bindings you'd use if you
#* prefer the token based movements bound to the normal emacs word movement
#* key bindings.
Set-PSReadLineKeyHandler -Key Alt+d -Function ShellKillWord
Set-PSReadLineKeyHandler -Key Alt+Backspace -Function ShellBackwardKillWord
Set-PSReadLineKeyHandler -Key Alt+b -Function ShellBackwardWord
Set-PSReadLineKeyHandler -Key Alt+f -Function ShellForwardWord
Set-PSReadLineKeyHandler -Key Alt+B -Function SelectShellBackwardWord
Set-PSReadLineKeyHandler -Key Alt+F -Function SelectShellForwardWord

#region Smart Insert/Delete

#* The next four key handlers are designed to make entering matched quotes
#* parens, and braces a nicer experience.  I'd like to include functions
#* in the module that do this, but this implementation still isn't as smart
#* as ReSharper, so I'm just providing it as a sample.
Set-PSReadLineKeyHandler -Key '"',"'" `
                         -BriefDescription SmartInsertQuote `
                         -LongDescription "Insert paired quotes if not already on a quote" `
                         -ScriptBlock {
    param($key, $arg)
    $quote = $key.KeyChar
    $selectionStart = $null
    $selectionLength = $null
    [Microsoft.PowerShell.PSConsoleReadLine]::GetSelectionState([ref]$selectionStart, [ref]$selectionLength)
    $line = $null
    $cursor = $null
    [Microsoft.PowerShell.PSConsoleReadLine]::GetBufferState([ref]$line, [ref]$cursor)
    # If text is selected, just quote it without any smarts
    if ($selectionStart -ne -1)
    {
        [Microsoft.PowerShell.PSConsoleReadLine]::Replace($selectionStart, $selectionLength, $quote + $line.SubString($selectionStart, $selectionLength) + $quote)
        [Microsoft.PowerShell.PSConsoleReadLine]::SetCursorPosition($selectionStart + $selectionLength + 2)
        return
    }
    $ast = $null
    $tokens = $null
    $parseErrors = $null
    [Microsoft.PowerShell.PSConsoleReadLine]::GetBufferState([ref]$ast, [ref]$tokens, [ref]$parseErrors, [ref]$null)
    function FindToken
    {
        param($tokens, $cursor)
        foreach ($token in $tokens)
        {
            if ($cursor -lt $token.Extent.StartOffset) { continue }
            if ($cursor -lt $token.Extent.EndOffset) {
                $result = $token
                $token = $token -as [StringExpandableToken]
                if ($token) {
                    $nested = FindToken $token.NestedTokens $cursor
                    if ($nested) { $result = $nested }
                }
                return $result
            }
        }
        return $null
    }
    $token = FindToken $tokens $cursor
    # If we're on or inside a **quoted** string token (so not generic), we need to be smarter
    if ($token -is [StringToken] -and $token.Kind -ne [TokenKind]::Generic) {
        # If we're at the start of the string, assume we're inserting a new string
        if ($token.Extent.StartOffset -eq $cursor) {
            [Microsoft.PowerShell.PSConsoleReadLine]::Insert("$quote$quote ")
            [Microsoft.PowerShell.PSConsoleReadLine]::SetCursorPosition($cursor + 1)
            return
        }
        # If we're at the end of the string, move over the closing quote if present.
        if ($token.Extent.EndOffset -eq ($cursor + 1) -and $line[$cursor] -eq $quote) {
            [Microsoft.PowerShell.PSConsoleReadLine]::SetCursorPosition($cursor + 1)
            return
        }
    }
    if ($null -eq $token -or
        $token.Kind -eq [TokenKind]::RParen -or $token.Kind -eq [TokenKind]::RCurly -or $token.Kind -eq [TokenKind]::RBracket) {
        if ($line[0..$cursor].Where{$_ -eq $quote}.Count % 2 -eq 1) {
            # Odd number of quotes before the cursor, insert a single quote
            [Microsoft.PowerShell.PSConsoleReadLine]::Insert($quote)
        }
        else {
            # Insert matching quotes, move cursor to be in between the quotes
            [Microsoft.PowerShell.PSConsoleReadLine]::Insert("$quote$quote")
            [Microsoft.PowerShell.PSConsoleReadLine]::SetCursorPosition($cursor + 1)
        }
        return
    }
    # If cursor is at the start of a token, enclose it in quotes.
    if ($token.Extent.StartOffset -eq $cursor) {
        if ($token.Kind -eq [TokenKind]::Generic -or $token.Kind -eq [TokenKind]::Identifier -or 
            $token.Kind -eq [TokenKind]::Variable -or $token.TokenFlags.hasFlag([TokenFlags]::Keyword)) {
            $end = $token.Extent.EndOffset
            $len = $end - $cursor
            [Microsoft.PowerShell.PSConsoleReadLine]::Replace($cursor, $len, $quote + $line.SubString($cursor, $len) + $quote)
            [Microsoft.PowerShell.PSConsoleReadLine]::SetCursorPosition($end + 2)
            return
        }
    }
    # We failed to be smart, so just insert a single quote
    [Microsoft.PowerShell.PSConsoleReadLine]::Insert($quote)
}

Set-PSReadLineKeyHandler -Key '(','{','[' `
                         -BriefDescription InsertPairedBraces `
                         -LongDescription "Insert matching braces" `
                         -ScriptBlock {
    param($key, $arg)
    $closeChar = switch ($key.KeyChar)
    {
        <#case#> '(' { [char]')'; break }
        <#case#> '{' { [char]'}'; break }
        <#case#> '[' { [char]']'; break }
    }
    $selectionStart = $null
    $selectionLength = $null
    [Microsoft.PowerShell.PSConsoleReadLine]::GetSelectionState([ref]$selectionStart, [ref]$selectionLength)
    $line = $null
    $cursor = $null
    [Microsoft.PowerShell.PSConsoleReadLine]::GetBufferState([ref]$line, [ref]$cursor)
    if ($selectionStart -ne -1)
    {
      # Text is selected, wrap it in brackets
      [Microsoft.PowerShell.PSConsoleReadLine]::Replace($selectionStart, $selectionLength, $key.KeyChar + $line.SubString($selectionStart, $selectionLength) + $closeChar)
      [Microsoft.PowerShell.PSConsoleReadLine]::SetCursorPosition($selectionStart + $selectionLength + 2)
    } else {
      # No text is selected, insert a pair
      [Microsoft.PowerShell.PSConsoleReadLine]::Insert("$($key.KeyChar)$closeChar")
      [Microsoft.PowerShell.PSConsoleReadLine]::SetCursorPosition($cursor + 1)
    }
}

Set-PSReadLineKeyHandler -Key ')',']','}' `
                         -BriefDescription SmartCloseBraces `
                         -LongDescription "Insert closing brace or skip" `
                         -ScriptBlock {
    param($key, $arg)
    $line = $null
    $cursor = $null
    [Microsoft.PowerShell.PSConsoleReadLine]::GetBufferState([ref]$line, [ref]$cursor)
    if ($line[$cursor] -eq $key.KeyChar)
    {
        [Microsoft.PowerShell.PSConsoleReadLine]::SetCursorPosition($cursor + 1)
    }
    else
    {
        [Microsoft.PowerShell.PSConsoleReadLine]::Insert("$($key.KeyChar)")
    }
}

Set-PSReadLineKeyHandler -Key Backspace `
                         -BriefDescription SmartBackspace `
                         -LongDescription "Delete previous character or matching quotes/parens/braces" `
                         -ScriptBlock {
    param($key, $arg)
    $line = $null
    $cursor = $null
    [Microsoft.PowerShell.PSConsoleReadLine]::GetBufferState([ref]$line, [ref]$cursor)
    if ($cursor -gt 0)
    {
        $toMatch = $null
        if ($cursor -lt $line.Length)
        {
            switch ($line[$cursor])
            {
                <#case#> '"' { $toMatch = '"'; break }
                <#case#> "'" { $toMatch = "'"; break }
                <#case#> ')' { $toMatch = '('; break }
                <#case#> ']' { $toMatch = '['; break }
                <#case#> '}' { $toMatch = '{'; break }
            }
        }
        if ($toMatch -ne $null -and $line[$cursor-1] -eq $toMatch)
        {
            [Microsoft.PowerShell.PSConsoleReadLine]::Delete($cursor - 1, 2)
        }
        else
        {
            [Microsoft.PowerShell.PSConsoleReadLine]::BackwardDeleteChar($key, $arg)
        }
    }
}

#endregion Smart Insert/Delete

#* Sometimes you enter a command but realize you forgot to do something else first.
#* This binding will let you save that command in the history so you can recall it,
#* but it doesn't actually execute.  It also clears the line with RevertLine so the
#* undo stack is reset - though redo will still reconstruct the command line.
Set-PSReadLineKeyHandler -Key Alt+w `
                         -BriefDescription SaveInHistory `
                         -LongDescription "Save current line in history but do not execute" `
                         -ScriptBlock {
    param($key, $arg)
    $line = $null
    $cursor = $null
    [Microsoft.PowerShell.PSConsoleReadLine]::GetBufferState([ref]$line, [ref]$cursor)
    [Microsoft.PowerShell.PSConsoleReadLine]::AddToHistory($line)
    [Microsoft.PowerShell.PSConsoleReadLine]::RevertLine()
}

#* Insert text from the clipboard as a here string
Set-PSReadLineKeyHandler -Key Ctrl+V `
                         -BriefDescription PasteAsHereString `
                         -LongDescription "Paste the clipboard text as a here string" `
                         -ScriptBlock {
    param($key, $arg)
    Add-Type -Assembly PresentationCore
    if ([System.Windows.Clipboard]::ContainsText())
    {
        # Get clipboard text - remove trailing spaces, convert \r\n to \n, and remove the final \n.
        $text = ([System.Windows.Clipboard]::GetText() -replace "\p{Zs}*`r?`n","`n").TrimEnd()
        [Microsoft.PowerShell.PSConsoleReadLine]::Insert("@'`n$text`n'@")
    }
    else
    {
        [Microsoft.PowerShell.PSConsoleReadLine]::Ding()
    }
}

#* Sometimes you want to get a property of invoke a member on what you've entered so far
#* but you need parens to do that.  This binding will help by putting parens around the current selection,
#* or if nothing is selected, the whole line.
Set-PSReadLineKeyHandler -Key 'Alt+(' `
                         -BriefDescription ParenthesizeSelection `
                         -LongDescription "Put parenthesis around the selection or entire line and move the cursor to after the closing parenthesis" `
                         -ScriptBlock {
    param($key, $arg)
    $selectionStart = $null
    $selectionLength = $null
    [Microsoft.PowerShell.PSConsoleReadLine]::GetSelectionState([ref]$selectionStart, [ref]$selectionLength)
    $line = $null
    $cursor = $null
    [Microsoft.PowerShell.PSConsoleReadLine]::GetBufferState([ref]$line, [ref]$cursor)
    if ($selectionStart -ne -1)
    {
        [Microsoft.PowerShell.PSConsoleReadLine]::Replace($selectionStart, $selectionLength, '(' + $line.SubString($selectionStart, $selectionLength) + ')')
        [Microsoft.PowerShell.PSConsoleReadLine]::SetCursorPosition($selectionStart + $selectionLength + 2)
    }
    else
    {
        [Microsoft.PowerShell.PSConsoleReadLine]::Replace(0, $line.Length, '(' + $line + ')')
        [Microsoft.PowerShell.PSConsoleReadLine]::EndOfLine()
    }
}

#* Each time you press Alt+', this key handler will change the token
#* under or before the cursor.  It will cycle through single quotes, double quotes, or
#* no quotes each time it is invoked.
Set-PSReadLineKeyHandler -Key "Alt+'" `
                         -BriefDescription ToggleQuoteArgument `
                         -LongDescription "Toggle quotes on the argument under the cursor" `
                         -ScriptBlock {
    param($key, $arg)
    $ast = $null
    $tokens = $null
    $errors = $null
    $cursor = $null
    [Microsoft.PowerShell.PSConsoleReadLine]::GetBufferState([ref]$ast, [ref]$tokens, [ref]$errors, [ref]$cursor)
    $tokenToChange = $null
    foreach ($token in $tokens)
    {
        $extent = $token.Extent
        if ($extent.StartOffset -le $cursor -and $extent.EndOffset -ge $cursor)
        {
            $tokenToChange = $token
            # If the cursor is at the end (it's really 1 past the end) of the previous token,
            # we only want to change the previous token if there is no token under the cursor
            if ($extent.EndOffset -eq $cursor -and $foreach.MoveNext())
            {
                $nextToken = $foreach.Current
                if ($nextToken.Extent.StartOffset -eq $cursor)
                {
                    $tokenToChange = $nextToken
                }
            }
            break
        }
    }
    if ($tokenToChange -ne $null)
    {
        $extent = $tokenToChange.Extent
        $tokenText = $extent.Text
        if ($tokenText[0] -eq '"' -and $tokenText[-1] -eq '"')
        {
            # Switch to no quotes
            $replacement = $tokenText.Substring(1, $tokenText.Length - 2)
        }
        elseif ($tokenText[0] -eq "'" -and $tokenText[-1] -eq "'")
        {
            # Switch to double quotes
            $replacement = '"' + $tokenText.Substring(1, $tokenText.Length - 2) + '"'
        }
        else
        {
            # Add single quotes
            $replacement = "'" + $tokenText + "'"
        }
        [Microsoft.PowerShell.PSConsoleReadLine]::Replace(
            $extent.StartOffset,
            $tokenText.Length,
            $replacement)
    }
}

#* This example will replace any aliases on the command line with the resolved commands.
Set-PSReadLineKeyHandler -Key "Alt+%" `
                         -BriefDescription ExpandAliases `
                         -LongDescription "Replace all aliases with the full command" `
                         -ScriptBlock {
    param($key, $arg)
    $ast = $null
    $tokens = $null
    $errors = $null
    $cursor = $null
    [Microsoft.PowerShell.PSConsoleReadLine]::GetBufferState([ref]$ast, [ref]$tokens, [ref]$errors, [ref]$cursor)
    $startAdjustment = 0
    foreach ($token in $tokens)
    {
        if ($token.TokenFlags -band [TokenFlags]::CommandName)
        {
            $alias = $ExecutionContext.InvokeCommand.GetCommand($token.Extent.Text, 'Alias')
            if ($alias -ne $null)
            {
                $resolvedCommand = $alias.ResolvedCommandName
                if ($resolvedCommand -ne $null)
                {
                    $extent = $token.Extent
                    $length = $extent.EndOffset - $extent.StartOffset
                    [Microsoft.PowerShell.PSConsoleReadLine]::Replace(
                        $extent.StartOffset + $startAdjustment,
                        $length,
                        $resolvedCommand)
                    # Our copy of the tokens won't have been updated, so we need to
                    # adjust by the difference in length
                    $startAdjustment += ($resolvedCommand.Length - $length)
                }
            }
        }
    }
}

#* F1 for help on the command line - naturally
Set-PSReadLineKeyHandler -Key F1 `
                         -BriefDescription CommandHelp `
                         -LongDescription "Open the help window for the current command" `
                         -ScriptBlock {
    param($key, $arg)
    $ast = $null
    $tokens = $null
    $errors = $null
    $cursor = $null
    [Microsoft.PowerShell.PSConsoleReadLine]::GetBufferState([ref]$ast, [ref]$tokens, [ref]$errors, [ref]$cursor)
    $commandAst = $ast.FindAll( {
        $node = $args[0]
        $node -is [CommandAst] -and
            $node.Extent.StartOffset -le $cursor -and
            $node.Extent.EndOffset -ge $cursor
        }, $true) | Select-Object -Last 1
    if ($commandAst -ne $null)
    {
        $commandName = $commandAst.GetCommandName()
        if ($commandName -ne $null)
        {
            $command = $ExecutionContext.InvokeCommand.GetCommand($commandName, 'All')
            if ($command -is [AliasInfo])
            {
                $commandName = $command.ResolvedCommandName
            }
            if ($commandName -ne $null)
            {
                Get-Help $commandName -ShowWindow
            }
        }
    }
}

#* Ctrl+Shift+j then type a key to mark the current directory.
#* Ctrj+j then the same key will change back to that directory without
#* needing to type cd and won't change the command line.
$global:PSReadLineMarks = @{}
Set-PSReadLineKeyHandler -Key Ctrl+J `
                         -BriefDescription MarkDirectory `
                         -LongDescription "Mark the current directory" `
                         -ScriptBlock {
    param($key, $arg)
    $key = [Console]::ReadKey($true)
    $global:PSReadLineMarks[$key.KeyChar] = $pwd
}
Set-PSReadLineKeyHandler -Key Ctrl+j `
                         -BriefDescription JumpDirectory `
                         -LongDescription "Goto the marked directory" `
                         -ScriptBlock {
    param($key, $arg)
    $key = [Console]::ReadKey()
    $dir = $global:PSReadLineMarks[$key.KeyChar]
    if ($dir)
    {
        Set-Location $dir
        [Microsoft.PowerShell.PSConsoleReadLine]::InvokePrompt()
    }
}
Set-PSReadLineKeyHandler -Key Alt+j `
                         -BriefDescription ShowDirectoryMarks `
                         -LongDescription "Show the currently marked directories" `
                         -ScriptBlock {
    param($key, $arg)
    $global:PSReadLineMarks.GetEnumerator() | ForEach-Object {
        [PSCustomObject]@{Key = $_.Key; Dir = $_.Value} } |
        Format-Table -AutoSize | Out-Host
    [Microsoft.PowerShell.PSConsoleReadLine]::InvokePrompt()
}

#* Auto correct 'git cmt' to 'git commit'
Set-PSReadLineOption -CommandValidationHandler {
    param([CommandAst]$CommandAst)
    switch ($CommandAst.GetCommandName())
    {
        'git' {
            $gitCmd = $CommandAst.CommandElements[1].Extent
            switch ($gitCmd.Text)
            {
                'cmt' {
                    [Microsoft.PowerShell.PSConsoleReadLine]::Replace(
                        $gitCmd.StartOffset, $gitCmd.EndOffset - $gitCmd.StartOffset, 'commit')
                }
            }
        }
    }
}

#* `ForwardChar` accepts the entire suggestion text when the cursor is at the end of the line.
#* This custom binding makes `RightArrow` behave similarly - accepting the next word instead of the entire suggestion text.
Set-PSReadLineKeyHandler -Key RightArrow `
                         -BriefDescription ForwardCharAndAcceptNextSuggestionWord `
                         -LongDescription "Move cursor one character to the right in the current editing line and accept the next word in suggestion when it's at the end of current editing line" `
                         -ScriptBlock {
    param($key, $arg)
    $line = $null
    $cursor = $null
    [Microsoft.PowerShell.PSConsoleReadLine]::GetBufferState([ref]$line, [ref]$cursor)
    if ($cursor -lt $line.Length) {
        [Microsoft.PowerShell.PSConsoleReadLine]::ForwardChar($key, $arg)
    } else {
        [Microsoft.PowerShell.PSConsoleReadLine]::AcceptNextSuggestionWord($key, $arg)
    }
}

#* Cycle through arguments on current line and select the text. This makes it easier to quickly change the argument if re-running a previously run command from the history
#* or if using a psreadline predictor. You can also use a digit argument to specify which argument you want to select, i.e. Alt+1, Alt+a selects the first argument
#* on the command line.
Set-PSReadLineKeyHandler -Key Alt+a `
                         -BriefDescription SelectCommandArguments `
                         -LongDescription "Set current selection to next command argument in the command line. Use of digit argument selects argument by position" `
                         -ScriptBlock {
    param($key, $arg)
    $ast = $null
    $cursor = $null
    [Microsoft.PowerShell.PSConsoleReadLine]::GetBufferState([ref]$ast, [ref]$null, [ref]$null, [ref]$cursor)
    $asts = $ast.FindAll( {
        $args[0] -is [System.Management.Automation.Language.ExpressionAst] -and
        $args[0].Parent -is [System.Management.Automation.Language.CommandAst] -and
        $args[0].Extent.StartOffset -ne $args[0].Parent.Extent.StartOffset
      }, $true)
    if ($asts.Count -eq 0) {
        [Microsoft.PowerShell.PSConsoleReadLine]::Ding()
        return
    }
    $nextAst = $null
    if ($null -ne $arg) {
        $nextAst = $asts[$arg - 1]
    }
    else {
        foreach ($ast in $asts) {
            if ($ast.Extent.StartOffset -ge $cursor) {
                $nextAst = $ast
                break
            }
        }
        if ($null -eq $nextAst) {
            $nextAst = $asts[0]
        }
    }
    $startOffsetAdjustment = 0
    $endOffsetAdjustment = 0
    if ($nextAst -is [System.Management.Automation.Language.StringConstantExpressionAst] -and
        $nextAst.StringConstantType -ne [System.Management.Automation.Language.StringConstantType]::BareWord) {
            $startOffsetAdjustment = 1
            $endOffsetAdjustment = 2
    }
    [Microsoft.PowerShell.PSConsoleReadLine]::SetCursorPosition($nextAst.Extent.StartOffset + $startOffsetAdjustment)
    [Microsoft.PowerShell.PSConsoleReadLine]::SetMark($null, $null)
    [Microsoft.PowerShell.PSConsoleReadLine]::SelectForwardChar($null, ($nextAst.Extent.EndOffset - $nextAst.Extent.StartOffset) - $endOffsetAdjustment)
}

#* Allow you to type a Unicode code point, then pressing `Alt+x` to transform it into a Unicode char.
Set-PSReadLineKeyHandler -Chord 'Alt+x' `
                         -BriefDescription ToUnicodeChar `
                         -LongDescription "Transform Unicode code point into a UTF-16 encoded string" `
                         -ScriptBlock {
    $buffer = $null
    $cursor = 0
    [Microsoft.PowerShell.PSConsoleReadLine]::GetBufferState([ref] $buffer, [ref] $cursor)
    if ($cursor -lt 4) {
        return
    }
    $number = 0
    $isNumber = [int]::TryParse(
        $buffer.Substring($cursor - 4, 4),
        [System.Globalization.NumberStyles]::AllowHexSpecifier,
        $null,
        [ref] $number)

    if (-not $isNumber) {
        return
    }
    try {
        $unicode = [char]::ConvertFromUtf32($number)
    } catch {
        return
    }
    [Microsoft.PowerShell.PSConsoleReadLine]::Delete($cursor - 4, 4)
    [Microsoft.PowerShell.PSConsoleReadLine]::Insert($unicode)
}

# #* Scoop and Chocolatey Auto Complete
# Invoke-Expression (&scoop-search --hook)
# # Import the Chocolatey Profile that contains the necessary code to enable
# # tab-completions to function for `choco`.
# # Be aware that if you are missing these lines from your profile, tab completion
# # for `choco` will not function.
# # See https://ch0.co/tab-completion for details.
# $ChocolateyProfile = "$env:ChocolateyInstall\helpers\chocolateyProfile.psm1"
# if (Test-Path($ChocolateyProfile)) {
#   Import-Module "$ChocolateyProfile"
# }

# #* Winget AutoComplete
# Register-ArgumentCompleter -Native -CommandName winget -ScriptBlock {
#     param($wordToComplete, $commandAst, $cursorPosition)
#         [Console]::InputEncoding = [Console]::OutputEncoding = $OutputEncoding = [System.Text.Utf8Encoding]::new()
#         $Local:word = $wordToComplete.Replace('"', '""')
#         $Local:ast = $commandAst.ToString().Replace('"', '""')
#         winget complete --word="$Local:word" --commandline "$Local:ast" --position $cursorPosition | ForEach-Object {
#             [System.Management.Automation.CompletionResult]::new($_, $_, 'ParameterValue', $_)
#         }
# }

#* Environmental Variable
$env:PATH += ";c:\ms1"
$env:PATH += ";c:\ms1\scripts"
$env:PATH += ";C:\ms1\utility"
# $env:PATH += ";D:\binutils-gdb\ld"

function killme  {
Stop-Process -Name "python"
Stop-Process -Name "dnplayer"
Stop-Process -Name "chrome"
}

function chat {
  cd "C:\ms1\ollama-chat-app"
  python server.py
}

function yy { pwsh -c "C:\ms1\scripts\winget_scoop\scoop_install.ps1" }
function nay { pwsh -c "C:\ms1\scripts\winget_scoop\scoop_uninstall.ps1" }

function ww { pwsh -c "C:\ms1\scripts\winget_scoop\wget_install.ps1" }
function yayw2 { pwsh -c "C:\ms1\scripts\winget_scoop\wget_install2.ps1" }
function nayw { pwsh -c "C:\ms1\scripts\winget_scoop\wget_install2.ps1" }
function yaywn1 { pwsh -c "C:\ms1\scripts\winget_scoop\wget_n_install.ps1" }
function yaywn2 { pwsh -c "C:\ms1\scripts\winget_scoop\wget_n_install2.ps1" }


# PsExec.exe this will only work through remote not in real terminal
function dark { cmd /c "C:\Users\nahid\OneDrive\backup\PSTools\PsExec64.exe -h -i 1 C:\Users\nahid\OneDrive\backup\DisplaySwitch.exe /external" }
function light { cmd /c "C:\Users\nahid\OneDrive\backup\PSTools\PsExec64.exe -h -i 1 C:\Users\nahid\OneDrive\backup\DisplaySwitch.exe /internal" }
function sd { cmd /c "shutdown /s /f /t 0" }
function rb { cmd /c "shutdown /r /f /t 0" }


function su {
    param (
        [Parameter(ValueFromRemainingArguments=$true)]
        [string[]]$Command
    )
    # Path to sudo.ps1
    $suPath = "C:\Users\nahid\scoop\shims\sudo.ps1"
    # Combine the command arguments into a single string and pass to sudo.ps1
    & $suPath $Command
}



function gitter {
    # Navigate to the current directory
    Set-Location -Path $PWD

    # Check if the current directory is a Git repository
    if (-not (Test-Path ".git")) {
        Write-Host "This is not a Git repository." -ForegroundColor Red
        return
    }

    # Prompt for optional commit message
    $UserInput = Read-Host "Enter commit message (press Enter to use 'Auto-commit')"

    if ([string]::IsNullOrWhiteSpace($UserInput)) {
        $CommitMessage = "Auto-commit"
    } else {
        $CommitMessage = $UserInput
    }

    # Show what changed
    git status
    # Stage all changes
    git add .
    # Commit with the generated message
    git commit -m $CommitMessage
    # Push to the remote repository
    git push

    # Completion message
    Write-Host " ██████╗ ██████╗ ███╗   ███╗██████╗ ██╗     ███████╗████████╗███████╗" -ForegroundColor Green
    Write-Host "██╔════╝██╔═══██╗████╗ ████║██╔══██╗██║     ██╔════╝╚══██╔══╝██╔════╝" -ForegroundColor Green
    Write-Host "██║     ██║   ██║██╔████╔██║██████╔╝██║     █████╗     ██║   █████╗  " -ForegroundColor Green
    Write-Host "██║     ██║   ██║██║╚██╔╝██║██╔═══╝ ██║     ██╔══╝     ██║   ██╔══╝  " -ForegroundColor Green
    Write-Host "╚██████╗╚██████╔╝██║ ╚═╝ ██║██║     ███████╗███████╗   ██║   ███████╗" -ForegroundColor Green
    Write-Host " ╚═════╝ ╚═════╝ ╚═╝     ╚═╝╚═╝     ╚══════╝╚══════╝   ╚═╝   ╚══════╝" -ForegroundColor Green
}



# Adding the function to your PowerShell profile
$ProfilePath = $PROFILE.CurrentUserAllHosts
if (-not (Test-Path $ProfilePath)) {
    New-Item -ItemType File -Path $ProfilePath -Force
}



# function Prompt {
#     $currentLocation = Get-Location
#     Write-Host ("->" + $currentLocation + " ⚡") -ForegroundColor Yellow -BackgroundColor Blue -NoNewline
#     return " "
# }

# function build {
#     cargo build --target-dir C:\Builds
# }

#* Override PSReadLine's history search
#Set-PsFzfOption -PSReadlineChordProvider 'Ctrl+t' `
#                -PSReadlineChordReverseHistory 'Ctrl+r'

#* Import List
# Import-Module scoop-completion

function killp  {
    $processName = (Get-Process | Select-Object Name, CPU | Sort-Object CPU -Descending | Format-Table -AutoSize | Out-String | fzf) -split '\s{2,}' | Select-Object -First 1; if ($processName) { Stop-Process -Name $processName -Force; Write-Host "Process $processName terminated." } else { Write-Host "No process selected." }
}

# function filterfzf {
#     param(
#         [string]$Command,
#         [string]$Text
#     )
#     $output = Invoke-Expression "$Command" | Out-String
#     $filteredOutput = $output -split "`n" | fzf --query="$Text"
#     Write-Output $filteredOutput
# }

# Import-Module -Name C:\ms1\asset\Powershell\pwsh_AutinHistory.ps1
# Import-Module -Name C:\ms1\asset\Powershell\pwsh_Polyfill.ps1

#* Enable Zoxide at the end of the script to work
#f45873b3-b655-43a6-b217-97c00aa0db58 PowerToys CommandNotFound module

# Import-Module -Name Microsoft.WinGet.CommandNotFound
#f45873b3-b655-43a6-b217-97c00aa0db58

# Invoke-Expression (&starship init powershell)

# function cc {
#     $args | ForEach-Object { 
#         Invoke-Expression $_
#     }
# }

# # Alias to save the current directory to the location stack
# Set-Alias cds Push-Location
# # Alias to return to the last saved directory from the location stack
# Set-Alias cdl Pop-Location


# # File to store the last directory
# $global:LastDirectoryFile = "$env:USERPROFILE\last_directory.txt"
# # Function to save the current directory to a file
# function Save-LastDirectory {
#     Set-Content -Path $global:LastDirectoryFile -Value (Get-Location).Path
# }
# # Load the last directory from the file, if it exists
# if (Test-Path $global:LastDirectoryFile) {
#     $global:LastDirectory = Get-Content -Path $global:LastDirectoryFile
# }
# # Alias to save the current directory to the location stack
# Set-Alias cds Save-LastDirectory
# # Alias to return to the last saved directory from the location stack

# function cdl {
#     if ($global:LastDirectory) {
#         Set-Location -Path $global:LastDirectory
#     } else {
#         Write-Host "No last directory found." -ForegroundColor Yellow
#     }
# }


# #! Dynamically define functions to avoid IDE references
# Remove-Item -Path Function:e -ErrorAction SilentlyContinue
# Remove-Item -Path Function:lse -ErrorAction SilentlyContinue

New-Item -Path Function:e -Value { explorer . } -Force | Out-Null
New-Item -Path Function:lse -Value { eza -al --color=always --group-directories-first } -Force | Out-Null
New-Item -Path Function:pk -Value { C:\WINDOWS\SYSTEM32\cmd.exe /c start powershell -ExecutionPolicy Bypass -File "C:\ms1\kp.ps1" } -Force | Out-Null
Set-Alias time date
New-Item -Path Function:ms1 -Value  { Set-Location c:\ms1\ } -Force | Out-Null
New-Item -Path Function:ms2 -Value  { Set-Location c:\ms2\ } -Force | Out-Null
New-Item -Path Function:ms3 -Value  { Set-Location c:\ms3\ } -Force | Out-Null
# New-Item -Path Function:yt -Value {yt-dlp} -Force | Out-Null

New-Item -Path Function:trim -Value { C:\Users\nahid\OneDrive\Git\ms1\scripts\ffmpeg\trim.ps1 } -Force | Out-Null

# function wget_install_fzf { winget search --exact "" | fzf --multi --preview 'winget show {1}' | ForEach-Object { winget install $_.split()[0] } }
# function wget_uninstall_fzf { winget list  "" | fzf --multi --preview 'winget show {1}' | ForEach-Object { winget uninstall $_.split()[0] } }

# function scoop_install_fzf { winget search  "" | fzf --multi --preview 'scoop info {1}' | ForEach-Object { scoop install $_.split()[0] } }
# function scoop_uninstall_fzf { scoop list  "" | fzf --multi --preview 'scoop show {1}' | ForEach-Object { scoop uninstall $_.split()[0] } }

Set-Alias trim C:\ms1\scripts\ffmpeg\trim.ps1

# function sync { c:\ms1\sync.ps1 }

# function prowlarr_stop { Stop-Process -Name prowlarr }
# function prowlarr      { Start-Process -FilePath "C:\ProgramData\Prowlarr\bin\Prowlarr.exe" }
# function sonarr        { Start-Process -FilePath "C:\ProgramData\Sonarr\bin\Sonarr.exe" }
# function sonarr_stop   { Stop-Process -Name sonarr }
# function radarr        { Start-Process -FilePath "C:\ProgramData\Radarr\bin\Radarr.exe" }
# function radarr_stop   { Stop-Process -Name radarr }


#! Run in PowerShell remove ( Warning: PowerShell detected that you might be using a 
#! screen reader and has disabled PSReadLine for compatibility purposes. If you want
#! to re-enable it, run 'Import-Module PSReadLine'. )
(Add-Type -PassThru -Name ScreenReaderUtil -Namespace WinApiHelper -MemberDefinition @'
  const int SPIF_SENDCHANGE = 0x0002;
  const int SPI_SETSCREENREADER = 0x0047;

  [DllImport("user32", SetLastError = true, CharSet = CharSet.Unicode)]
  private static extern bool SystemParametersInfo(uint uiAction, uint uiParam, IntPtr pvParam, uint fWinIni);

  public static void EnableScreenReader(bool enable)
  {
    var ok = SystemParametersInfo(SPI_SETSCREENREADER, enable ? 1u : 0u, IntPtr.Zero, SPIF_SENDCHANGE);
    if (!ok)
    {
      throw new System.ComponentModel.Win32Exception(Marshal.GetLastWin32Error());
    }
  }
'@)::EnableScreenReader($false)


function pkill {
    param (
        [Parameter(Mandatory = $true)]
        [string]$Name
    )
    $processes = Get-Process | Where-Object { $_.Name -like "*$Name*" }
    if ($processes) {
        $processes | ForEach-Object {
            try {
                Stop-Process -Id $_.Id -Force -ErrorAction Stop
                Write-Host "Killed: $($_.Name) (PID: $($_.Id))" -ForegroundColor Green
            } catch {
                Write-Host "Failed to kill: $($_.Name) (PID: $($_.Id)) - $_" -ForegroundColor Red
            }
        }
    } else {
        Write-Host "No process found matching '$Name'" -ForegroundColor Yellow
    }
}

# $env:GEMINI_API_KEY = "AIzaSyD3tpmHrTXFJGAvL7N055Qz1b4ZRUX6yJM"
$ENV:STARSHIP_CONFIG = "C:\ms1\linux\config\.config\starship\starship.toml"

Invoke-Expression (& 'C:\Users\nahid\scoop\shims\starship.exe' init powershell --print-full-init | Out-String)
# oh-my-posh init pwsh --config 'C:\Users\nahid\scoop\apps\oh-my-posh\current\themes\1_shell.omp.json' | Invoke-Expression
Invoke-Expression (& { (zoxide init powershell | Out-String) })