from django.db import models
from django.contrib.auth.models import User


CATEGORIE = {
    ('tech', 'Problème technique'),
    ('plc', 'Problème liée a mon compte'),
}


class Questions(models.Model):
    user = models.ForeignKey(User,blank=True, null=True, on_delete=models.CASCADE)
    text = models.CharField(max_length=10000,blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True,blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True,blank=True, null=True)


    class Meta:
        verbose_name="Question"
        verbose_name_plural = "Questions"

    def __str__(self):
        return self.user.username

class Reponse(models.Model):
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE)
    question = models.ForeignKey(Questions, blank=True, null=True, on_delete=models.CASCADE)


    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)


    class Meta:
        verbose_name="Réponse"
        verbose_name_plural = "Réponses"

    def __str__(self):
        return self.user.username