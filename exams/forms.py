from django import forms


INPUTS4MULTI_ANSWER_QUEST = 10


class AnswerForm(forms.Form):
    def __init__(self, *args, num_fields, name_mixin=None, **kwargs):
        super(AnswerForm, self).__init__(*args, **kwargs)
        # add inputs for any question, that contains more than 1 answer
        input_num = max(INPUTS4MULTI_ANSWER_QUEST, num_fields) if num_fields > 1 else num_fields
        for i in range(input_num):
            name = str(i)
            if name_mixin is not None:
                name = f"{name_mixin}_{name}"
            self.fields[name] = forms.CharField(max_length=100, label='', required=False)
