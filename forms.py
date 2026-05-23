from django import forms


class NewsAnalysisForm(forms.Form):
    """Formulaire principal pour soumettre un texte à analyser."""

    LANGUAGE_CHOICES = [
        ('sw', '🇹🇿 Swahili'),
        ('ha', '🇳🇬 Haoussa'),
    ]

    text = forms.CharField(
        widget=forms.Textarea(attrs={
            'id': 'news-text',
            'placeholder': (
                'Swahili: Bandika habari unayotaka kuchunguza hapa...\n'
                'Haoussa: Rubuta labari da kake son bincika anan...'
            ),
            'rows': 8,
        }),
        label='Texte à analyser',
        min_length=10,
        max_length=5000,
        error_messages={
            'min_length': 'Le texte doit contenir au moins 10 caractères.',
            'max_length': 'Le texte ne doit pas dépasser 5000 caractères.',
            'required': 'Veuillez saisir un texte à analyser.',
        }
    )

    language = forms.ChoiceField(
        choices=LANGUAGE_CHOICES,
        label='Langue du texte',
        initial='sw',
        widget=forms.RadioSelect(attrs={'class': 'lang-radio'}),
    )


class FeedbackForm(forms.Form):
    """Formulaire de signalement d'une mauvaise classification."""

    comment = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 4,
            'placeholder': 'Expliquez pourquoi vous pensez que cette classification est incorrecte...'
        }),
        label='Votre commentaire',
        required=False,
        max_length=1000,
    )
