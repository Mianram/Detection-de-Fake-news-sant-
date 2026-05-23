"""
Module de prédiction pour la détection de fake news
en Swahili et Haoussa avec AfriBERTa.
"""

import os
import torch
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class FakeNewsPredictor:
    """
    Classe principale pour la détection de fake news.
    Utilise le modèle AfriBERTa fine-tuné sur des données
    en swahili et haoussa dans le domaine sanitaire.
    Implémente le patron Singleton : le modèle n'est chargé qu'une seule fois.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.model      = None
        self.tokenizer  = None
        self.device     = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.labels     = {0: 'VRAIE', 1: 'FAUSSE'}
        self.demo_mode  = False
        self._initialized = True

        self._load_model()

    def _load_model(self):
        """Charge le modèle et le tokenizer depuis le disque."""

        # Chemin absolu : on remonte de model/ vers la racine du projet
        base_dir       = Path(__file__).resolve().parent.parent
        model_path     = base_dir / 'model' / 'fake_news_model'
        tokenizer_path = base_dir / 'model' / 'tokenizer'

        # Vérifie que les dossiers existent et ne sont pas vides
        model_ok     = model_path.exists()     and any(model_path.iterdir())
        tokenizer_ok = tokenizer_path.exists() and any(tokenizer_path.iterdir())

        if not model_ok or not tokenizer_ok:
            logger.warning(
                "Modèle ou tokenizer introuvable.\n"
                "  → model      : %s (trouvé: %s)\n"
                "  → tokenizer  : %s (trouvé: %s)\n"
                "Passage en MODE DÉMONSTRATION.",
                model_path, model_ok,
                tokenizer_path, tokenizer_ok,
            )
            self.demo_mode = True
            return

        try:
            from transformers import AutoTokenizer, AutoModelForSequenceClassification

            logger.info("Chargement du tokenizer depuis %s ...", tokenizer_path)
            self.tokenizer = AutoTokenizer.from_pretrained(str(tokenizer_path))

            logger.info("Chargement du modèle depuis %s ...", model_path)
            self.model = AutoModelForSequenceClassification.from_pretrained(
                str(model_path)
            )
            self.model.to(self.device)
            self.model.eval()

            self.demo_mode = False
            logger.info("✅ Modèle chargé avec succès sur %s", self.device)

        except Exception as exc:
            logger.error("Erreur lors du chargement du modèle : %s", exc)
            self.demo_mode = True

    # ─────────────────────────────────────────────────────────
    def predict(self, text: str, language: str = 'sw') -> dict:
        """
        Prédit si un texte est une fake news ou non.

        Args:
            text     : Le texte à analyser (swahili ou haoussa)
            language : 'sw' pour Swahili, 'ha' pour Haoussa

        Returns:
            dict avec les clés :
              label        – 'VRAIE' ou 'FAUSSE'
              is_fake      – bool
              confidence   – float (0-100)
              prob_vraie   – float (0-100)
              prob_fausse  – float (0-100)
              language     – 'sw' ou 'ha'
              demo_mode    – bool
        """
        if not text or not text.strip():
            return {
                'error'      : 'Le texte ne peut pas être vide.',
                'label'      : None,
                'confidence' : 0,
            }

        if self.demo_mode:
            return self._demo_predict(text, language)

        try:
            inputs = self.tokenizer(
                text,
                return_tensors='pt',
                max_length=512,
                truncation=True,
                padding=True,
            ).to(self.device)

            with torch.no_grad():
                outputs      = self.model(**inputs)
                probabilities = torch.softmax(outputs.logits, dim=-1).squeeze()

            pred_idx   = torch.argmax(probabilities).item()
            confidence = probabilities[pred_idx].item()

            return {
                'label'      : self.labels[pred_idx],
                'is_fake'    : pred_idx == 1,
                'confidence' : round(confidence * 100, 2),
                'prob_vraie' : round(probabilities[0].item() * 100, 2),
                'prob_fausse': round(probabilities[1].item() * 100, 2),
                'language'   : language,
                'demo_mode'  : False,
            }

        except Exception as exc:
            logger.error("Erreur lors de la prédiction : %s", exc)
            return {
                'error'      : f'Erreur de prédiction : {exc}',
                'label'      : None,
                'confidence' : 0,
            }

    # ─────────────────────────────────────────────────────────
    def _demo_predict(self, text: str, language: str) -> dict:
        """
        Mode démonstration : prédiction simulée par heuristiques simples.
        Activé automatiquement si le modèle n'est pas disponible.
        """
        import random
        import hashlib

        seed = int(hashlib.md5(text.encode()).hexdigest(), 16) % 1000
        random.seed(seed)

        fake_keywords = {
            'sw': ['tiba ya ajabu', 'dawa ya haraka', 'ponya', 'siri kubwa'],
            'ha': ['magani mai ban mamaki', 'warkar nan take', 'karya', 'ba tabbas'],
        }

        text_lower   = text.lower()
        keywords     = fake_keywords.get(language, [])
        is_suspicious = any(kw in text_lower for kw in keywords)

        prob_fake = random.uniform(0.70, 0.95) if is_suspicious \
                    else random.uniform(0.10, 0.45)
        prob_real = 1.0 - prob_fake
        is_fake   = prob_fake > 0.5

        return {
            'label'      : 'FAUSSE' if is_fake else 'VRAIE',
            'is_fake'    : is_fake,
            'confidence' : round(max(prob_fake, prob_real) * 100, 2),
            'prob_vraie' : round(prob_real * 100, 2),
            'prob_fausse': round(prob_fake * 100, 2),
            'language'   : language,
            'demo_mode'  : True,
        }


# ── Instance globale (chargée une seule fois au démarrage) ───
predictor = FakeNewsPredictor()


def predict_text(text: str, language: str = 'sw') -> dict:
    """Point d'entrée public utilisé par views.py."""
    return predictor.predict(text, language)