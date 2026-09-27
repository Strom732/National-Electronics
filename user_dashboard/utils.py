# your_app/utils.py

from allauth.socialaccount.models import SocialAccount

def get_google_profile_image(user):
    try:
        social_account = SocialAccount.objects.get(user=user, provider='google')
        profile_image_url = social_account.extra_data['picture']
        return profile_image_url
    except SocialAccount.DoesNotExist:
        return None
