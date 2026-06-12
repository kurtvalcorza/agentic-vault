<#
.SYNOPSIS
    Purges all desktop.ini files in the current directory and subdirectories.

.DESCRIPTION
    This script recursively searches for desktop.ini files starting from the current location
    and deletes them. It runs with -Force to ensure hidden/system files are removed.

.EXAMPLE
    .\purge-desktop-ini.ps1
#>

$startPath = Get-Location
Write-Host "Searching for desktop.ini files in: $startPath" -ForegroundColor Cyan

$items = Get-ChildItem -Path $startPath -Filter "desktop.ini" -Recurse -Force -ErrorAction SilentlyContinue

if ($items) {
    # If only one item is found, $items is not an array, so .Count might perform differently in older PS versions,
    # but strictly speaking strict-mode might care. Wrapping in array @() ensures .Count works.
    $items = @($items)
    $count = $items.Count
    Write-Host "Found $count desktop.ini file(s)." -ForegroundColor Yellow
    foreach ($item in $items) {
        try {
            Remove-Item -Path $item.FullName -Force -ErrorAction Stop
            Write-Host "Deleted: $($item.FullName)" -ForegroundColor Green
        }
        catch {
            Write-Host "Failed to delete: $($item.FullName). Error: $($_.Exception.Message)" -ForegroundColor Red
        }
    }
    Write-Host "Purge complete." -ForegroundColor Cyan
}
else {
    Write-Host "No desktop.ini files found." -ForegroundColor Green
}
