import enum
from collections import Counter
from dataclasses import dataclass, field
from itertools import starmap
from itertools import zip_longest

from django.shortcuts import render, get_object_or_404
from django.views import View
from natsort import natsorted

from .forms import AnswerForm
from .models import Exam

INPUTS_CNT4MULTI_ANSWER_QUEST = 10


class AnswerState(enum.Enum):
    PENDING = enum.auto()
    WRONG = enum.auto()
    CORRECT = enum.auto()


class Delimiters:
    sep = ', '
    sequence = '-'
    sub_del = '.'


class Answer:
    """Instance of this class represents an answer given by user"""
    __slots__ = ("general_num", "sub_num", "text", "max_points", "state")

    def __init__(self, ans: str | list[str], correct_ans: Counter[str] | None, num: int, sub_num: int | None = None):
        self.general_num = num
        self.sub_num = sub_num
        if isinstance(ans, list):
            self.text = '\n'.join(ans)
        else:
            self.text = ans
        self.max_points: int = 1
        self.state = self.get_state(ans, correct_ans)

    def get_state(self, ans: str | list[str], correct_ans: Counter[str]) -> AnswerState:
        if isinstance(ans, list):
            if not self.text:
                return AnswerState.PENDING
            if (correct_ans - Counter(ans)).total() == 0:
                return AnswerState.CORRECT
            return AnswerState.WRONG

        if not ans or correct_ans is None:
            return AnswerState.PENDING
        if correct_ans[ans]:
            correct_ans[ans] -= 1
            return AnswerState.CORRECT
        return AnswerState.WRONG

    @property
    def points(self):
        return self.max_points if self.state == AnswerState.CORRECT else 0

    def __str__(self):
        if self.sub_num is None:
            return str(self.general_num)
        return f"{self.general_num}{Delimiters.sub_del}{self.sub_num}"


def get_answers(question, num: int, answer_lines: list[str]) -> list[Answer]:
    user_answers = [line.strip().translate({9: None, 32: None}).casefold() for line in answer_lines]
    # strip all falsy items after latest true if there is one
    rind_true = next((i for i, x in enumerate(reversed(user_answers)) if x), len(user_answers))
    if rind_true > 0:
        user_answers = user_answers[:-rind_true]
    db_answers = [item.value for item in question.answer_set.all()]  # answers in db already processed before save

    result = []
    is_sub_numbers = len(db_answers) > 1 and not question.atomic_check

    # build answers and append to the result
    if question.is_order_matters and question.atomic_check:
        result.append(Answer(
            ans='\n'.join(user_answers),
            correct_ans=Counter(('\n'.join(db_answers),)),
            num=num,
            sub_num=None
        ))
    elif question.is_order_matters:
        for i, (user_ans, db_ans) in enumerate(zip_longest(user_answers, db_answers, fillvalue=''), start=1):
            result.append(Answer(
                ans=user_ans,
                correct_ans=Counter((db_ans,)),
                num=num,
                sub_num=i if is_sub_numbers else None
            ))
    elif question.atomic_check:
        result.append(Answer(
            ans=user_answers,
            correct_ans=Counter(db_answers),
            num=num,
            sub_num=None
        ))
    else:
        for i, user_ans in enumerate(user_answers, start=1):
            result.append(Answer(
                ans=user_ans,
                correct_ans=Counter(db_answers),
                num=num,
                sub_num=i if is_sub_numbers else None
            ))
        for i in range(len(result) + 1, len(db_answers) + 1):
            result.append(Answer(
                ans='',
                correct_ans=None,
                num=num,
                sub_num=i if is_sub_numbers else None
            ))

    return result


@dataclass
class Sequence:
    start: int
    stop: int

    def __len__(self):
        return self.stop - self.start + 1

    def __str__(self):
        if len(self) > 2:
            return f"{self.start}{Delimiters.sequence}{self.stop}"
        if len(self) == 2:
            return f"{self.start}{Delimiters.sep}{self.stop}"
        return str(self.start)


@dataclass
class Result:
    score: float = 0
    max_score: float = 0

    total: int = 0

    answers: list[Answer] = field(default_factory=list)

    @property
    def details(self):
        class NestedObject:
            _func = self._get_details_str

            def __getattr__(self, item):
                try:
                    return self._func(AnswerState[item])
                except AttributeError | KeyError:
                    raise AttributeError
        return NestedObject

    def _get_details_str(self, state: AnswerState) -> str:
        res_parts = []
        cnt = 0
        last_seq = None
        for ans in filter(lambda a: a.state == state, self.answers):
            cnt += 1
            if ans.sub_num:
                if last_seq is not None:
                    res_parts.append(str(last_seq))
                    last_seq = None
                res_parts.append(str(ans))
            elif last_seq is None:
                last_seq = Sequence(start=ans.general_num, stop=ans.general_num)
            elif ans.general_num > last_seq.stop + 1:
                res_parts.append(str(last_seq))
                last_seq = Sequence(start=ans.general_num, stop=ans.general_num)
            else:
                last_seq.stop = ans.general_num
        if last_seq is not None:
            res_parts.append(str(last_seq))

        if cnt > 0:
            return f"{cnt} ({Delimiters.sep.join(res_parts)})"
        else:
            return f"{cnt}"

    def push_question(self, question, ans_lines: list[str]):
        self.total += 1

        # self.detail.total used like sequence number here
        answers = get_answers(question, self.total, ans_lines)
        self.score += sum(map(lambda ans: ans.state == AnswerState.CORRECT, answers))
        self.max_score += len(answers)

        self.answers += answers


def index(request):
    # group name, exam uuid, exam title
    exams = Exam.objects.filter(is_hidden=False).values('group__name', 'id', 'title')
    exams = natsorted(exams, key=lambda exam: (exam["group__name"], exam["title"]))
    return render(request, "exams/index.html", context={'exams': exams})


def _get_num_fields(quest):
    ans_cnt = quest.answer_set.count()
    if quest.atomic_check and ans_cnt > 1:
        return max(ans_cnt, INPUTS_CNT4MULTI_ANSWER_QUEST)
    return ans_cnt


class ExamView(View):
    def get(self, request, exam_uuid):
        exam = get_object_or_404(Exam, pk=exam_uuid)
        question_set = exam.question_set.all()

        ans_forms = starmap(lambda i, x: AnswerForm(num_fields=_get_num_fields(x), prefix=i), enumerate(question_set))
        context = {
            'exam': exam,
            'quest_form_pairs': zip(question_set, ans_forms)
        }
        return render(request, "exams/exam.html", context)

    def post(self, request, exam_uuid):
        exam = get_object_or_404(Exam, pk=exam_uuid)
        question_set = exam.question_set.all()
        ans_forms = starmap(lambda i, x: AnswerForm(request.POST, num_fields=_get_num_fields(x), prefix=i),
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
