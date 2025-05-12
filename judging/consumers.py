"""
Consumidores WebSocket para actualización en tiempo real de calificaciones y rankings.
"""
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import logging

logger = logging.getLogger(__name__)

class ScoreConsumer(AsyncWebsocketConsumer):
    """
    Consumidor para actualizaciones en tiempo real de calificaciones.
    """
    
    async def connect(self):
        # Obtener ID de competencia de la URL
        self.competition_id = self.scope['url_route']['kwargs']['competition_id']
        
        # Crear nombre de grupo único para esta competencia
        self.room_group_name = f'rankings_{self.competition_id}'
        
        # Unirse al grupo
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        await self.send_current_rankings()
    
    async def disconnect(self, close_code):
        # Salir del grupo al desconectar
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        """
        Recibir mensaje desde WebSocket
        """
        try:
            data = json.loads(text_data)
            
            # Procesar el mensaje según su tipo
            message_type = data.get('type')
            
            if message_type == 'score_update':
                # Verificar permisos (esto debería ser mejorado en producción)
                # En esta implementación básica, cualquier cliente puede enviar actualizaciones
                await self.update_score(data)
            
            elif message_type == 'request_scores':
                # El cliente solicita datos actuales
                await self.send_current_scores()
                
        except json.JSONDecodeError:
            logger.error(f"Error al decodificar JSON: {text_data}")
        except Exception as e:
            logger.error(f"Error en receive: {e}")
    
    @database_sync_to_async
    def update_score(self, data):
        """
        Actualizar calificación en la base de datos
        """
        from judging.models import Score, CompetitionParameter
        from django.contrib.auth import get_user_model
        
        try:
            User = get_user_model()
            
            judge_id = data.get('judge_id')
            parameter_id = data.get('parameter_id')
            value = data.get('value')
            
            # Validar datos básicos
            if not all([judge_id, parameter_id, value is not None]):
                logger.warning(f"Datos incompletos: {data}")
                return False
            
            # Obtener parámetro de competencia
            parameter = CompetitionParameter.objects.get(
                competition_id=self.competition_id,
                parameter_id=parameter_id
            )
            
            # Obtener juez
            judge = User.objects.get(id=judge_id)
            
            # Actualizar o crear calificación
            score, created = Score.objects.update_or_create(
                competition_id=self.competition_id,
                participant_id=self.participant_id,
                judge=judge,
                parameter=parameter,
                defaults={
                    'value': value,
                    'comments': data.get('comments', ''),
                    'is_edited': data.get('is_edited', False),
                    'edit_reason': data.get('edit_reason', 'Actualización vía WebSocket')
                }
            )
            
            # Notificar a todos los clientes en el grupo
            self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'score_message',
                    'score': {
                        'id': score.id,
                        'judge_id': judge_id,
                        'parameter_id': parameter_id,
                        'value': float(score.value),
                        'calculated_result': float(score.calculated_result),
                        'is_edited': score.is_edited,
                        'updated_at': score.updated_at.isoformat()
                    }
                }
            )
            
            # Actualizar rankings
            from judging.services import update_participant_rankings
            update_participant_rankings(self.competition_id)
            
            # Sincronizar con Firebase
            from judging.firebase import sync_participant_scores
            sync_participant_scores(self.competition_id, self.participant_id, judge_id)
            
            return True
            
        except Exception as e:
            logger.error(f"Error al actualizar calificación: {e}")
            return False
    
    @database_sync_to_async
    def get_current_scores(self):
        """
        Obtener calificaciones actuales para este participante
        """
        from judging.models import Score
        
        # Obtener todas las calificaciones para este participante
        scores = Score.objects.filter(
            competition_id=self.competition_id,
            participant_id=self.participant_id
        ).select_related('judge', 'parameter__parameter')
        
        # Organizar por juez y parámetro
        result = {}
        for score in scores:
            judge_id = str(score.judge_id)
            param_id = str(score.parameter.parameter_id)
            
            if judge_id not in result:
                result[judge_id] = {
                    'name': f"{score.judge.first_name} {score.judge.last_name}",
                    'scores': {}
                }
            
            result[judge_id]['scores'][param_id] = {
                'id': score.id,
                'value': float(score.value),
                'calculated_result': float(score.calculated_result),
                'is_edited': score.is_edited,
                'comments': score.comments,
                'updated_at': score.updated_at.isoformat()
            }
        
        return result
    
    async def send_current_scores(self):
        """
        Enviar calificaciones actuales al cliente
        """
        scores = await self.get_current_scores()
        
        await self.send(text_data=json.dumps({
            'type': 'current_scores',
            'scores': scores
        }))
    
    async def score_message(self, event):
        """
        Enviar actualización de calificación a los clientes WebSocket
        """
        await self.send(text_data=json.dumps({
            'type': 'score_update',
            'score': event['score']
        }))


