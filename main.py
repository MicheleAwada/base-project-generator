import os
import subprocess
from settings import get_settings
from docker import get_dockercompose
from nginx import get_nginx
from base_url import get_base_url
import shutil


def copytree(src, dst, symlinks=False, ignore=None):
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)
def soft_copy_directory(source_dir, destination_dir):
    # Create destination directory if it doesn't exist
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)

    # Loop through files and directories in the source directory
    for item in os.listdir(source_dir):
        source_item = os.path.join(source_dir, item)
        destination_item = os.path.join(destination_dir, item)

        if os.path.isdir(source_item):
            soft_copy_directory(source_item, destination_item)
        else:
            shutil.copy2(source_item, destination_item)


env = {
"DJANGO_DEBUG": "True",
"USE_SQLITE_DATABASE": "True",
"WILLING_TO_ACCEPT_HTTPS": "False",
"HTTP_PROTOCOL": "http://",
"BACKEND_NAME": "127.0.0.1:8000",
"FRONTEND_NAME": "localhost:5173"
}

setting_to_add_for_email = """\n\n\nEMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get("EMAIL_HOST")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT"))
EMAIL_USE_TLS = os.environ.get("EMAIL_TLS") == "True"
EMAIL_HOST_USER = os.environ.get("EMAIL_USER")
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_PASSWORD')"""

backend_dockerfile = \
"""FROM python

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip
COPY . .
RUN pip install -r requirements.txt"""

git_ignore = [
    "backend/config/.env",
    "backend/**/__pycache__/",
    "backend/db.sqlite3",
    "venv",
    ".idea"
]



def create_folder_if_doesnt_exists(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)


this_base_directory = os.path.dirname(os.path.abspath(__file__))

