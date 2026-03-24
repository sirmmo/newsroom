from django.core.management.base import BaseCommand
from openai import OpenAI
import os

DEFAULT_BASE_URL = "https://openrouter.ai/api/v1"


class Command(BaseCommand):
    def handle(self, *args, **options):
        base_url = os.environ.get("OPENAI_BASE_URL", DEFAULT_BASE_URL)

        client = OpenAI(
            base_url=base_url,
            api_key=os.environ.get("OPENAI_API_KEY", ""),
        )

        self.stdout.write(f"Connected to {base_url}")
        models = client.models.list()
        for m in models.data:
            self.stdout.write(f"  {m.id}")
