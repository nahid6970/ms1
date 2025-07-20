# Get the list of models from `ollama list`, skipping the header
$models = ollama list | Select-Object -Skip 1 | ForEach-Object {
    ($_ -split '\s+')[0]
}

# Loop through and stop each model
foreach ($model in $models) {
    if ($model -and $model -ne 'NAME') {
        Write-Host "Stopping model: $model"
        ollama stop $model
    }
}