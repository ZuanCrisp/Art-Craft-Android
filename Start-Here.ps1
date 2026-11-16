<#
  Start-Here.ps1 - one command to install Art Craft Android Sync into YOUR account.
  Run:  .\Start-Here.ps1            (add -Plan first for a read-only rehearsal)
  Needs: Git for Windows. Optional: GitHub CLI (gh auth login) so the secret/default branch/first run are automatic.
#>
[CmdletBinding()]
param(
    [switch]$Plan,
    [switch]$UpdateControl,
    [string]$WorkDir = 'D:\Vibe Coding Project\Art Craft Android',
    [string]$Repository = 'ZuanCrisp/Art-Craft-Android'
)
$ErrorActionPreference = 'Stop'
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force

$installer = Join-Path (Split-Path -Parent $MyInvocation.MyCommand.Path) 'Install-ArtCraftAndroid.ps1'
Unblock-File -LiteralPath $installer -ErrorAction SilentlyContinue

$gitName = 'ZuanCrisp'
$email = Read-Host 'GitHub noreply email (e.g. 12345678+ZuanCrisp@users.noreply.github.com)'
if (-not $email) { throw 'Email is required (it is used for the commit author).' }

$params = @{ WorkDir = $WorkDir; Repository = $Repository; GitUserName = $gitName; GitUserEmail = $email }
if ($Plan) { $params['Plan'] = $true }
elseif ($UpdateControl) { $params['UpdateControl'] = $true }
else { $params['SetSecret'] = $true; $params['FirstRun'] = 'dry-run' }

& $installer @params
