from django.core.management.base import BaseCommand
from django.core.management import call_command
from io import StringIO

class Command(BaseCommand):
    help = 'Run multiple update commands in sequence and display their output'

    def handle(self, *args, **kwargs):
        commands = [
            'updatelocalizationstrings',
            'updategear',
            'updatesplashtags',
            'updatestages',
            'updateweapons',
            'updatetitles',
            'updateawards',
            'updatechallenges',
            'updatesplatfests',
        ]

        for cmd in commands:
            self.stdout.write(f"\nRunning {cmd}...\n")
            
            output = StringIO()
            try:
                call_command(cmd, stdout=output)
                output.seek(0)
                self.stdout.write(output.read())
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"Error running {cmd}: {str(e)}"))
            finally:
                output.close()

            self.stdout.write(f"Finished {cmd}\n")
        
        self.stdout.write(self.style.SUCCESS('All update commands have been executed successfully.'))