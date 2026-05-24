param(
  [switch]$Replace
)

$ErrorActionPreference = "Stop"

$repo = Resolve-Path (Join-Path $PSScriptRoot "..")
$codex = Join-Path $HOME ".codex"
$hooksDir = Join-Path $codex "hooks"
$targetRequirementsToml = Join-Path $codex "requirements.toml"
$targetConfigToml = Join-Path $codex "config.toml"
$sourceRequirementsToml = Join-Path $repo "hooks\requirements.example.toml"
$sourceHookScript = Join-Path $repo "hooks\checkpoint_session_hook.py"
$targetHookScript = Join-Path $hooksDir "checkpoint_session_hook.py"

New-Item -ItemType Directory -Force $hooksDir | Out-Null
Copy-Item -Force $sourceHookScript $targetHookScript

$requirements = Get-Content -Raw -Encoding UTF8 $sourceRequirementsToml
$requirements = $requirements.Replace('C:\Users\YOUR_USER\.codex\hooks', $hooksDir)
$requirements = $requirements.Replace('C:\Users\YOUR_USER\.codex\hooks\checkpoint_session_hook.py', $targetHookScript)
$requirements = $requirements.Replace('python3 "$HOME/.codex/hooks/checkpoint_session_hook.py"', 'python "' + $targetHookScript + '"')
Set-Content -Encoding UTF8 $targetRequirementsToml $requirements

$config = ""
if (Test-Path $targetConfigToml) {
  $config = Get-Content -Raw -Encoding UTF8 $targetConfigToml
}

$managedBlockStart = "# BEGIN checkpoint managed hooks"
$managedBlockEnd = "# END checkpoint managed hooks"
$managedBlock = @"

$managedBlockStart
[hooks]
managed_dir = "~/.codex/hooks"
windows_managed_dir = '$hooksDir'

[[hooks.SessionStart]]
matcher = "startup|resume|clear|compact"

[[hooks.SessionStart.hooks]]
type = "command"
command = 'python "$targetHookScript"'
command_windows = 'python "$targetHookScript"'
timeout = 10
statusMessage = "Initializing checkpoint session log"

[[hooks.UserPromptSubmit]]

[[hooks.UserPromptSubmit.hooks]]
type = "command"
command = 'python "$targetHookScript"'
command_windows = 'python "$targetHookScript"'
timeout = 10
statusMessage = "Recording checkpoint session prompt"

[[hooks.PostCompact]]
matcher = "manual|auto"

[[hooks.PostCompact.hooks]]
type = "command"
command = 'python "$targetHookScript"'
command_windows = 'python "$targetHookScript"'
timeout = 10
statusMessage = "Recording compact boundary"
$managedBlockEnd
"@

$pattern = "(?s)\r?\n?# BEGIN checkpoint managed hooks.*?# END checkpoint managed hooks\r?\n?"
if ($config -match [regex]::Escape($managedBlockStart)) {
  $config = [regex]::Replace($config, $pattern, "`r`n$managedBlock`r`n")
} else {
  $config = $config.TrimEnd() + "`r`n" + $managedBlock + "`r`n"
}

if ($config -match "(?m)^\[features\]\s*$") {
  $featureBlockPattern = "(?ms)(^\[features\]\s*\r?\n)(.*?)(?=^\[|\z)"
  $config = [regex]::Replace($config, $featureBlockPattern, {
    param($m)
    $body = $m.Groups[2].Value
    if ($body -match "(?m)^hooks\s*=") {
      return $m.Value
    }
    return $m.Groups[1].Value + $body.TrimEnd() + "`r`nhooks = true`r`n`r`n"
  }, 1)
} else {
  $config = $config.TrimEnd() + "`r`n`r`n[features]`r`nhooks = true`r`n"
}
Set-Content -Encoding UTF8 $targetConfigToml $config

Write-Host "Installed checkpoint hook script: $targetHookScript"
Write-Host "Updated Codex managed requirements: $targetRequirementsToml"
Write-Host "Updated Codex user config inline hooks: $targetConfigToml"
Write-Host "Restart Codex so managed requirements are reloaded."