class RankingConsumer(AsyncWebsocketConsumer):
    """
    Consumidor para actualizaciones en tiempo real de rankings.
    """
    
    async def connect(self):
        # Obtener ID de competencia de la URL
        self.competition_id = self.scope['url_route']['kwargs']['competition_id']
        
        # Crear nombre de grupo único para esta competencia
        self.room_group_name = f'rankings_{self.competition_id}'
        
        # Unirse al grupo
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        await self.send_current_rankings()
    
    async def disconnect(self, close_code):
        # Salir del grupo al desconectar
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """
        Recibir mensaje desde WebSocket
        """
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'request_rankings':
                await self.send_current_rankings()
                
        except Exception as e:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': str(e)
            }))
    
    @database_sync_to_async
    def get_current_rankings(self):
        from judging.models import Ranking
        
        rankings = Ranking.objects.filter(
            competition_id=self.competition_id
        ).select_related(
            'participant', 'participant__rider', 'participant__horse'
        ).order_by('position')
        
        result = []
        for ranking in rankings:
            participant = ranking.participant
            rider = participant.rider
            horse = participant.horse
            
            result.append({
                'id': ranking.id,
                'participant_id': participant.id,
                'position': ranking.position,
                'average': float(ranking.average_score),
                'percentage': float(ranking.percentage),
                'rider': {
                    'id': rider.id,
                    'name': f"{rider.first_name} {rider.last_name}",
                    'nationality': rider.nationality or ''
                },
                'horse': {
                    'id': horse.id,
                    'name': horse.name,
                    'breed': horse.breed or ''
                }
            })
        
        return result
    
    async def send_current_rankings(self):
        """
        Enviar rankings actuales al cliente
        """
        rankings = await self.get_current_rankings()
        
        await self.send(text_data=json.dumps({
            'type': 'current_rankings',
            'rankings': rankings
        }))
    
    async def rankings_update(self, event):
        """
        Enviar actualización de rankings a los clientes WebSocket
        """
        await self.send(text_data=json.dumps({
            'type': 'rankings_update',
            'rankings': event['rankings']
        }))


def notify_rankings_update(competition_id, rankings_data=None):
    """
    Función auxiliar para notificar actualizaciones de rankings desde código síncrono.
    Esta función debe ser llamada después de actualizar rankings en la base de datos.
    
    Ejemplo de uso:
        from judging.consumers import notify_rankings_update
        notify_rankings_update(competition_id)
    """
    from channels.layers import get_channel_layer
    from asgiref.sync import async_to_sync
    
    try:
        # Si no se proporciona data, obtener rankings actuales
        if rankings_data is None:
            from judging.models import Ranking
            
            rankings = Ranking.objects.filter(
                competition_id=competition_id
            ).select_related(
                'participant', 'participant__rider', 'participant__horse'
            ).order_by('position')
            
            # Formatear para enviar por WebSocket
            rankings_data = []
            for ranking in rankings:
                participant = ranking.participant
                rider = participant.rider
                horse = participant.horse
                
                rankings_data.append({
                    'id': ranking.id,
                    'participant_id': participant.id,
                    'position': ranking.position,
                    'average': float(ranking.average_score),
                    'percentage': float(ranking.percentage),
                    'rider': {
                        'id': rider.id,
                        'name': f"{rider.first_name} {rider.last_name}"
                    },
                    'horse': {
                        'id': horse.id,
                        'name': horse.name
                    }
                })
        
        # Enviar actualización a todos los clientes conectados
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'rankings_{competition_id}',
            {
                'type': 'rankings_update',
                'rankings': rankings_data
            }
        )
        
        logger.info(f"Notificación de actualización de rankings enviada: competencia {competition_id}")
        return True
    except Exception as e:
        logger.error(f"Error al notificar actualización de rankings: {e}")
        return False