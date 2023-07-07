from django.db.models import Sum, Case, When, IntegerField, Count
from rest_framework.filters import OrderingFilter


class TeacherOrderingFilter(OrderingFilter):
    def filter_queryset(self, request, queryset, view):
        queryset = queryset.annotate(
            total_score=Sum(
                Case(
                    When(teacher_votes__vote=1, then=1),
                    When(teacher_votes__vote=-1, then=-1),
                    default=0,
                    output_field=IntegerField()
                )
            ),
            total_vote_count=Sum(
                Case(
                    When(teacher_votes__vote=1, then=1),
                    When(teacher_votes__vote=-1, then=1),
                    default=0,
                    output_field=IntegerField()
                )
            ),
        )
        return super().filter_queryset(request, queryset, view)
