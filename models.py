from django.db import models
from django.utils import timezone


class Prediction(models.Model):
    """Enregistre chaque analyse effectuée par l'utilisateur."""

    LANGUAGE_CHOICES = [
        ('sw', 'Swahili'),
        ('ha', 'Haoussa'),
    ]

    text = models.TextField(verbose_name="Texte analysé")
    language = models.CharField(
        max_length=2,
        choices=LANGUAGE_CHOICES,
        default='sw',
        verbose_name="Langue"
    )
    label = models.CharField(max_length=10, verbose_name="Résultat")
    is_fake = models.BooleanField(verbose_name="Est une fake news ?")
    confidence = models.FloatField(verbose_name="Confiance (%)")
    prob_vraie = models.FloatField(default=0.0, verbose_name="Probabilité vraie (%)")
    prob_fausse = models.FloatField(default=0.0, verbose_name="Probabilité fausse (%)")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Date d'analyse")
    demo_mode = models.BooleanField(default=False, verbose_name="Mode démonstration")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Prédiction"
        verbose_name_plural = "Prédictions"

    def __str__(self):
        lang = dict(self.LANGUAGE_CHOICES).get(self.language, self.language)
        return f"[{lang}] {self.label} ({self.confidence}%) — {self.created_at.strftime('%d/%m/%Y %H:%M')}"


class FeedbackReport(models.Model):
    """Permet aux utilisateurs de signaler des erreurs de classification."""

    prediction = models.ForeignKey(
        Prediction,
        on_delete=models.CASCADE,
        related_name='feedbacks'
    )
    user_comment = models.TextField(verbose_name="Commentaire", blank=True)
    reported_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Signalement"
        verbose_name_plural = "Signalements"

    def __str__(self):
        return f"Signalement #{self.id} — Prédiction #{self.prediction_id}"
