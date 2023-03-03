import enum
from dataclasses import dataclass, field
from itertools import starmap
from typing import NamedTuple

from django.shortcuts import render, get_object_or_404
from django.views import View
from natsort import natsorted

from .forms import AnswerForm
from .models import Exam


class AnswerState(enum.Enum):
    PENDING = 0
    WRONG = 1
    CORRECT = 2


class AnswerResume(NamedTuple):
    points: float = 0
    given_ans: str = ""
    state: AnswerState = AnswerState.PENDING


@dataclass
class RangeEnumerator:
    total: int = 0
    items: list[range] = field(default_factory=list)

    def add(self, item: int):
        self.total += 1
        if not self.items or \
                self.items[-1].stop < item:
            self.items.append(range(item, item + 1))
        else:
            self.items[-1] = range(self.items[-1].start, item + 1)

    def __str__(self):
        def range_stringify(r: range):
            if len(r) == 1:
                return f"{r.start}"
            elif len(r) == 2:
                return f"{r.start}{sep}{r.stop-1}"
            return f"{r.start}-{r.stop-1}"

        sep = ', '
        description = sep.join(map(range_stringify, self.items))
        if description:
            description = f"({description})"
        return f"{self.total} {description}".rstrip()


@dataclass
class ResultDetails:
    pending: RangeEnumerator = field(default_factory=RangeEnumerator)
    wrong: RangeEnumerator = field(default_factory=RangeEnumerator)
    correct: RangeEnumerator = field(default_factory=RangeEnumerator)

    answered: int = 0
    total: int = 0


@dataclass
class Result:
    score: float = 0
    max_score: float = 0
    answers: list[AnswerResume] = field(default_factory=list)
    details: ResultDetails = field(default_factory=ResultDetails)

    def push_question(self, question, ans_lines: list[str]):
        self.details.total += 1
        is_correct = check_answer(question, ans_lines)

        point_weight = question.point_weight
        self.max_score += point_weight

        points = point_weight * is_correct
        self.score += points

        state = get_answer_state(ans_lines, is_correct)
        self.answers.append(AnswerResume(points, '\n'.join(ans_lines), state))
        match state:  # self.detail.total used like enum number here
            case AnswerState.PENDING:
                self.details.pending.add(self.details.total)
            case AnswerState.WRONG:
                self.details.wrong.add(self.details.total)
                self.details.answered += 1
            case AnswerState.CORRECT:
                self.details.correct.add(self.details.total)
                self.details.answered += 1


def check_answer(question, answer_list: list[str]) -> bool:
    answer_list = [item.translate({9: None, 32: None}).casefold() for item in answer_list if item.strip()]
    db_answers = [item.value for item in question.answer_set.all()]  # answers in db already processed before save
    if question.is_order_matters:
        return db_answers == answer_list
    else:
        return len(set(db_answers) - set(answer_list)) == 0


def get_answer_state(answer_list: list[str], is_correct: bool) -> AnswerState:
    if is_correct:
        return AnswerState.CORRECT
    elif any(answer_list):
        return AnswerState.WRONG
    return AnswerState.PENDING


def index(request):
    # group name, exam uuid, exam title
    exams = Exam.objects.values('group__name', 'id', 'title')
    exams = natsorted(exams, key=lambda exam: (exam["group__name"], exam["title"]))
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

        result = Result()
        for question, form in zip(question_set, ans_forms):
            if form.is_valid():
                ans_lines = list(form.cleaned_data.values())
                result.push_question(question, ans_lines)

        context = {
            'result': result,
        }
        return render(request, 'exams/result.html', context=context)
