from datetime import datetime
from fitness_app.models import User


def reset_user_streaks():
    today = datetime.now().date()
    users = User.objects.all()
    count_reset = 0

    for user in users:
        if not user.lastStreakEvidence or (today - user.lastStreakEvidence).days > 1:
            if user.restDays > 0 and user.streak != 0:
                user.restDays -= 1
            else:
                user.streak = 0
                count_reset += 1
            user.save()
