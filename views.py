import sys
import os
import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages

from .forms import NewsAnalysisForm, FeedbackForm
from .models import Prediction, FeedbackReport

logger = logging.getLogger(__name__)


def _get_predictor():
    """Importe et retourne le prédicteur (avec le bon path)."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    model_dir = os.path.join(base_dir, 'model')
    if model_dir not in sys.path:
        sys.path.insert(0, model_dir)
    from predict import predict_text
    return predict_text


def index(request):
    """Page d'accueil avec le formulaire d'analyse."""
    form = NewsAnalysisForm()
    recent_predictions = Prediction.objects.all()[:5]
    stats = {
        'total': Prediction.objects.count(),
        'fake': Prediction.objects.filter(is_fake=True).count(),
        'real': Prediction.objects.filter(is_fake=False).count(),
        'swahili': Prediction.objects.filter(language='sw').count(),
        'haoussa': Prediction.objects.filter(language='ha').count(),
    }
    return render(request, 'detector/index.html', {
        'form': form,
        'recent_predictions': recent_predictions,
        'stats': stats,
    })


@require_http_methods(["POST"])
def analyze(request):
    """Traite le formulaire et retourne le résultat d'analyse."""
    form = NewsAnalysisForm(request.POST)

    if not form.is_valid():
        return render(request, 'detector/index.html', {
            'form': form,
            'error': 'Formulaire invalide. Veuillez vérifier vos données.',
        })

    text = form.cleaned_data['text']
    language = form.cleaned_data['language']

    try:
        predict_text = _get_predictor()
        result = predict_text(text, language)
    except Exception as e:
        logger.error("Erreur lors de l'appel au prédicteur: %s", str(e))
        result = {
            'error': 'Le module de prédiction est indisponible.',
            'label': None,
            'confidence': 0,
        }

    if result.get('error'):
        messages.error(request, result['error'])
        return redirect('index')

    # Sauvegarde en base
    prediction = Prediction.objects.create(
        text=text,
        language=language,
        label=result['label'],
        is_fake=result['is_fake'],
        confidence=result['confidence'],
        prob_vraie=result.get('prob_vraie', 0),
        prob_fausse=result.get('prob_fausse', 0),
        demo_mode=result.get('demo_mode', False),
    )

    return render(request, 'detector/result.html', {
        'prediction': prediction,
        'result': result,
        'text': text,
        'language': language,
        'language_name': 'Swahili' if language == 'sw' else 'Haoussa',
        'feedback_form': FeedbackForm(),
    })


@require_http_methods(["POST"])
def api_analyze(request):
    """Endpoint API JSON pour l'analyse de texte."""
    import json
    try:
        data = json.loads(request.body)
        text = data.get('text', '').strip()
        language = data.get('language', 'sw')

        if not text:
            return JsonResponse({'error': 'Le champ texte est requis.'}, status=400)

        if language not in ('sw', 'ha'):
            return JsonResponse({'error': 'Langue non supportée. Utilisez sw ou ha.'}, status=400)

        predict_text = _get_predictor()
        result = predict_text(text, language)
        return JsonResponse(result)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON invalide.'}, status=400)
    except Exception as e:
        logger.error("Erreur API: %s", str(e))
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["POST"])
def submit_feedback(request, prediction_id):
    """Enregistre un signalement utilisateur."""
    prediction = get_object_or_404(Prediction, pk=prediction_id)
    form = FeedbackForm(request.POST)

    if form.is_valid():
        FeedbackReport.objects.create(
            prediction=prediction,
            user_comment=form.cleaned_data.get('comment', ''),
        )
        messages.success(request, 'Merci pour votre signalement !')
    else:
        messages.error(request, 'Erreur lors du signalement.')

    return redirect('index')


def history(request):
    """Historique des analyses."""
    predictions = Prediction.objects.all()
    return render(request, 'detector/history.html', {
        'predictions': predictions,
    })
