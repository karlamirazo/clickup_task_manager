@echo off
echo Subiendo solucion OAuth simplificada...
git add app/main.py
git commit -m "Simplified OAuth solution that works"
git push origin master
echo ¡Listo! Espera 2-3 minutos para que Railway despliegue
echo Luego prueba: https://clickuptaskmanager-production.up.railway.app
pause