def create_django_project():
    project_dir = input("Enter the directory where you want to create the project: ")
    project_dir = os.path.normpath(project_dir)

    backended_project_dir = os.path.join(project_dir, "backend")
    create_folder_if_doesnt_exists(project_dir)
    create_folder_if_doesnt_exists(backended_project_dir)

    os.chdir(backended_project_dir)

    subprocess.run(["django-admin", "startproject", "config", "."])

    def quick_question_bool(question, default=None):
        if default is not None:
            return input(f"{question} [{default and 'y' or 'n'}] (y/n): ") or default
        return input(f"{question}? (y/n): ").lower() == 'y'
    def quick_question_string(question, default=None):
        if default:
            return input(f"{question} [{default}]: ") or default
        return input(f"{question}: ")



    domain_name = quick_question_string("Whats the domain you want", "domain.com")
    yes_www = quick_question_bool("do you want to use www for frontend domain")
    backend_domain_name = f"api.{domain_name}"
    frontend_domain_name = f"{yes_www and 'www.' or ''}{domain_name}"
    opposite_frontend_domain_name = f"{yes_www and '' or 'www.'}{domain_name}"

    prod_domain_env = {
        "#BACKEND_NAME": backend_domain_name,
        "#FRONTEND_NAME": frontend_domain_name,
    }
    env.update(prod_domain_env)

    from django.core.management.utils import get_random_secret_key
    random_secret_key = get_random_secret_key()
    env["DJANGO_SECRET_KEY"] = random_secret_key


    postgres_db = quick_question_string("enter the postgres db name", "db")
    postgres_user = quick_question_string("enter the postgres user", "postgres")
    random_password = get_random_secret_key()
    postgres_password = random_password
    postgres_port = 5432

    database_env = {
        "POSTGRES_DB": postgres_db,
        "POSTGRES_PORT": postgres_port,
        "POSTGRES_USER": postgres_user,
        "POSTGRES_HOST": 'localhost',
        "POSTGRES_PASSWORD": "password",
        "#POSTGRES_HOST": 'postgres',
        "#POSTGRES_PASSWORD": postgres_password,
    }
    env.update(database_env)


    git_ignore_string = "\n".join(git_ignore)


    traefik_path_name = quick_question_string("enter the traefik path name")
    docker_compose = get_dockercompose(traefik_path_name, domain_name)

    requirements = [
        "django",
        "djangorestframework",
        "django-cors-headers",
        "gunicorn",
        "psycopg2-binary"
    ]

    installed_apps_extra = []


    base_urls_pattern = []

    add_contact_module = quick_question_bool("add contact module")
    if add_contact_module:
        this_contact_module_path = os.path.join(this_base_directory, "contact")
        contact_module_path = os.path.join(backended_project_dir, "contact")
        create_folder_if_doesnt_exists(contact_module_path)
        copytree(this_contact_module_path, contact_module_path)
        requirements.append("pytz")
        installed_apps_extra.append("contact")
        base_urls_pattern.append("path('api/contact/', include('contact.urls'))")

    add_newsletter_module = quick_question_bool("add newsletter module")
    if add_newsletter_module:
        env["EMAIL_UNSUBSCRIBE_PATH"] = "/api/newsletter/unsubscribe/"
        this_newsletter_module_path = os.path.join(this_base_directory, "newsletter")
        newsletter_module_path = os.path.join(backended_project_dir, "newsletter")
        create_folder_if_doesnt_exists(newsletter_module_path)
        copytree(this_newsletter_module_path, newsletter_module_path)
        installed_apps_extra.append("newsletter")
        base_urls_pattern.append("path('api/newsletter/', include('newsletter.urls'))")

    final_mail_signals = None
    final_mail_tasks = None
    add_mail_module = quick_question_bool("add sending mail module")
    if add_mail_module:
        this_mail_module_path = os.path.join(this_base_directory, "mail")
        mail_module_path = os.path.join(backended_project_dir, "mail")
        create_folder_if_doesnt_exists(mail_module_path)
        copytree(this_mail_module_path, mail_module_path)
        installed_apps_extra.append("mail")
        from mail_configurator import create_signals, create_tasks, base_contact_signal, base_contact_task, base_newsletter_signal, base_newsletter_task
        signals_functions = []
        tasks_functions = []
        if add_newsletter_module:
            signals_functions.append(base_newsletter_signal)
            tasks_functions.append(base_newsletter_task)
        if add_contact_module:
            signals_functions.append(base_contact_signal)
            tasks_functions.append(base_contact_task)
        final_mail_signals = create_signals(signals_functions)
        final_mail_tasks = create_tasks(tasks_functions)



    settings_string = get_settings(installed_apps=installed_apps_extra)
    base_url_string = get_base_url(base_urls_pattern=base_urls_pattern)

    wants_to_add_email = quick_question_bool("Do you want email")
    if (wants_to_add_email):
        email = quick_question_string("enter the email")
        email_password = quick_question_string("enter the email's password")
        email_host = "mail.mintyhint.com"
        email_port = "587"
        email_use_tls = "True"
        email_env = {
            "EMAIL_USER": email,
            "EMAIL_PASSWORD": email_password,
            "EMAIL_HOST": email_host,
            "EMAIL_PORT": email_port,
            "EMAIL_TLS": email_use_tls,
        }
        env.update(email_env)
        settings_string += setting_to_add_for_email
    if (add_newsletter_module): settings_string += "\n\nEMAIL_UNSUBSCRIBE_PATH = os.getenv('EMAIL_UNSUBSCRIBE_PATH')"

    requirements_dev = requirements.copy()
    requirements_dev.append("python-dotenv")
    requirements_dev_string = "\n".join(requirements_dev)
    requirements_string = "\n".join(requirements)
    env_string = "\n".join([f"{k}={v}" for k, v in env.items()])
    nginx_string = get_nginx(frontend_domain_name=frontend_domain_name, backend_domain_name=backend_domain_name, opposite_frontend_domain_name=opposite_frontend_domain_name)

    def addstringtofile(path, content):
        path = os.path.join(project_dir, path)
        with open(path, 'w') as f:
            f.write(content)

    if add_mail_module:
        addstringtofile("backend/mail/tasks.py", final_mail_tasks)
        addstringtofile("backend/mail/signals.py", final_mail_signals)

    addstringtofile("backend/config/.env", env_string)
    addstringtofile("backend/config/settings.py", settings_string)
    addstringtofile("backend/config/urls.py", base_url_string)
    addstringtofile("backend/requirements.txt", requirements_string)
    addstringtofile("backend/dev-requirements.txt", requirements_dev_string)
    addstringtofile("backend/Dockerfile", backend_dockerfile)
    addstringtofile(".gitignore", git_ignore_string)
    addstringtofile("docker-compose.yml", docker_compose)
    addstringtofile("nginx.conf", nginx_string)





    #frontend time
    frontend_project_dir = os.path.join(project_dir, "frontend")
    this_frontend_skeletion_dir = os.path.join(this_base_directory, "frontend")
    create_folder_if_doesnt_exists(frontend_project_dir)
    os.chdir(frontend_project_dir)

    # subprocess.run(["yarn", "create", "vite", ".", "--template", "react", "--use-yarn"])
    # subprocess.run(["yarn"])

    dependencies = [
        "react-router-dom",
        "@ mui/material",
        "@ emotion/react",
        "@ emotion/styled",
    ]
    # for dependency in dependencies:
    #     subprocess.run(["yarn", "add", dependency])

    soft_copy_directory(this_frontend_skeletion_dir, frontend_project_dir)

    #maizzle
    this_maizzle_skeletion_dir = os.path.join(this_base_directory, "maizzle")
    maizzle_project_dir = os.path.join(project_dir, "maizzle")
    create_folder_if_doesnt_exists(maizzle_project_dir)
    copytree(this_maizzle_skeletion_dir, maizzle_project_dir)

    todo = [
        "Consider changing email subjects in mail module",
        "Change Domain Name in API",
        "Add APIs in Frontend",
        "add the following dependencies\n" + "\n".join(dependencies),
    ]
    print("all done\nNow What\n")
    print("\n".join(map(lambda todo_obj: f"- {todo_obj}",todo)))



if __name__ == "__main__":
    create_django_project()