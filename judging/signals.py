"""
Señales para actualización automática de calificaciones y rankings.
Este módulo asegura que los cálculos FEI y los rankings se actualicen automáticamente.
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db import transaction
import logging

from .models import Score, Ranking, FirebaseSync

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Score)
def update_ranking_on_score_change(sender, instance, created, **kwargs):
    """
    Actualiza el ranking cuando se guarda una calificación.
    
    Args:
        sender: Modelo que envía la señal
        instance: Instancia del modelo guardada
        created: Si la instancia fue creada o actualizada
    """
    try:
        # Evitar recursión infinita si estamos dentro de otra transacción
        if hasattr(transaction, 'get_autocommit') and not transaction.get_autocommit():
            return
        
        # Obtener IDs necesarios
        competition_id = instance.competition_id
        participant_id = instance.participant_id
        
        # Actualizar ranking para este participante
        with transaction.atomic():
            # Calcular ranking del participante
            Ranking.calculate_for_participant(competition_id, participant_id)
            
            # Actualizar posiciones de todos los participantes
            Ranking.update_positions(competition_id)
            
            # Marcar para sincronización con Firebase
            FirebaseSync.objects.update_or_create(
                competition_id=competition_id,
                defaults={'is_synced': False}
            )
        
        # Intentar sincronizar con Firebase
        try:
            from .firebase import sync_participant_scores, sync_rankings
            
            # Sincronizar la calificación específica
            sync_participant_scores(competition_id, participant_id, instance.judge_id)
            
            # Sincronizar rankings
            sync_rankings(competition_id)
            
            # Marcar como sincronizado
            FirebaseSync.objects.update_or_create(
                competition_id=competition_id,
                defaults={'is_synced': True, 'error_message': None}
            )
        except Exception as e:
            logger.error(f"Error al sincronizar con Firebase: {e}")
            
            # Registrar error pero no propagarlo
            FirebaseSync.objects.update_or_create(
                competition_id=competition_id,
                defaults={'is_synced': False, 'error_message': str(e)}
            )
    except Exception as e:
        logger.error(f"Error al actualizar ranking después de guardar calificación: {e}")


@receiver(post_delete, sender=Score)
def update_ranking_on_score_delete(sender, instance, **kwargs):
    """
    Actualiza el ranking cuando se elimina una calificación.
    
    Args:
        sender: Modelo que envía la señal
        instance: Instancia del modelo eliminada
    """
    try:
        # Evitar recursión infinita si estamos dentro de otra transacción
        if hasattr(transaction, 'get_autocommit') and not transaction.get_autocommit():
            return
        
        # Obtener IDs necesarios
        competition_id = instance.competition_id
        participant_id = instance.participant_id
        
        # Actualizar ranking para este participante
        with transaction.atomic():
            # Verificar si todavía hay calificaciones para este participante
            has_scores = Score.objects.filter(
                competition_id=competition_id,
                participant_id=participant_id
            ).exists()
            
            if has_scores:
                # Calcular ranking del participante
                Ranking.calculate_for_participant(competition_id, participant_id)
            else:
                # No hay más calificaciones, eliminar ranking
                Ranking.objects.filter(
                    competition_id=competition_id,
                    participant_id=participant_id
                ).delete()
            
            # Actualizar posiciones de todos los participantes
            Ranking.update_positions(competition_id)
            
            # Marcar para sincronización con Firebase
            FirebaseSync.objects.update_or_create(
                competition_id=competition_id,
                defaults={'is_synced': False}
            )
        
        # Intentar sincronizar con Firebase
        try:
            from .firebase import sync_rankings
            
            # Sincronizar rankings
            sync_rankings(competition_id)
            
            # Marcar como sincronizado
            FirebaseSync.objects.update_or_create(
                competition_id=competition_id,
                defaults={'is_synced': True, 'error_message': None}
            )
        except Exception as e:
            logger.error(f"Error al sincronizar con Firebase después de eliminar calificación: {e}")
            
            # Registrar error pero no propagarlo
            FirebaseSync.objects.update_or_create(
                competition_id=competition_id,
                defaults={'is_synced': False, 'error_message': str(e)}
            )
    except Exception as e:
        logger.error(f"Error al actualizar ranking después de eliminar calificación: {e}")


def connect_signals():
    """
    Conecta todas las señales. Llamar desde apps.py ready().
    """
    logger.info("Conectando señales para actualizaciones automáticas FEI")
    # Las señales ya se conectan automáticamente por los decoradores @receiver


def disconnect_signals():
    """
    Desconecta todas las señales. Útil para pruebas o migraciones.
    """
    logger.info("Desconectando señales para actualizaciones automáticas FEI")
    post_save.disconnect(update_ranking_on_score_change, sender=Score)
    post_delete.disconnect(update_ranking_on_score_delete, sender=Score)