import json
import os

from django.core.management.base import BaseCommand

from catalog.models import ContentItem, Section
from quizzes.models import Choice, Difficulty, Question, Quiz


class Command(BaseCommand):
    help = "Import quizzes from JSON file, including images"

    def add_arguments(self, parser):
        parser.add_argument(
            'json_file', type=str, help='Path to the JSON file containing the quiz data'
        )
        parser.add_argument(
            '--media-dir', type=str, default='media', help='Base directory for media files'
        )
        parser.add_argument(
            '--images-subdir', type=str, default='quiz_images/questions',
            help='Subdirectory inside media-dir where question images are stored'
        )

    def handle(self, *args, **options):
        json_file = options['json_file']
        media_dir = options['media_dir']
        images_subdir = options['images_subdir']

        # Load JSON
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Failed to read JSON file: {e}"))
            return

        # Section
        section, _ = Section.objects.get_or_create(title="Imported Quizzes")

        # ContentItem
        content_item = ContentItem.objects.create(
            title=data['quiz']['title'],
            type=ContentItem.ItemType.QUIZ,
            section=section,
        )

        # Quiz
        quiz = Quiz.objects.create(
            content_item=content_item,
            title=data['quiz']['title'],
            description=data['quiz'].get('description', ''),
            pass_score=data['quiz'].get('pass_score', 0),
        )

        # Questions & Choices
        for q in data['quiz']['questions']:
            question = Question(
                quiz=quiz,
                order=q.get('order', 0),
                text=q.get('text', ''),
                difficulty=q.get('difficulty', Difficulty.EASY),
            )

            q_img = q.get('question_image')
            if q_img:
                q_img_path = os.path.join(media_dir, images_subdir, q_img)
                if os.path.exists(q_img_path):
                    question.question_image = f'{images_subdir}/{q_img}'
                else:
                    self.stdout.write(self.style.WARNING(f"Question image not found: {q_img_path}"))

            question.save()

            for c in q.get('choices', []):
                choice = Choice(
                    question=question,
                    order=c.get('order', 0),
                    text=c.get('text', ''),
                    is_correct=c.get('is_correct', False),
                )

                c_img = c.get('choice_image')
                if c_img:
                    c_img_path = os.path.join(media_dir, images_subdir, c_img)
                    if os.path.exists(c_img_path):
                        choice.choice_image = f'{images_subdir}/{c_img}'
                    else:
                        self.stdout.write(self.style.WARNING(f"Choice image not found: {c_img_path}"))

                choice.save()

        self.stdout.write(self.style.SUCCESS(
            f"Quiz '{quiz.title}' imported successfully with {quiz.questions.count()} questions!"
        ))