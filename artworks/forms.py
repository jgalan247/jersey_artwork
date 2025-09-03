# artworks/forms.py - Minimal version
from django import forms
from artworks.models import Artwork

class ArtworkUploadForm(forms.ModelForm):
    main_image = forms.ImageField(required=True, label="Upload Image")
    
    class Meta:
        model = Artwork
        # Only include fields that definitely exist
        fields = ['title', 'description', 'price']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make fields required
        self.fields['title'].required = True
        self.fields['description'].required = True
        self.fields['price'].required = True
