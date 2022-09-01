from allauth.account.adapter import DefaultAccountAdapter


# saving custom user
class UserAdapter(DefaultAccountAdapter):
    # could be used when adding extra fields to the signup process
    def save_user(self, request, user, form, commit=True):
        data = form.cleaned_data
        return super().save_user(request, user, form, commit=commit)
