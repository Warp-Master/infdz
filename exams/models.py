import uuid

from django.db import models
from django.core.validators import MinValueValidator


class Exam(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=100)

    class Meta:
        verbose_name = 'Exam'
        verbose_name_plural = 'Exams'


class Question(models.Model):
    question_text = models.TextField()
    ordered_answers = models.BooleanField(default=False)
    exam = models.ForeignKey('Exam', on_delete=models.CASCADE)
    # answer_length = models.PositiveIntegerField(validators=[MinValueValidator(1)],
    #                                             default=1, verbose_name='Answer table length')
    # answer_height = models.PositiveIntegerField(validators=[MinValueValidator(1)],
    #                                             default=1, verbose_name='Answer table height')

    class Meta:
        verbose_name = 'Question'
        verbose_name_plural = 'Questions'


class Answer(models.Model):
    value = models.CharField(max_length=100)
    question = models.ForeignKey('Question', on_delete=models.CASCADE)

    class Meta:
        order_with_respect_to = 'question'
        verbose_name = 'Answer'
        verbose_name_plural = 'Answers'
