import uuid

from django.db import models
from django.core.validators import MinValueValidator


class ExamGroup(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Group of exams'
        verbose_name_plural = 'Groups of exams'


class Exam(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=100)
    group = models.ForeignKey('ExamGroup', blank=False, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.title} - {self.id}"

    class Meta:
        verbose_name = 'Exam'
        verbose_name_plural = 'Exams'


class Question(models.Model):
    question_text = models.TextField(blank=True)
    is_order_matters = models.BooleanField(default=False)
    point_weight = models.PositiveIntegerField(validators=[MinValueValidator(1)], default=1)
    exam = models.ForeignKey('Exam', on_delete=models.CASCADE)

    class Meta:
        order_with_respect_to = 'exam'
        verbose_name = 'Question'
        verbose_name_plural = 'Questions'


class Answer(models.Model):
    value = models.CharField(max_length=100)
    question = models.ForeignKey('Question', on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        # translate removes '\t'(9) and ' '(32) chars
        self.value = self.value.translate({9: None, 32: None}).casefold()
        super().save(*args, **kwargs)

    class Meta:
        order_with_respect_to = 'question'
        verbose_name = 'Answer'
        verbose_name_plural = 'Answers'
