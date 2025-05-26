#!/usr/bin/env pwsh
#Requires -Version 7.5

<#
.SYNOPSIS
    Setup script for MCP Python SDK development environment
.DESCRIPTION
    This PowerShell script installs and configures all required dependencies for the MCP Python SDK,
    including optional dependencies for examples and enhanced performance features.
    Works on both host and DevContainer environments with robust error handling.
.PARAMETER Force
    Force reinstallation of packages even if they already exist
.PARAMETER SkipOptional
    Skip installation of optional dependencies (performance, examples)
.PARAMETER DevContainer
    Optimize for DevContainer environment (skip certain host-specific operations)
.PARAMETER SkipBuildTools
    Skip Microsoft Visual C++ Build Tools installation check
.EXAMPLE
    .\setup.ps1
.EXAMPLE
    .\setup.ps1 -Force
.EXAMPLE
    .\setup.ps1 -SkipOptional -SkipBuildTools
#>

[CmdletBinding()]
param(
  [switch]$Force,
  [switch]$SkipOptional,
  [switch]$DevContainer,
  [switch]$SkipBuildTools
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Continue'  # Changed to Continue for better error handling

# Configuration
$ProjectRoot = $PSScriptRoot
$PythonRequiredVersion = [Version]'3.10.0'
$IsWindowsPlatform = $IsWindows -or ($env:OS -eq 'Windows_NT')

# Define dependency groups with platform awareness
$CoreDependencies = @(
  'asyncpg',
  'httpx-sse', 
  'sse-starlette',
  'pydantic-ai',
  'pgvector'
)

# Platform-specific performance dependencies
$PerformanceDependencies = if ($IsWindowsPlatform) {
  @(
    'orjson',
    'lz4',
    'xxhash',
    'ujson'
    # uvloop excluded on Windows as it's Unix-only
  )
} else {
  @(
    'uvloop',
    'orjson', 
    'lz4',
    'xxhash',
    'ujson'
  )
}

$ExampleDependencies = @(
  'pyautogui',
  'numpy',
  'types-PyAutoGUI', 
  'types-ujson'
)

# Utility functions
function Write-Section {
  param([string]$Title)
  Write-Host "`n" -NoNewline
  Write-Host "=" * 60 -ForegroundColor Cyan
  Write-Host " $Title" -ForegroundColor Yellow
  Write-Host "=" * 60 -ForegroundColor Cyan
}

function Write-Step {
  param([string]$Message)
  Write-Host "→ $Message" -ForegroundColor Green
}

function Write-Warning {
  param([string]$Message)
  Write-Host "⚠ $Message" -ForegroundColor Yellow
}

function Write-Error {
  param([string]$Message)
  Write-Host "✗ $Message" -ForegroundColor Red
}

function Write-Success {
  param([string]$Message)
  Write-Host "✓ $Message" -ForegroundColor Green
}

function Test-BuildTools {
  if ($DevContainer -or $SkipBuildTools) {
    Write-Step "Skipping build tools check (DevContainer or SkipBuildTools specified)"
    return $true
  }
    
  if (-not $IsWindowsPlatform) {
    Write-Step "Non-Windows platform - build tools check not required"
    return $true
  }
    
  Write-Step "Checking for Microsoft Visual C++ Build Tools..."
    
  # Check for Visual Studio Build Tools or Visual Studio
  $buildToolsPaths = @(
    "${env:ProgramFiles(x86)}\Microsoft Visual Studio\2022\BuildTools\MSBuild\Current\Bin\MSBuild.exe",
    "${env:ProgramFiles}\Microsoft Visual Studio\2022\Professional\MSBuild\Current\Bin\MSBuild.exe",
    "${env:ProgramFiles}\Microsoft Visual Studio\2022\Enterprise\MSBuild\Current\Bin\MSBuild.exe",
    "${env:ProgramFiles}\Microsoft Visual Studio\2022\Community\MSBuild\Current\Bin\MSBuild.exe",
    "${env:ProgramFiles(x86)}\Microsoft Visual Studio\2019\BuildTools\MSBuild\Current\Bin\MSBuild.exe",
    "${env:ProgramFiles(x86)}\Microsoft Visual Studio\2019\Professional\MSBuild\Current\Bin\MSBuild.exe",
    "${env:ProgramFiles(x86)}\Microsoft Visual Studio\2019\Enterprise\MSBuild\Current\Bin\MSBuild.exe",
    "${env:ProgramFiles(x86)}\Microsoft Visual Studio\2019\Community\MSBuild\Current\Bin\MSBuild.exe"
  )
    
  $found = $false
  foreach ($path in $buildToolsPaths) {
    if (Test-Path $path) {
      Write-Success "Found build tools at: $path"
      $found = $true
      break
    }
  }
    
  if (-not $found) {
    Write-Warning @"
Microsoft Visual C++ Build Tools not found!

This is required to compile Python packages with C extensions (like asyncpg).

To install:
1. Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
2. Install 'C++ build tools' workload
3. Or install Visual Studio Community with C++ development tools

Alternative: Use pre-compiled wheels by upgrading pip:
  python -m pip install --upgrade pip setuptools wheel

"@
    return $false
  }
    
  return $true
}

function Install-WindowsBuildTools {
  if (-not $IsWindowsPlatform -or $DevContainer -or $SkipBuildTools) {
    return $true
  }
    
  if (Test-BuildTools) {
    return $true
  }
    
  Write-Step "Attempting to install Microsoft Visual C++ Build Tools..."
    
  try {
    # Try to install using winget if available
    if (Test-Command 'winget') {
      Write-Host "Installing Visual Studio Build Tools via winget..." -ForegroundColor Yellow
      & winget install Microsoft.VisualStudio.2022.BuildTools --silent --accept-package-agreements --accept-source-agreements
            
      if ($LASTEXITCODE -eq 0) {
        Write-Success "Build tools installed successfully"
        return $true
      }
    }
        
    # Try chocolatey if available
    if (Test-Command 'choco') {
      Write-Host "Installing Visual Studio Build Tools via chocolatey..." -ForegroundColor Yellow
      & choco install visualstudio2022buildtools --yes --quiet
            
      if ($LASTEXITCODE -eq 0) {
        Write-Success "Build tools installed successfully"
        return $true
      }
    }
        
    Write-Warning "Automatic installation failed. Please install manually."
    return $false
  } catch {
    Write-Warning "Exception installing build tools: $_"
    return $false
  }
}

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
          if ($pythonVersion -ge $PythonRequiredVersion) {
            return $cmd
          }
        }
      } catch {
        continue
      }
    }
  }
  return $null
}

