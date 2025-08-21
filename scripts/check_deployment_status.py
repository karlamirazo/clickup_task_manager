#!/usr/bin/env python3
"""
Script para verificar el estado del deployment
"""

import asyncio
import aiohttp
import json

async def check_deployment_status():
    """Verificar el estado del deployment"""
    
    print("ğŸ”� VERIFICANDO ESTADO DEL DEPLOYMENT")
    print("=" * 50)
    
    # URL de la API
    base_url = "https://clickuptaskmanager-production.up.railway.app"
    
    try:
        async with aiohttp.ClientSession() as session:
            # Test endpoint basico
            print("ğŸ“¡ Probando endpoint basico...")
            async with session.get(f"{base_url}/") as response:
                print(f"ğŸ“¡ Status: {response.status}")
                response_text = await response.text()
                print(f"ğŸ“„ Respuesta: {response_text[:200]}...")
                
                if response.status == 200:
                    print("âœ… Endpoint basico funciona")
                else:
                    print("â�Œ Endpoint basico no funciona")
            
            # Test endpoint de health check
            print(f"\nğŸ“¡ Probando health check...")
            async with session.get(f"{base_url}/health") as response:
                print(f"ğŸ“¡ Status: {response.status}")
                response_text = await response.text()
                print(f"ğŸ“„ Respuesta: {response_text}")
                
                if response.status == 200:
                    print("âœ… Health check funciona")
                else:
                    print("â�Œ Health check no funciona")
            
            # Test endpoint de debug
            print(f"\nğŸ“¡ Probando endpoint de debug...")
            async with session.get(f"{base_url}/debug") as response:
                print(f"ğŸ“¡ Status: {response.status}")
                response_text = await response.text()
                print(f"ğŸ“„ Respuesta: {response_text[:200]}...")
                
                if response.status == 200:
                    print("âœ… Endpoint de debug funciona")
                else:
                    print("â�Œ Endpoint de debug no funciona")
            
            # Test endpoint de tareas
            print(f"\nğŸ“¡ Probando endpoint de tareas...")
            async with session.get(f"{base_url}/api/v1/tasks") as response:
                print(f"ğŸ“¡ Status: {response.status}")
                response_text = await response.text()
                print(f"ğŸ“„ Respuesta: {response_text[:200]}...")
                
                if response.status == 200:
                    print("âœ… Endpoint de tareas funciona")
                else:
                    print("â�Œ Endpoint de tareas no funciona")
    
    except Exception as e:
        print(f"â�Œ Error: {e}")

if __name__ == "__main__":
    asyncio.run(check_deployment_status())
