# FakeNewsChek — Détecteur de Fake News Sanitaires
### Swahili 🇹🇿 & Haoussa 🇳🇬 | Powered by AfriBERTa

---

## Structure du projet

```
fake_news_project/
├── manage.py
├── requirements.txt
├── model/
│   ├── fake_news_model/    
│   ├── tokenizer/         
│   └── predict.py
├── notebooks/
│   └── fine_tuning_afriberta.ipynb
├── dataset/
│   ├── train.csv
│   └── test.csv
├── fake_news_project/
│   ├── settings.py
│   ├── urls.py
│   └── ...
├── detector/
│   └── ...
└── media/
```

---

## Lancement rapide

### 1. Créer l'environnement virtuel

```bash
cd fake_news_project
python -m venv venv

# Linux/macOS
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 2. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 3. Appliquer les migrations Django

```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Créer un super-utilisateur (optionnel)

```bash
python manage.py createsuperuser
```

### 5. Collecter les fichiers statiques

```bash
python manage.py collectstatic --noinput
```

### 6. Lancer le serveur

```bash
python manage.py runserver
```

Accéder à : http://127.0.0.1:8000

---

## Fine-tuner le modèle AfriBERTa

1. Préparez vos données dans `dataset/train.csv` et `dataset/test.csv`
   - Colonnes requises : `text`, `label` (`real`/`fake`), `language` (`sw`/`ha`)

2. Ouvrez `notebooks/fine_tuning_afriberta.ipynb` dans Jupyter

3. Exécutez toutes les cellules

4. Le modèle sera sauvegardé automatiquement dans `model/fake_news_model/` et `model/tokenizer/`

---

## API REST

```bash
curl -X POST http://127.0.0.1:8000/api/analyze/ \
  -H "Content-Type: application/json" \
  -d '{"text": "Chanjo ya COVID-19 inasaidia", "language": "sw"}'
```

Réponse :
```json
{
  "label": "VRAIE",
  "is_fake": false,
  "confidence": 87.3,
  "prob_vraie": 87.3,
  "prob_fausse": 12.7,
  "language": "sw",
  "demo_mode": false
}
```

---

## Mode démonstration

Si aucun modèle n'est présent dans `model/fake_news_model/`, l'application
fonctionne en **mode démonstration** avec des prédictions simulées.
Un bandeau orange vous en informe sur la page de résultats.

---

## Technologies

- **Django 4.2** — Framework web
- **AfriBERTa** — Modèle de langue africain (Hugging Face)
- **PyTorch** — Backend deep learning
- **SQLite** — Base de données (dev)
