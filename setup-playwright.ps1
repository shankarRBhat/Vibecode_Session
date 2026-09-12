$ErrorActionPreference = "Stop"

$nodeDir = Join-Path $env:ProgramFiles "nodejs"
$npm = Join-Path $nodeDir "npm.cmd"

if (-not (Test-Path $npm)) {
    throw "Node.js was not found at $nodeDir. Reinstall Node.js LTS, then run this script again."
}

$env:Path = "$nodeDir;$env:Path"
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($userPath -notlike "*${nodeDir}*") {
    [Environment]::SetEnvironmentVariable("Path", "$userPath;$nodeDir", "User")
}

Write-Host "Node.js:"
& (Join-Path $nodeDir "node.exe") --version
Write-Host "npm:"
& $npm --version

& $npm install
& $npm run playwright:agents
& $npm run playwright:skills
& $npm run playwright:install

Write-Host "Playwright setup completed. Restart the VS Code terminal before using npm directly."
