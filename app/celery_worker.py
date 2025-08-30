from celery import Celery
from app import create_app # Flask uygulama fabrikası fonksiyonunuzu import ediyoruz

# Redis'i message broker olarak kullanacak şekilde Celery'yi yapılandırın.
# Eğer Redis'i başka bir port veya host'ta çalıştırıyorsanız burayı güncelleyin.
celery = Celery('tasks', broker='redis://localhost:6379/0')

# Flask uygulama bağlamını her görev için etkinleştiren özel bir Task sınıfı oluşturun.
# Bu, Celery'nin Flask uzantılarına (db, mail vb.) erişebilmesini sağlar.
class ContextTask(celery.Task):
    def __call__(self, *args, **kwargs):
        with self.app.flask_app.app_context():
            return self.run(*args, **kwargs)

# Flask uygulamasını oluşturan fonksiyonu kullanarak Celery için bir uygulama örneği oluşturun
def create_celery_app():
    flask_app = create_app()
    celery.flask_app = flask_app
    celery.Task = ContextTask
    celery.conf.update(flask_app.config)
    return celery

# Celery uygulamasını oluştur
celery_app = create_celery_app()