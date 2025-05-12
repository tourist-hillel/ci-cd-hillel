from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import re
import zxcvbn
from django.contrib.auth.hashers import check_password

class MinimumLengthValidator:
    def __init__(self, min_length=12):
        self.min_length = min_length

    def validate(self, password, user=None):
        if len(password) < self.min_length:
            raise ValidationError(
                _(f'Пароль занадто короткий! Потрібно принаймні {self.min_length} символів!'),
                code='password_too_short'
            )
        
    def get_help_text(self):
        return _(f'Пароль повинен містити принаймні {self.min_length} символів!')


class CharacterTypeValidator:
    def validate(self, password, user=None):
        if not re.search(r'[A-Z]', password):
            raise ValidationError(
                _('Пароль має містити принаймні одну велику літеру латиниці'),
                code='no_uppercase'
            )
        if not re.search(r'[a-z]', password):
            raise ValidationError(
                _('Пароль має містити принаймні одну велику малу латиниці'),
                code='no_lowercase'
            )
        if not re.search(r'[0-9]', password):
            raise ValidationError(
                _('Пароль має містити принаймні одну цифру'),
                code='no_digit'
            )
        if not re.search(r'[!@#$%^&*()?:<>]', password):
            raise ValidationError(
                _('Пароль має містити принаймні один спецсимвол (!@#$%^&*()?:<>)'),
                code='no_special_char'
            )
    def get_help_text(self):
        return _(f'Пароль повинен містити великі і малі літери латиниці, цифри та спец символи!')


class PasswordStrengthValidator:
    def __init__(self, min_score=3):
        self.min_score = min_score

    def validate(self, password, user=None):
        user_inputs = [user.username, user.email, user.first_name, user.last_name] if user else []
        result = zxcvbn.zxcvbn(password, user_inputs=user_inputs)
        if result['score'] < self.min_score:
            raise ValidationError(
                _('Пароль недостатньо міцний. Додайте унікальні символи'),
                code='weak_password'
            )
        
    def get_help_text(self):
        return _('Пароль має бути достатньо надійним!')
    

class NoRepetitiveCharsValidator:
    def __init__(self, max_repeats=3):
        self.max_repeats = max_repeats
    
    def validate(self, password, user=None):
        for char in set(password):
            if password.count(char) > self.max_repeats:
                raise ValidationError(
                    _(f'Пароль не може містити більше {self.max_repeats} однакових символів!'),
                    code='repetitive_chars'
                )
    def get_help_text(self):
        return _(f'Пароль не мусить містити більше {self.max_repeats} однакових символів!')

       
class PasswordHistoryValidator:
    def __init__(self, history_limits=3):
        self.history_limits = history_limits

    def validate(self, password, user=None):
        if user and hasattr(user, 'passwordhistory_set'):
            for old_password in user.passwordhistory_set.all()[:self.history_limits]:
                if check_password(password, old_password.password):
                    raise ValidationError(
                        _('Ви не можете викоритовувати старі паролі!'),
                        code='password_reused'
                    )
                
    def get_help_text(self):
        return _('Пароль не має збігатись із одним із попередніх паролів!')
