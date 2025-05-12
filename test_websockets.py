import asyncio
import websockets
import json

async def test_websocket_connection():
    """Prueba la conexión WebSocket para rankings"""
    
    print("=== Prueba de Conexión WebSocket para Rankings ===")
    
    try:
        # Conectar al WebSocket
        uri = "ws://127.0.0.1:8000/ws/rankings/1/"
        async with websockets.connect(uri) as websocket:
            print("Conexión establecida exitosamente!")
            
            # Solicitar rankings actuales
            print("\nSolicitando rankings actuales...")
            await websocket.send(json.dumps({
                "type": "request_rankings"
            }))
            
            # Recibir respuesta (con timeout de 5 segundos)
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                data = json.loads(response)
                
                # Verificar respuesta
                if data["type"] == "current_rankings":
                    print("Respuesta recibida correctamente!")
                    print(f"Tipo de mensaje: {data['type']}")
                    print(f"Rankings recibidos: {len(data.get('rankings', []))}")
                    
                    # Mostrar algunos datos
                    rankings = data.get('rankings', [])
                    if rankings:
                        print("\nDatos de rankings:")
                        for i, ranking in enumerate(rankings[:3]):  # Mostrar máximo 3
                            print(f"{i+1}. Posición: {ranking.get('position')}, " +
                                f"Porcentaje: {ranking.get('percentage')}%, " +
                                f"Jinete: {ranking.get('rider', {}).get('name', 'Desconocido')}")
                    else:
                        print("No se recibieron rankings.")
                else:
                    print(f"Respuesta inesperada: {data}")
            except asyncio.TimeoutError:
                print("Error: Timeout esperando respuesta del servidor")
                return False
            except Exception as e:
                print(f"Error recibiendo datos: {str(e)}")
                return False
    except Exception as e:
        print(f"Error conectando al WebSocket: {str(e)}")
        return False
    
    return True

async def run_tests():
    """Ejecuta todas las pruebas de WebSocket"""
    success = await test_websocket_connection()
    print("\nResumen de las pruebas:")
    print(f"- Conexión WebSocket para rankings: {'✓ ÉXITO' if success else '✗ FALLÓ'}")

if __name__ == "__main__":
    # Ejecutar pruebas de WebSocket
    asyncio.run(run_tests())