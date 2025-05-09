# backend/rankings/models.py

from django.db import models
from competencias.models import Competencia, Categoria, Inscripcion

class Ranking(models.Model):
    """
    Modelo para almacenar los rankings generados para una categoría de competencia.
    """
    TIPO_CHOICES = [
        ('preliminar', 'Preliminar'),
        ('final', 'Final'),
    ]
    
    competencia = models.ForeignKey(
        Competencia, 
        on_delete=models.CASCADE, 
        related_name='rankings',
        verbose_name="Competencia"
    )
    categoria = models.ForeignKey(
        Categoria, 
        on_delete=models.CASCADE, 
        related_name='rankings',
        verbose_name="Categoría"
    )
    tipo = models.CharField(
        max_length=20, 
        choices=TIPO_CHOICES, 
        default='preliminar',
        verbose_name="Tipo de Ranking"
    )
    fecha_generacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de Generación"
    )
    fecha_publicacion = models.DateTimeField(
        blank=True, 
        null=True,
        verbose_name="Fecha de Publicación"
    )
    publicado = models.BooleanField(
        default=False,
        verbose_name="Publicado"
    )
    descripcion = models.TextField(
        blank=True, 
        null=True,
        verbose_name="Descripción"
    )
    
    class Meta:
        verbose_name = "Ranking"
        verbose_name_plural = "Rankings"
        ordering = ['-fecha_generacion']
        unique_together = ['competencia', 'categoria', 'tipo']
    
    def __str__(self):
        return f"Ranking {self.get_tipo_display()} - {self.categoria.nombre} - {self.competencia.nombre}"
    
    def generar_resultados(self):
        """
        Genera los resultados del ranking basados en las evaluaciones.
        Calcula los puntajes finales y las posiciones.
        """
        from django.db.models import Avg, Count, F
        
        # Obtener inscripciones con evaluaciones completadas para esta categoría
        inscripciones = Inscripcion.objects.filter(
            competencia=self.competencia,
            categoria=self.categoria,
            estado='completada',
            evaluaciones__estado='completada'
        ).distinct()
        
        # Para cada inscripción, calcular el puntaje promedio
        resultados = []
        for inscripcion in inscripciones:
            # Obtener el promedio de puntajes de todas las evaluaciones para esta inscripción
            puntaje_promedio = inscripcion.evaluaciones.filter(
                estado='completada'
            ).aggregate(
                promedio=Avg('puntaje_total')
            )['promedio'] or 0
            
            resultados.append({
                'inscripcion': inscripcion,
                'puntaje': round(puntaje_promedio, 2)
            })
        
        # Ordenar resultados por puntaje (descendente)
        resultados_ordenados = sorted(resultados, key=lambda x: x['puntaje'], reverse=True)
        
        # Crear o actualizar los registros de ResultadoRanking
        self.resultados.all().delete()  # Eliminar resultados anteriores
        
        for posicion, resultado in enumerate(resultados_ordenados, 1):
            ResultadoRanking.objects.create(
                ranking=self,
                inscripcion=resultado['inscripcion'],
                posicion=posicion,
                puntaje=resultado['puntaje']
            )
    
    def publicar(self):
        """
        Publica el ranking y actualiza la fecha de publicación.
        """
        from django.utils import timezone
        
        self.publicado = True
        self.fecha_publicacion = timezone.now()
        self.save(update_fields=['publicado', 'fecha_publicacion'])

class ResultadoRanking(models.Model):
    """
    Modelo para almacenar los resultados individuales dentro de un ranking.
    """
    ranking = models.ForeignKey(
        Ranking, 
        on_delete=models.CASCADE, 
        related_name='resultados',
        verbose_name="Ranking"
    )
    inscripcion = models.ForeignKey(
        Inscripcion, 
        on_delete=models.CASCADE, 
        related_name='resultados_ranking',
        verbose_name="Inscripción"
    )
    posicion = models.PositiveIntegerField(verbose_name="Posición")
    puntaje = models.DecimalField(
        max_digits=6, 
        decimal_places=2,
        verbose_name="Puntaje"
    )
    medalla = models.CharField(
        max_length=20, 
        blank=True, 
        null=True,
        verbose_name="Medalla/Reconocimiento"
    )
    comentario = models.TextField(
        blank=True, 
        null=True,
        verbose_name="Comentario"
    )
    
    class Meta:
        verbose_name = "Resultado de Ranking"
        verbose_name_plural = "Resultados de Ranking"
        ordering = ['ranking', 'posicion']
        unique_together = ['ranking', 'inscripcion']
    
    def __str__(self):
        return f"{self.posicion}° lugar - {self.inscripcion.jinete.usuario.get_full_name()} con {self.inscripcion.caballo.nombre}"

class Certificado(models.Model):
    """
    Modelo para almacenar los certificados de participación y premiación.
    """
    TIPO_CHOICES = [
        ('participacion', 'Participación'),
        ('premiacion', 'Premiación'),
    ]
    
    resultado = models.OneToOneField(
        ResultadoRanking, 
        on_delete=models.CASCADE, 
        related_name='certificado',
        verbose_name="Resultado de Ranking"
    )
    tipo = models.CharField(
        max_length=20, 
        choices=TIPO_CHOICES, 
        default='participacion',
        verbose_name="Tipo de Certificado"
    )
    codigo = models.CharField(
        max_length=50, 
        unique=True,
        verbose_name="Código de Verificación"
    )
    fecha_generacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de Generación"
    )
    archivo = models.FileField(
        upload_to='certificados/', 
        blank=True, 
        null=True,
        verbose_name="Archivo PDF"
    )
    
    class Meta:
        verbose_name = "Certificado"
        verbose_name_plural = "Certificados"
        ordering = ['-fecha_generacion']
    
    def __str__(self):
        return f"Certificado de {self.get_tipo_display()} - {self.resultado.inscripcion.jinete.usuario.get_full_name()}"
    
    def save(self, *args, **kwargs):
        """
        Sobrescribir save para generar código único si no existe.
        """
        if not self.codigo:
            import uuid
            self.codigo = uuid.uuid4().hex[:10].upper()
        
        super().save(*args, **kwargs)
    
    def generar_pdf(self):
        """
        Genera el archivo PDF del certificado.
        Esta función se implementará con una biblioteca de generación de PDF.
        """
        # Implementación futura con ReportLab, WeasyPrint u otra biblioteca
        pass