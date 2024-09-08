"""View modules for handling polling functionality in KU Polls."""
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models import Choice, Question, Vote


class IndexView(generic.ListView):
    """
    View class that displays a list of the latest published questions.
    """
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """
        Return the last five published questions (not including those set to be
        published in the future).
        """
        return Question.objects.filter(
            pub_date__lte=timezone.now()
        ).order_by('-pub_date')[:5]


class DetailView(generic.DetailView):
    """
    View class that displays details of questions.
    """
    model = Question
    template_name = 'polls/detail.html'

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())

    def get(self, request, *args, **kwargs):
        """
        Handle GET requests for the detail view of a specific question.
        Redirect to the index page with an error message if voting is not allowed.
        """
        question = self.get_object()
        if not question.can_vote():
            messages.error(request, "Voting on this question is currently not allowed.")
            return HttpResponseRedirect(reverse('polls:index'))
        return super().get(request, *args, **kwargs)


class ResultsView(generic.DetailView):
    """
    View class that displays the results of a specific question.
    """
    model = Question
    template_name = 'polls/results.html'

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        published_question_list = [q.pk for q in Question.objects.all()
                                   if q.is_published()]
        return Question.objects.filter(pk__in=published_question_list)


@login_required
def vote(request, question_id):
    """
    Handling voting for a specific question.
    """
    question = get_object_or_404(Question, pk=question_id)

    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })

    # Reference to the current user
    this_user = request.user

    # Get the user's vote
    try:
        vote = Vote.objects.get(user=this_user, choice__question=question)
        # user has a vote for this question! Update his vote
        vote.choice = selected_choice
        vote.save()
        messages.success(request, f"Your vote was changed to '{selected_choice.choice_text}")
    except Vote.DoesNotExist:
        # does not have a vote
        vote = Vote.objects.create(user=this_user, choice=selected_choice)
        # automatically saved
        messages.success(request, f"You voted for '{selected_choice.choice_text}'")

        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
    return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))
