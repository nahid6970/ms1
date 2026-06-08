param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$RemainingArgs
)

& codex @RemainingArgs
$exitCode = $LASTEXITCODE

try {
    python "C:\@delta\ms1\asset\codex\task_complete.py"
} catch {
}

exit $exitCode
