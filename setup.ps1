#!/usr/bin/env pwsh
#Requires -Version 7.5

[CmdletBinding()]
param(
  [switch]$Force,
  [switch]$Test
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# Core configuration
$PYTHON_MIN = [Version]'3.10.0'
$IS_WINDOWS = $IsWindows -or ($env:OS -eq 'Windows_NT')

# All required packages (consolidated for reliability)
$PACKAGES = @(
  'asyncpg',
  'httpx-sse',
  'sse-starlette', 
  'pydantic-ai',
  'pgvector',
  'pyautogui',
  'numpy',
  'orjson',
  'lz4',
  'ujson',
  'types-PyAutoGUI',
  'types-ujson'
)

# Unix-only packages
if (-not $IS_WINDOWS) {
  $PACKAGES += 'uvloop'
}

# Utility functions
function Test-Command {
  param([string]$Command)
  return $null -ne (Get-Command $Command -ErrorAction SilentlyContinue)
}

function Get-PythonExecutable {
  $pythonCommands = @('python', 'python3', 'py')
  foreach ($cmd in $pythonCommands) {
    if (Test-Command $cmd) {
      try {
        $version = & $cmd --version 2>&1
        if ($version -match 'Python (\d+\.\d+\.\d+)') {
          $pythonVersion = [Version]$matches[1]
          if ($pythonVersion -ge $PYTHON_MIN) {
            return $cmd
          }
        }
      } catch { continue }
    }
  }
  return $null
}

function Install-Packages {
  param([string]$PythonCmd, [string[]]$Packages)
  
  # Upgrade pip first
  & $PythonCmd -m pip install --upgrade pip setuptools wheel | Out-Null
  
  # Try uv if available
  if (Test-Command 'uv') {
    try {
      & uv add @Packages
      if ($LASTEXITCODE -eq 0) { return $true }
    } catch { }
  }
  
  # Fallback to pip
  foreach ($package in $Packages) {
    try {
      $pipArgs = @('-m', 'pip', 'install', '--upgrade', $package)
      if ($Force) { $pipArgs += '--force-reinstall' }
      & $PythonCmd @pipArgs
      if ($LASTEXITCODE -ne 0) { throw "Failed to install $package" }
    } catch {
      Write-Error "Failed to install $package`: $_"
      return $false
    }
  }
  return $true
}

function Test-Installation {
  param([string]$PythonCmd)
  
  # Test critical imports
  $imports = @('asyncpg', 'httpx_sse', 'sse_starlette', 'pydantic_ai', 'pgvector', 'orjson', 'lz4')
  if (-not $IS_WINDOWS) { $imports += 'uvloop' }
  
  foreach ($import in $imports) {
    try {
      & $PythonCmd -c "import $import" 2>&1 | Out-Null
      if ($LASTEXITCODE -ne 0) {
        Write-Error "Import test failed for $import"
        return $false
      }
    } catch {
      Write-Error "Import test failed for $import`: $_"
      return $false
    }
  }
  return $true
}

# Main execution
try {
  $pythonCmd = Get-PythonExecutable
  if (-not $pythonCmd) {
    throw "Python $PYTHON_MIN or higher required"
  }
  
  if (-not (Install-Packages -PythonCmd $pythonCmd -Packages $PACKAGES)) {
    throw "Package installation failed"
  }
  
  if ($Test -and -not (Test-Installation -PythonCmd $pythonCmd)) {
    throw "Installation verification failed"
  }
  
  exit 0
} catch {
  Write-Error $_.Exception.Message
  exit 1
}