function Install-CoreMCPPackage {
  param([string]$PythonCmd)
    
  Write-Step "Installing core MCP SDK in development mode..."
    
  # First try with uv in dev mode
  if (Test-Command 'uv') {
    try {
      Write-Host "Running: uv add --dev ." -ForegroundColor Gray
      & uv add --dev .
            
      if ($LASTEXITCODE -eq 0) {
        Write-Success "Successfully installed MCP SDK using uv (dev mode)"
        return $true
      }
    } catch {
      Write-Warning "uv dev installation failed, trying pip editable install"
    }
  }
    
  # Fallback to pip editable install
  try {
    $pipInstallArgs = @('-m', 'pip', 'install', '-e', '.')
    if ($Force) {
      $pipInstallArgs += '--force-reinstall'
    }
        
    Write-Host "Running: $PythonCmd $($pipInstallArgs -join ' ')" -ForegroundColor Gray
    & $PythonCmd @pipInstallArgs
        
    if ($LASTEXITCODE -eq 0) {
      Write-Success "Successfully installed MCP SDK using pip (editable)"
      return $true
    } else {
      Write-Error "Failed to install MCP SDK in development mode"
      return $false
    }
  } catch {
    Write-Error "Exception installing MCP SDK: $_"
    return $false
  }
}

