from modeltranslation.translator import TranslationOptions, register

from users.models import User, Profile


@register(User)
class UserTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(Profile)
class ProfileTranslationOptions(TranslationOptions):
    fields = ('bio', 'short_desc',)