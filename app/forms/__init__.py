# Import forms to make them available when importing from the forms package
from app.forms.auth_forms import RegistrationForm, LoginForm
from app.forms.user_forms import UpdateProfileForm
from app.forms.appointment_forms import AppointmentForm, AppointmentCancellationForm