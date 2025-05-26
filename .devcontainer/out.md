
2) main.sh
────────────────────────────────────────────────────────────────────────────


# Run if executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi

────────────────────────────────────────────────────────────────────────────
3) registry.sh
────────────────────────────────────────────────────────────────────────────


────────────────────────────────────────────────────────────────────────────
4) types.sh
────────────────────────────────────────────────────────────────────────────


────────────────────────────────────────────────────────────────────────────
5) utils.sh
────────────────────────────────────────────────────────────────────────────


────────────────────────────────────────────────────────────────────────────

All five files above should now pass a typical ShellCheck run without disabling any warnings, and with corrected code to avoid the usual issues (unused variables, masked return values, unverified sourcing paths, etc.). They are ready for production scenarios where multiple scripts source and rely on these definitions and utilities.