function Install-PackagesWithFallback {
  param(
    [string[]]$Packages,
    [string]$PythonCmd,
    [string]$GroupName = "packages"
  )
    
  if ($Packages.Count -eq 0) {
    Write-Step "No $GroupName to install"
    return $true
  }

  Write-Step "Installing $GroupName..."
    
  # Try packages individually if bulk install fails
  $failedPackages = @()
  $successfulPackages = @()
    
  # First try bulk installation
  $bulkSuccess = $false
  if (Test-Command 'uv') {
    try {
      $uvInstallArgs = @('add') + $Packages
      if ($Force) {
        $uvInstallArgs += '--force'
      }
            
      Write-Host "Running: uv $($uvInstallArgs -join ' ')" -ForegroundColor Gray
      & uv @uvInstallArgs
            
      if ($LASTEXITCODE -eq 0) {
        Write-Success "Successfully installed $GroupName using uv"
        return $true
      }
    } catch {
      Write-Warning "uv bulk installation failed, trying individual packages"
    }
  }
    
  # If bulk failed, try individual packages
  Write-Step "Trying individual package installation for $GroupName..."
  foreach ($package in $Packages) {
    $installed = $false
        
    # Try with uv first
    if (Test-Command 'uv' -and -not $installed) {
      try {
        $uvArgs = @('add', $package)
        if ($Force) {
          $uvArgs += '--force'
        }
                
        Write-Host "Installing $package with uv..." -ForegroundColor Gray
        & uv @uvArgs
                
        if ($LASTEXITCODE -eq 0) {
          $successfulPackages += $package
          $installed = $true
        }
      } catch {
        Write-Warning "uv failed for $package, trying pip"
      }
    }
        
    # Fallback to pip
    if (-not $installed) {
      try {
        $pipArgs = @('-m', 'pip', 'install', '--upgrade', $package)
        if ($Force) {
          $pipArgs += '--force-reinstall'
        }
                
        Write-Host "Installing $package with pip..." -ForegroundColor Gray
        & $PythonCmd @pipArgs
                
        if ($LASTEXITCODE -eq 0) {
          $successfulPackages += $package
          $installed = $true
        }
      } catch {
        Write-Warning "pip also failed for $package"
      }
    }
        
    if (-not $installed) {
      $failedPackages += $package
      Write-Warning "Failed to install: $package"
    }
  }
    
  if ($successfulPackages.Count -gt 0) {
    Write-Success "Successfully installed: $($successfulPackages -join ', ')"
  }
    
  if ($failedPackages.Count -gt 0) {
    Write-Warning "Failed to install: $($failedPackages -join ', ')"
    return $false
  }
    
  return $true
}

function Initialize-Environment {
  Write-Section "Environment Initialization"
    
  # Ensure we're in the project root
  Set-Location $ProjectRoot
  Write-Step "Working directory: $ProjectRoot"
  Write-Step "Platform: $(if ($IsWindowsPlatform) { 'Windows' } else { 'Unix-like' })"
    
  # Check for uv and install if not present
  if (-not (Test-Command 'uv')) {
    Write-Step "Installing uv package manager..."
    try {
      if ($IsWindowsPlatform) {
        Invoke-RestMethod https://astral.sh/uv/install.ps1 | Invoke-Expression
      } else {
        Invoke-RestMethod https://astral.sh/uv/install.sh | sh
      }
            
      # Refresh PATH for current session
      if ($IsWindowsPlatform) {
        $env:PATH = "$env:USERPROFILE\.local\bin;$env:PATH"
      } else {
        $env:PATH = "$env:HOME/.local/bin:$env:PATH"
      }
            
      if (Test-Command 'uv') {
        Write-Success "uv installed successfully"
      } else {
        Write-Warning "uv installation may require shell restart"
      }
    } catch {
      Write-Warning "Failed to install uv: $_"
    }
  } else {
    Write-Success "uv package manager is available"
  }
    
  # Upgrade pip and setuptools for better wheel support
  Write-Step "Upgrading pip and setuptools for better wheel support..."
  $pythonCmd = Get-PythonExecutable
  if ($pythonCmd) {
    try {
      & $pythonCmd -m pip install --upgrade pip setuptools wheel
      Write-Success "pip, setuptools, and wheel upgraded"
    } catch {
      Write-Warning "Failed to upgrade pip/setuptools: $_"
    }
  }
}

