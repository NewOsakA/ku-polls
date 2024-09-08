"""Model module for related classes for polls application
"""
import datetime

from django.db import models
from django.utils import timezone
from django.contrib import admin
from django.contrib.auth.models import User


class Question(models.Model):
    """
    Represents a poll question in the application.
    Each question has its own text and a publication date.
    """
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published', default=timezone.now)
    end_date = models.DateTimeField('date ending', null=True, blank=True)

    def was_published_recently(self):
        """Returns True if the question was published within the last day."""
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now

    def is_published(self):
        """Returns True if the current date-time is on or after the question’s publication date."""
        now = timezone.now()
        return now >= self.pub_date

    def can_vote(self):
        """Returns True if voting is allowed for this question."""
        now = timezone.now()
        if self.end_date is None:
            return self.pub_date <= now
        return self.pub_date <= now <= self.end_date

    def __str__(self):
        """Returns a string which represent the text question."""
        return self.question_text


@admin.display(
    boolean=True,
    ordering='pub_date',
    description='Is published',
)
class Choice(models.Model):
    """
    Represents a choice in a poll question.
    Each choice is a part of a specific question and has its own text and vote count.
    """
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    # votes = models.IntegerField(default=0)

    @property
    def votes(self):
        """Return the number of votes for this choice."""
        return self.vote_set.count()

    def __str__(self):
        """Returns a string which represent the text choice."""
        return self.choice_text


class Vote(models.Model):
    """A vote by a user for a choice in a poll"""

    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"Vote by {self.user.username} for {self.choice.choice_text}"
