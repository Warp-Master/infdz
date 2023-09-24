from django.contrib import admin
from nested_inline.admin import NestedTabularInline, NestedStackedInline, NestedModelAdmin

from .models import ExamGroup, Exam, Question, Answer


class AnswerInline(NestedTabularInline):
    model = Answer
    extra = 1


class QuestionInline(NestedStackedInline):
    model = Question
    inlines = AnswerInline,
    extra = 1


@admin.register(Exam)
class ExamAdmin(NestedModelAdmin):
    list_display = 'title', 'id'
    fields = 'title', 'group', 'is_hidden'
    inlines = QuestionInline,


@admin.register(ExamGroup)
class ExamGroupAdmin(admin.ModelAdmin):
    list_display = "name",