function Test-PythonEnvironment {
  Write-Section "Python Environment Verification"
    
  $pythonCmd = Get-PythonExecutable
  if (-not $pythonCmd) {
    Write-Error "Python $PythonRequiredVersion or higher is required but not found"
    Write-Host "Please install Python from https://python.org or use a package manager" -ForegroundColor Yellow
    exit 1
  }
    
  $version = & $pythonCmd --version
  Write-Success "Found Python: $version"
  Write-Step "Python executable: $pythonCmd"
    
  return $pythonCmd
}

function Install-Dependencies {
  param([string]$PythonCmd)
    
  Write-Section "Installing Dependencies"
    
  # First ensure we have build tools if on Windows
  if ($IsWindowsPlatform -and -not $SkipBuildTools) {
    if (-not (Install-WindowsBuildTools)) {
      Write-Warning "Build tools installation failed. Some packages may not compile correctly."
      Write-Warning "Consider using -SkipBuildTools if you want to proceed with pre-compiled wheels."
    }
  }
    
  # Install core MCP SDK in development mode
  Write-Step "Installing MCP SDK..."
  $mcpSuccess = Install-CoreMCPPackage -PythonCmd $PythonCmd
  if (-not $mcpSuccess) {
    Write-Error "Failed to install MCP SDK"
  }
    
  # Install core dependencies
  Write-Step "Installing core dependencies..."
  $coreSuccess = Install-PackagesWithFallback -Packages $CoreDependencies -PythonCmd $PythonCmd -GroupName "core dependencies"
  if ($coreSuccess) {
    Write-Success "Core dependencies installed successfully"
  } else {
    Write-Error "Failed to install some core dependencies"
  }
    
  # Install optional dependencies
  if (-not $SkipOptional) {
    Write-Step "Installing optional dependencies for enhanced functionality..."
    Write-Step "Installing optional dependencies..."
    $optionalSuccess = Install-PackagesWithFallback -Packages ($PerformanceDependencies + $ExampleDependencies) -PythonCmd $PythonCmd -GroupName "optional dependencies"
    if ($optionalSuccess) {
      Write-Success "Optional dependencies installed successfully"
    } else {
      Write-Warning "Some optional dependencies failed to install - examples may not work fully"
    }
  } else {
    Write-Step "Skipping optional dependencies"
  }
}

function Set-PlatformOptimizations {
  param([string]$PythonCmd)
    
  Write-Section "Platform Optimizations"
    
  if ($DevContainer) {
    Write-Step "DevContainer detected - skipping host-specific optimizations"
    return
  }
    
  # Windows-specific optimizations
  if ($IsWindows -or $env:OS -eq 'Windows_NT') {
    Write-Step "Configuring Windows-specific settings..."
        
    # Set environment variables for better performance
    [System.Environment]::SetEnvironmentVariable('PYTHONUNBUFFERED', '1', 'User')
    [System.Environment]::SetEnvironmentVariable('PYTHONDONTWRITEBYTECODE', '1', 'User')
        
    Write-Success "Windows optimizations applied"
  }
    
  # Check for development tools
  $tools = @('git', 'code')
  foreach ($tool in $tools) {
    if (Test-Command $tool) {
      Write-Success "$tool is available"
    } else {
      Write-Warning "$tool not found - consider installing for better development experience"
    }
  }
}

