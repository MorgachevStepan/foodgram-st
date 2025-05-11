from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.db.models import F, Q, CheckConstraint, UniqueConstraint
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    Кастомная модель пользователя.
    Email используется как логин. Добавлены поля first_name, last_name, avatar.
    """
    username_validator = UnicodeUsernameValidator()

    email = models.EmailField(
        _('email address'),
        max_length=254,
        unique=True,
        error_messages={
            'unique': _("Пользователь с таким email уже существует."),
        },
    )
    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        validators=[username_validator],
        help_text=_('Обязательное поле. Не более 150 символов. Буквы, цифры и @/./+/-/_.'),
        error_messages={
            'unique': _("Пользователь с таким username уже существует."),
        },
    )
    first_name = models.CharField(
        _('first name'),
        max_length=150,
    )
    last_name = models.CharField(
        _('last name'),
        max_length=150, # Из API спеки
    )
    avatar = models.ImageField(
        _('avatar'),
        upload_to='users/avatars/',
        blank=True,
        null=True,
        help_text=_('Аватар пользователя')
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = _('Пользователь')
        verbose_name_plural = _('Пользователи')
        ordering = ('username',)

    def __str__(self):
        return self.email


class Subscription(models.Model):
    """
    Модель подписки пользователя на автора.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name=_('Подписчик'),
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name=_('Автор'),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Дата подписки')
    )

    class Meta:
        verbose_name = _('Подписка')
        verbose_name_plural = _('Подписки')
        constraints = [
            UniqueConstraint(
                fields=['user', 'author'], name='unique_user_author_subscription'
            ),
            CheckConstraint(
                check=~Q(user=F('author')), name='prevent_self_subscription'
            ),
        ]
        ordering = ('-created_at',)

    def __str__(self):
        return f'{self.user} подписан на {self.author}'