from fitness_app.models import User


def refill_rest_days():
    users = User.objects.all()

    for user in users:
        user.restDays = 10
        user.save()
