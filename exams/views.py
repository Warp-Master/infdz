from itertools import starmap
from operator import attrgetter
import enum

from django.shortcuts import render, get_object_or_404
from django.views import View

from .forms import AnswerForm
from .models import Exam


class AnswerState(enum.Enum):
    PENDING = 0
    WRONG = 1
    CORRECT = 2


def check_answer(question, answer_list: list[str]) -> bool:
    query_set = question.answer_set.all()
    answers_from_db = map(attrgetter('value'), query_set)
    if question.is_order_matters:
        return list(answers_from_db) == answer_list
    else:
        return len(set(answers_from_db) - set(answer_list)) == 0


def get_answer_state(answer_list: list[str], is_correct: bool) -> AnswerState:
    if is_correct:
        return AnswerState.CORRECT
    elif any(answer_list):
        return AnswerState.WRONG
    return AnswerState.PENDING


def index(request):
    # group name, exam uuid, exam title
    exams = Exam.objects.order_by('group__id').values('group__name', 'id', 'title')

    return render(request, "exams/index.html", context={'exams': exams})


class ExamView(View):
    def get(self, request, exam_uuid):
        exam = get_object_or_404(Exam, pk=exam_uuid)
        question_set = exam.question_set.all()
        ans_forms = starmap(lambda i, x: AnswerForm(num_fields=x.answer_set.count(), prefix=i), enumerate(question_set))
        context = {
            'exam': exam,
            'quest_form_pairs': zip(question_set, ans_forms)
        }
        return render(request, "exams/exam.html", context)

    def post(self, request, exam_uuid):
        exam = get_object_or_404(Exam, pk=exam_uuid)
        question_set = exam.question_set.all()
        ans_forms = starmap(lambda i, x: AnswerForm(request.POST, num_fields=x.answer_set.count(), prefix=i),
                            enumerate(question_set))

        max_score = 0
        score = 0
        answers_given = 0
        results = []
        for question, form in zip(question_set, ans_forms):
            if form.is_valid():
                ans_list = list(form.cleaned_data.values())
                is_correct = check_answer(question, ans_list)
                state = get_answer_state(ans_list, is_correct).value
                point_weight = question.point_weight
                points = point_weight * is_correct

                score += points
                results.append((points, '\n'.join(ans_list), state))
                answers_given += bool(state)
                max_score += point_weight

        context = {
            'max_score': max_score,
            'score': score,
            'answers_given': answers_given,
            'results': results,
        }
        return render(request, 'exams/result.html', context=context)
