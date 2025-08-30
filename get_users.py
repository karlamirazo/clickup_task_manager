import asyncio
import aiohttp
import json

async def get_clickup_users():
    api_token = 'pk_156221125_GI1OKEUEW57LFWA8RYWHGIC54TL6XVVZ'
    workspace_id = '9014943317'
    base_url = 'https://api.clickup.com/api/v2'
    
    headers = {
        'Authorization': api_token,
        'Content-Type': 'application/json'
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            # Primero intentar obtener el workspace/team info
            url = f'{base_url}/team/{workspace_id}'
            print(f'🔍 Consultando workspace: {url}')
            
            async with session.get(url, headers=headers) as response:
                print(f'📊 Status: {response.status}')
                
                if response.status == 200:
                    data = await response.json()
                    print(f'✅ Workspace encontrado: {data.get("team", {}).get("name")}')
                    
                    # Ahora intentar obtener miembros del workspace
                    members_url = f'{base_url}/team'  # Obtener todos los teams del usuario
                    print(f'🔍 Consultando teams: {members_url}')
                    
                    async with session.get(members_url, headers=headers) as teams_response:
                        if teams_response.status == 200:
                            teams_data = await teams_response.json()
                            print(f'📊 Teams response: {json.dumps(teams_data, indent=2)}')
                            
                            # Buscar nuestro workspace específico
                            if 'teams' in teams_data:
                                for team in teams_data['teams']:
                                    if team.get('id') == workspace_id:
                                        print(f'✅ Team encontrado: {team.get("name")}')
                                        
                                        # Obtener miembros
                                        if 'members' in team:
                                            members = team['members']
                                            print(f'👥 Usuarios encontrados: {len(members)}')
                                            
                                            print('\n📋 LISTA DE USUARIOS:')
                                            for member in members:
                                                user = member.get('user', {})
                                                user_id = user.get('id')
                                                username = user.get('username')
                                                email = user.get('email')
                                                print(f'  - ID: {user_id}')
                                                print(f'    Username: {username}')  
                                                print(f'    Email: {email}')
                                                print('    ---')
                                            
                                            # Generar mapeo para user_mapping_config.py
                                            print('\n🔧 MAPEO PARA user_mapping_config.py:')
                                            print('CLICKUP_USER_MAPPING = {')
                                            for member in members:
                                                user = member.get('user', {})
                                                user_id = user.get('id')
                                                username = user.get('username', 'Usuario')
                                                print(f'    "{user_id}": "{username}",')
                                            print('}')
                                            break
                        else:
                            error_text = await teams_response.text()
                            print(f'❌ Error obteniendo teams {teams_response.status}: {error_text}')
                    
                else:
                    error_text = await response.text()
                    print(f'❌ Error {response.status}: {error_text}')
                    
        except Exception as e:
            print(f'❌ Error de conexión: {e}')

if __name__ == "__main__":
    asyncio.run(get_clickup_users())
