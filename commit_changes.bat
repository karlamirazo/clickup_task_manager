@echo off
echo Haciendo commit de los cambios...
git add .
git commit -m "Fix OAuth to handle ClickUp URL without https protocol"
git push origin master
echo ¡Cambios subidos exitosamente!
pause
