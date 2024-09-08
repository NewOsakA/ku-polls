"""View modules for handling polling functionality in KU Polls."""
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver
import logging

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
        # Replace cludgy code with Messages.
        try:
            question = self.get_object()
        except Http404:
            messages.error(request, "This question is not available.")
            return HttpResponseRedirect(reverse('polls:index'))

        if not question.can_vote():
            messages.error(request, "Voting on this question is currently not allowed.")
            return HttpResponseRedirect(reverse('polls:index'))

        this_user = request.user
        last_vote = None
        if this_user.is_authenticated:
            try:
                last_vote = Vote.objects.get(user=this_user, choice__question=question).choice.id
            except Vote.DoesNotExist:
                last_vote = None
        return render(request, self.template_name, {'question': question, 'last_vote': last_vote})


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


def get_client_ip(request):
    """
    Get the visitor’s IP address using request headers.
    """
    forwarded_for_header = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded_for_header:
        client_ip = forwarded_for_header.split(',')[0]
    else:
        client_ip = request.META.get('REMOTE_ADDR')
    return client_ip


logger = logging.getLogger('polls')


@login_required
def vote(request, question_id):
    """
    Handling voting for a specific question.
    """
    question = get_object_or_404(Question, pk=question_id)
    this_user = request.user
    ip_address = get_client_ip(request)

    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        logger.warning(f"{this_user} failed to vote in {question} from {ip_address}")
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

        logger.info(f'{this_user} voted for Choice {selected_choice.id} in Question {question.id} from {ip_address}')
        messages.success(request, f"Your vote was changed to '{selected_choice.choice_text}'")
    except Vote.DoesNotExist:
        # does not have a vote
        vote = Vote.objects.create(user=this_user, choice=selected_choice)
        # automatically saved
        messages.success(request, f"You voted for '{selected_choice.choice_text}'")

        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
    return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))


def log_user_activity(action, user=None, request=None):
    """
    Helper function to log user activities like login, logout, and login failures.
    """
    ip_address = get_client_ip(request) if request else 'Unknown IP'
    if user:
        logger.info(f'{user} {action} from {ip_address}')
    else:
        logger.warning(f'{action} from {ip_address}')


@receiver(user_logged_in)
def log_user_login(request, user, **kwargs):
    log_user_activity('logged in', user=user, request=request)


@receiver(user_logged_out)
def log_user_logout(request, user, **kwargs):
    log_user_activity('logged out', user=user, request=request)


@receiver(user_login_failed)
def log_user_login_failed(request, **kwargs):
    log_user_activity('failed to log in', request=request)

