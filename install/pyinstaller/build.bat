REM Simplify executing pyinstaller
REM
REM License: MIT (see license.txt)
REM THIS PROGRAM COMES WITH NO WARRANTY

pyinstaller --noconfirm ^
            --clean ^
            --onedir ^
            --additional-hooks-dir=install/pyinstaller/hooks ^
            install\pyinstaller\wxglade.spec
