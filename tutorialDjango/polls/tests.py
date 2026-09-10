import datetime

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Question

def create_question(question_text, days):
    """
    Crea una pregunta con una fecha determinada.
    """

    time = timezone.now() + datetime.timedelta(days=days)

    return Question.objects.create(
        question_text=question_text,
        pub_date=time
    )

class QuestionIndexViewTests(TestCase):

    def test_no_questions(self):
        """
        Si no existen preguntas,
        se muestra el mensaje correspondiente.
        """

        response = self.client.get(
            reverse("polls:index")
        )

        self.assertEqual(response.status_code, 200)

        self.assertContains(
            response,
            "No polls are available."
        )

        self.assertQuerySetEqual(
            response.context["latest_question_list"],
            []
        )


    def test_past_question(self):
        """
        Una pregunta pasada aparece en el índice.
        """

        question = create_question(
            question_text="Past question.",
            days=-30
        )

        response = self.client.get(
            reverse("polls:index")
        )

        self.assertQuerySetEqual(
            response.context["latest_question_list"],
            [question]
        )


    def test_future_question(self):
        """
        Una pregunta futura no aparece en el índice.
        """

        create_question(
            question_text="Future question.",
            days=30
        )

        response = self.client.get(
            reverse("polls:index")
        )

        self.assertContains(
            response,
            "No polls are available."
        )

        self.assertQuerySetEqual(
            response.context["latest_question_list"],
            []
        )


    def test_future_question_and_past_question(self):
        """
        Si hay una pregunta pasada y otra futura,
        solamente aparece la pasada.
        """

        question = create_question(
            question_text="Past question.",
            days=-30
        )

        create_question(
            question_text="Future question.",
            days=30
        )

        response = self.client.get(
            reverse("polls:index")
        )

        self.assertQuerySetEqual(
            response.context["latest_question_list"],
            [question]
        )


    def test_two_past_questions(self):
        """
        El índice puede mostrar varias preguntas.
        """

        question1 = create_question(
            question_text="Past question 1.",
            days=-30
        )

        question2 = create_question(
            question_text="Past question 2.",
            days=-5
        )

        response = self.client.get(
            reverse("polls:index")
        )

        self.assertQuerySetEqual(
            response.context["latest_question_list"],
            [question2, question1]
        )
class QuestionModelTests(TestCase):
    
    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently() devuelve False
        si la pregunta tiene más de un día.
        """

        time = timezone.now() - datetime.timedelta(
            days=1,
            seconds=1
        )

        old_question = Question(pub_date=time)

        self.assertIs(
            old_question.was_published_recently(),
            False
        )


    def test_was_published_recently_with_recent_question(self):
        """
        was_published_recently() devuelve True
        si la pregunta fue publicada dentro del último día.
        """

        time = timezone.now() - datetime.timedelta(
            hours=23,
            minutes=59,
            seconds=59
        )

        recent_question = Question(pub_date=time)

        self.assertIs(
            recent_question.was_published_recently(),
            True
        )

class QuestionDetailViewTests(TestCase):

    def test_future_question(self):
        """
        Una pregunta futura debe devolver 404.
        """

        future_question = create_question(
            question_text="Future question.",
            days=5
        )

        url = reverse(
            "polls:detail",
            args=(future_question.id,)
        )

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            404
        )


    def test_past_question(self):
        """
        Una pregunta pasada debe poder visualizarse.
        """

        past_question = create_question(
            question_text="Past Question.",
            days=-5
        )

        url = reverse(
            "polls:detail",
            args=(past_question.id,)
        )

        response = self.client.get(url)

        self.assertContains(
            response,
            past_question.question_text
        )