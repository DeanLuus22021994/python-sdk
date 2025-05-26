@echo off
REM Main Orchestrator Windows Entry Point
REM This is a Windows batch file that delegates to the bash orchestrator

echo === MCP Python SDK Orchestrator - Windows Entry Point ===

REM Check if bash exists
where bash > nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Error: Bash is required but not found in PATH
    exit /b 1
)

REM Execute the main orchestrator script
echo Delegating to bash orchestrator...
bash -c "cd %~dp0 && ./master-orchestrator.sh %*"