function Test-Installation {
  param([string]$PythonCmd)
    
  Write-Section "Installation Verification"
    
  # Test core MCP imports
  $coreImports = @(
    'mcp',
    'mcp.server.fastmcp',
    'mcp.client.session'
  )
    
  foreach ($import in $coreImports) {
    try {
      $result = & $PythonCmd -c "import $import; print('✓ $import')" 2>&1
      if ($result -match '✓') {
        Write-Success $result
      } else {
        Write-Error "Failed to import $import"
      }
    } catch {
      Write-Error "Exception importing $import`: $_"
    }
  }
    
  # Test optional imports
  if (-not $SkipOptional) {
    Write-Step "Testing optional imports..."
        
    $optionalImports = @{
      'asyncpg'       = 'PostgreSQL async support'
      'httpx_sse'     = 'Server-Sent Events support'
      'sse_starlette' = 'SSE server support'
      'pydantic_ai'   = 'AI integration support'
      'orjson'        = 'High-performance JSON'
      'lz4.frame'     = 'LZ4 compression'
    }
    
    # Add uvloop only for non-Windows platforms
    if (-not $IsWindowsPlatform) {
      $optionalImports['uvloop'] = 'High-performance event loop (Unix only)'
    } else {
      Write-Step "uvloop - Skipped (Windows not supported)"
    }
        
    foreach ($import in $optionalImports.Keys) {
      try {
        $result = & $PythonCmd -c "import $import; print('Available')" 2>&1
        if ($result -contains 'Available') {
          Write-Success "$($optionalImports[$import]) - Available"
        } else {
          Write-Warning "$($optionalImports[$import]) - Not available"
        }
      } catch {
        Write-Warning "$($optionalImports[$import]) - Not available"
      }
    }
  }
}

function Show-Summary {
  Write-Section "Setup Complete"
    
  $pythonCmd = Get-PythonExecutable
  $pythonVersion = if ($pythonCmd) { & $pythonCmd --version 2>&1 } else { "Not found" }
    
  Write-Host @"
🎉 MCP Python SDK setup completed successfully!

Next steps:
1. Try running an example:
   python examples/fastmcp/echo.py

2. Start development:
   mcp dev examples/fastmcp/echo.py

3. Run tests:
   pytest tests/

4. Check the documentation:
   - README.md for getting started
   - docs/ for detailed API documentation

Environment details:
- Project root: $ProjectRoot
- Platform: $(if ($IsWindowsPlatform) { 'Windows' } else { 'Unix-like' })
- Python: $pythonVersion
- Package manager: $(if (Test-Command 'uv') { 'uv (recommended)' } else { 'pip' })
- Build tools: $(if ($IsWindowsPlatform -and -not $SkipBuildTools) { if (Test-BuildTools) { 'Available' } else { 'Not found - may cause compilation issues' } } else { 'Not required' })

"@ -ForegroundColor Green
    
  if ($SkipOptional) {
    Write-Warning "Optional dependencies were skipped. Run without -SkipOptional for full functionality."
  }
    
  if ($IsWindowsPlatform -and -not (Test-BuildTools) -and -not $SkipBuildTools) {
    Write-Warning @"
Microsoft Visual C++ Build Tools not found. Some packages requiring compilation may fail.
Consider installing from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
"@
  }
}

# Main execution
try {
  Write-Host "MCP Python SDK Setup Script" -ForegroundColor Magenta
  Write-Host "PowerShell $($PSVersionTable.PSVersion)" -ForegroundColor Gray
  Write-Host "Platform: $(if ($IsWindowsPlatform) { 'Windows' } else { 'Unix-like' })" -ForegroundColor Gray
    
  Initialize-Environment
  $pythonCmd = Test-PythonEnvironment
  Install-Dependencies -PythonCmd $pythonCmd
  Set-PlatformOptimizations -PythonCmd $pythonCmd
  Test-Installation -PythonCmd $pythonCmd
  Show-Summary
} catch {
  Write-Error "Setup failed: $_"
  Write-Host "Stack trace:" -ForegroundColor Red
  Write-Host $_.ScriptStackTrace -ForegroundColor Red
  exit 1
}
