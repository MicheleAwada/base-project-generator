base_contact_task = \
"""def send_contact_email(instance):
    html_content = render_to_string("mail/contact success.html", {
        "name": instance.name,
        "email": instance.email,
        "body": instance.body
    })

    send_mail(
        subject="Message to BLANK Successfully sent!",
        message="",
        from_email=from_email,
        recipient_list=[instance.email],
        html_message=html_content,
        fail_silently=True
    )
    
    send_mail(
        subject=f"{instance.name} at {instance.email}!",
        message=f"",
        from_email=from_email,
        recipient_list=["form@mintyhint.com"],
        fail_silently=True
    )"""

base_contact_signal = """ContactModel = apps.get_model('contact', 'Contact')

@receiver(signals.post_save, sender=ContactModel)
def detect_contact_created(instance, created, **kwargs):
    if created:
        async_function(lambda: send_contact_email(instance))"""






base_newsletter_task = """
NewsletterSubscriberModel = apps.get_model('newsletter', 'NewsletterSubscriber')
def send_newsletters_email(instance):
    html_content = instance.html_content
    for newsletter_sub in NewsletterSubscriberModel.objects.all():    
        send_mail(
            subject=instance.subject,
            message=instance.text_content,
            from_email=from_email,
            recipient_list=[newsletter_sub.email],
            html_message=instance.html_content,
            fail_silently=True
        )

def send_newsletter_created_email(instance):
    html_content = render_to_string("mail/newsletter created.html", {
        "email": instance.email,
    })
    
    send_mail(
        subject="Successfully Subscribed to Newsletter!",
        message="",
        from_email=from_email,
        recipient_list=[instance.email],
        html_message=html_content,
        fail_silently=True
    )



def send_newsletter_deleted_email(instance):
    
    html_content = render_to_string("mail/newsletter deleted.html", {
        "email": instance.email,
    })
    
    send_mail(
        subject="Successfully Unsubscribed from Newsletter!",
        message="",
        from_email=from_email,
        recipient_list=[instance.email],
        html_message=html_content,
        fail_silently=True
    )"""


base_newsletter_signal = """NewsletterSubscriberModel = apps.get_model('newsletter', 'NewsletterSubscriber')
NewsletterModel = apps.get_model('newsletter', 'Newsletter')

@receiver(signals.post_save, sender=NewsletterModel)
def detect_newsletter_created(instance, created, **kwargs):
    if created:
        async_function(lambda: tasks.send_newsletters_email(instance))

@receiver(signals.post_save, sender=NewsletterSubscriberModel)
def detect_newsletter_user_created(instance, created, **kwargs):
    if created:
        async_function(lambda: tasks.send_newsletter_created_email(instance))

@receiver(signals.post_delete, sender=NewsletterSubscriberModel)
def detect_newsletter_user_deleted(sender, instance, **kwargs):
    async_function(lambda: tasks.send_newsletter_deleted_email(instance))
"""







def create_tasks(functions):
    return \
"""from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.apps import apps


from_email = settings.EMAIL_HOST_USER

"""+"\n".join(functions)

def create_signals(functions):
    return \
"""import threading
def async_function(function):
    t = threading.Thread(target=function)
    t.start()

from django.apps import apps
from . import tasks
from django.dispatch import receiver
from django.db.models import signals




"""+"\n".join(functions)