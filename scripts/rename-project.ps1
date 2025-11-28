# PowerShell script to rename project components (cross-platform alternative to rename-project.sh)
# Usage: .\rename-project.ps1 [NewProjectName]

$ErrorActionPreference = 'Stop'

function Write-Color($Text, $Color = 'White', $Bold = $false) {
    $esc = "`e["
    $boldCode = if ($Bold) { "1;" } else { "" }
    $colorCode = switch ($Color) {
        'Red' { '31m' }
        'Green' { '32m' }
        'Yellow' { '33m' }
        'Cyan' { '36m' }
        default { '0m' }
    }
    Write-Host "$esc$boldCode$colorCode$Text$esc[0m"
}

function Slugify($name) {
    $slug = $name.ToLower() -replace '[^a-z0-9_-]', '_' -replace '^_+', '' -replace '_+$', ''
    return $slug
}

Set-Location -Path (Join-Path $PSScriptRoot '..')

$NEW_NAME = $null
if ($args.Count -gt 0) {
    $NEW_NAME = $args[0]
}

while ([string]::IsNullOrWhiteSpace($NEW_NAME)) {
    Write-Color "Let's give your project a shiny new name!" 'Cyan'
    $NEW_NAME = Read-Host "Enter the new project name (Ctrl + C to cancel)"
    if ([string]::IsNullOrWhiteSpace($NEW_NAME)) {
        Write-Color "Don't be shy, your project deserves a name!" 'Yellow'
    }
}

$SLUGIFIED_NAME = Slugify $NEW_NAME
if ($NEW_NAME -ne $SLUGIFIED_NAME) {
    Write-Color "The project name should be slugified." 'Yellow'
    Write-Color "Suggested name: $SLUGIFIED_NAME" 'Cyan' $true
    $USE_SUGGESTED = Read-Host "Use suggested name? [Y/n]"
    if ($USE_SUGGESTED -match '^(Y|y|Yes|yes)$' -or [string]::IsNullOrWhiteSpace($USE_SUGGESTED)) {
        $NEW_NAME = $SLUGIFIED_NAME
        Write-Color "Great choice!" 'Green'
    } else {
        while ($true) {
            $NEW_NAME = Read-Host "Enter a slugified project name"
            $SLUGIFIED_NAME = Slugify $NEW_NAME
            if ($NEW_NAME -eq $SLUGIFIED_NAME -and -not [string]::IsNullOrWhiteSpace($NEW_NAME)) {
                Write-Color "Looks perfect!" 'Green'
                break
            } else {
                Write-Color "Name must be slugified (lowercase, alphanumeric, _, -)." 'Red'
            }
        }
    }
}

# Get current project name from docker-compose.production.yml
$CURRENT_NAME = Select-String -Path "docker-compose.production.yml" -Pattern 'image:\s*([a-zA-Z0-9_-]+)(?=_production_django)' | ForEach-Object {
    if ($_.Matches.Count -gt 0) { $_.Matches[0].Groups[1].Value } else { $null }
} | Select-Object -First 1

Write-Color "Current project name: $CURRENT_NAME" 'Cyan' $true
Write-Color "New project name: $NEW_NAME" 'Cyan' $true

Write-Color "Are you sure you want to rename the project from '$CURRENT_NAME' to '$NEW_NAME'?" 'Yellow'
$CONFIRM = Read-Host "[y/N]"
if (-not ($CONFIRM -match '^(Y|y|Yes|yes)$')) {
    Write-Color "Renaming cancelled. Maybe next time!" 'Red'
    exit 0
}

# Replace in files
$files = @(
    "docker-compose.production.yml",
    "docker-compose.local.yml",
    ".devcontainer/devcontainer.json"
)
foreach ($file in $files) {
    if (Test-Path $file) {
        (Get-Content $file) -replace [regex]::Escape($CURRENT_NAME), $NEW_NAME | Set-Content $file
    }
}

Write-Color "🎉 Project renamed successfully to '$NEW_NAME'! 🎉" 'Green' $true
Write-Color "Please review the changes." 'Cyan'
Write-Color "You may want to rebuild the Docker images with: docker-compose -f docker-compose.local.yml build --no-cache or the VSCode Dev Container." 'Yellow'

exit 0
