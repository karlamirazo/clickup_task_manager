@echo off
echo Desplegando solucion final OAuth...
git add app/main.py
git commit -m "Final OAuth solution that works with ClickUp behavior"
git push origin master
echo.
echo ¡Desplegado! Espera 2-3 minutos y prueba:
echo https://ctm-pro.up.railway.app
echo.
echo Esta version maneja correctamente el comportamiento de ClickUp
pause
