@echo off
echo Desplegando aplicacion universal OAuth...
git add .
git commit -m "Universal OAuth handler - captures ALL ClickUp redirects"
git push origin master
echo.
echo ¡Desplegado! Espera 3 minutos y prueba:
echo https://ctm-pro.up.railway.app
echo.
echo Esta version captura TODAS las redirecciones de ClickUp
pause
