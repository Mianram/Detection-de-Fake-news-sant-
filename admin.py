from django.contrib import admin
from .models import Prediction, FeedbackReport


@admin.register(Prediction)
class PredictionAdmin(admin.ModelAdmin):
    list_display = ['id', 'language', 'label', 'confidence', 'is_fake', 'demo_mode', 'created_at']
    list_filter = ['language', 'is_fake', 'demo_mode', 'created_at']
    search_fields = ['text']
    readonly_fields = ['created_at']
    ordering = ['-created_at']


@admin.register(FeedbackReport)
class FeedbackReportAdmin(admin.ModelAdmin):
    list_display = ['id', 'prediction', 'reported_at']
    list_filter = ['reported_at']
    ordering = ['-reported_at']
