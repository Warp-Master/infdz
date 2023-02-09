from django import forms
from django.forms import ModelForm
from .models import Answer


class AnswerForm(forms.Form):
    def __init__(self, *args, num_fields, name_mixin=None, **kwargs):
        super(AnswerForm, self).__init__(*args, **kwargs)

        for i in range(num_fields):
            name = str(i)
            if name_mixin is not None:
                name = f"{name_mixin}_{name}"
            self.fields[name] = forms.CharField(max_length=100, label='', required=False)

    # def __getitem__(self, name):
    #     return self[name]


# class AnswerForm(ModelForm):
#     value = forms.CharField(max_length=100, label='')
#
#     class Meta:
#         model = Answer
#         fields = 'value',
