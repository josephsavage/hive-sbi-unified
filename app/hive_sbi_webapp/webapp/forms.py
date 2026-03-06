from django import forms


class UserInfoForm(forms.Form):
    user = forms.CharField(
        required=False,
        max_length=100,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user'].widget.attrs['class'] = 'form-control'
