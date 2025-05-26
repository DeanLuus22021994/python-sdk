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

# Required packages with version constraints to avoid issues
$PACKAGES = @(
  'asyncpg>=0.28.0',
  'httpx-sse>=0.4.0',
  'sse-starlette>=1.6.0',
  'pydantic-ai>=0.0.7',
  'pgvector>=0.2.4',
  'pyautogui>=0.9.54',
  'numpy>=1.21.0',
  'orjson>=3.8.0',
  'lz4>=4.0.0',
  'ujson>=5.7.0',
  'types-PyAutoGUI>=0.9.3',
  'types-ujson>=5.7.0'
)

# Unix-only packages
if (-not $IS_WINDOWS) {
  $PACKAGES += 'uvloop>=0.17.0'
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
  Write-Host "Upgrading pip, setuptools, wheel..."
  & $PythonCmd -m pip install --upgrade pip setuptools wheel --quiet
  if ($LASTEXITCODE -ne 0) { throw "Failed to upgrade pip" }
  
  # Install packages one by one with pip (skip uv due to resolution issues)
  foreach ($package in $Packages) {
    Write-Host "Installing $package..."
    try {
      $pipArgs = @('-m', 'pip', 'install', '--upgrade', $package, '--quiet')
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
