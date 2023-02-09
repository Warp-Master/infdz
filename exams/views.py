import typing
from itertools import starmap
from operator import attrgetter
from typing import Iterable

from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views import View

from .forms import AnswerForm
from .models import Exam

# if typing.TYPE_CHECKING:
#     from .models import Question


def check_answer(question, answers: Iterable) -> bool:
    query_set = question.answer_set.all()
    answers_from_db = map(attrgetter('value'), query_set)
    if question.is_order_matters:
        return list(answers_from_db) == list(answers)
    else:
        return len(set(answers_from_db) - set(answers)) == 0


def index(request):
    return HttpResponse("You're at the exams index.")


class ExamView(View):
    def get(self, request, exam_uuid):
        exam = get_object_or_404(Exam, pk=exam_uuid)
        question_set = exam.question_set.all()
        ans_forms = starmap(lambda i, x: AnswerForm(num_fields=x.answer_set.count(), prefix=i), enumerate(question_set))
        context = {
            'exam': exam,
            # 'questions': question_set,
            # 'ans_forms': map(lambda x: AnswerForm(x.answer_set.length()), question_set)
            'quest_form_pairs': zip(question_set, ans_forms)
        }
        return render(request, "exams/exam.html", context)

    # def get(self, request, exam_uuid):
    #     exam = get_object_or_404(Exam, pk=exam_uuid)
    #     question_set = exam.question_set.all()
    #     # ans_forms = starmap(lambda i, x: formset_factory(AnswerForm(x.answer_set.count(), name_mixin=i)), enumerate(question_set))
    #     formset = formset_factory([*map(lambda x: AnswerForm(, extra=x.answer_set.count()), question_set)])
    #     context = {
    #         'exam': exam,
    #         # 'questions': question_set,
    #         # 'ans_forms': map(lambda x: AnswerForm(x.answer_set.length()), question_set)
    #         'quest_form_pairs': zip(question_set, formset)
    #     }
    #     return render(request, "exams/exam.html", context)

    def post(self, request, exam_uuid):
        exam = get_object_or_404(Exam, pk=exam_uuid)
        question_set = exam.question_set.all()
        ans_forms = starmap(lambda i, x: AnswerForm(request.POST, num_fields=x.answer_set.count(), prefix=i), enumerate(question_set))

        points_total = len(question_set)
        points = 0
        for question, form in zip(question_set, ans_forms):
            if form.is_valid():
                points += check_answer(question, form.cleaned_data.values())
        return HttpResponse(f"{points}/{points_total}")
