from flask import Blueprint, render_template, request, jsonify, session
from flask_login import login_required, current_user
from app.models.psychologist import Psychologist
from app.models.appointment import Appointment
from app.services.appointment_service import AppointmentService
from datetime import datetime, timedelta
import json
import os
import openai
from openai import OpenAI

chatbot_bp = Blueprint('chatbot', __name__, url_prefix='/chatbot')

# Initialize OpenAI client (legacy format for openai==1.3.0)
try:
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key and api_key != 'your-openai-api-key-here':
        openai.api_key = api_key
        OPENAI_AVAILABLE = True
        print("OpenAI API key configured successfully")
    else:
        OPENAI_AVAILABLE = False
        print("Warning: OpenAI API key not configured.")
except Exception as e:
    OPENAI_AVAILABLE = False
    print(f"Warning: OpenAI initialization failed: {e}")

class PsychologyConsultantTools:
    """Tools for ChatGPT to interact with the psychology website database"""
    
    @staticmethod
    def search_psychologists(specialty=None, gender=None, language=None):
        """Search psychologists by specialty, gender, and language preferences"""
        try:
            psychologists = Psychologist.query.all()
            filtered = []
            
            for p in psychologists:
                # Filter by specialty if provided
                if specialty:
                    specialties = p.get_specialties()
                    specialty_match = any(specialty.lower() in s.lower() for s in specialties)
                    if not specialty_match:
                        continue
                
                # Filter by gender if provided
                if gender:
                    first_name = p.first_name.lower()
                    # Simple gender detection based on common names
                    female_names = ['mary', 'patricia', 'jennifer', 'linda', 'elizabeth', 'barbara', 'susan', 'jessica', 'sarah', 'karen', 'nancy', 'lisa', 'betty', 'helen', 'sandra', 'donna', 'carol', 'ruth', 'sharon', 'michelle', 'laura', 'kimberly', 'deborah', 'dorothy', 'ayşe', 'fatma', 'emine', 'hatice', 'zeynep', 'elif', 'merve', 'seda', 'büşra', 'esra']
                    
                    is_female = first_name in female_names
                    
                    if gender.lower() in ['female', 'kadın', 'bayan'] and not is_female:
                        continue
                    elif gender.lower() in ['male', 'erkek', 'bay'] and is_female:
                        continue
                
                filtered.append({
                    'id': p.id,
                    'name': p.full_name,
                    'specialties': p.get_specialties(),
                    'bio': p.bio,
                    'working_hours': p.get_working_hours(),
                    'experience_years': getattr(p, 'experience_years', 'N/A')
                })
            
            return filtered[:5]  # Return top 5 matches
        except Exception as e:
            return f"Error searching psychologists: {str(e)}"
    
    @staticmethod
    def get_psychologist_details(psychologist_id):
        """Get detailed information about a specific psychologist"""
        try:
            psychologist = Psychologist.query.get(psychologist_id)
            if not psychologist:
                return "Psychologist not found"
            
            return {
                'id': psychologist.id,
                'name': psychologist.full_name,
                'specialties': psychologist.get_specialties(),
                'bio': psychologist.bio,
                'working_hours': psychologist.get_working_hours(),
                'experience_years': getattr(psychologist, 'experience_years', 'N/A')
            }
        except Exception as e:
            return f"Error getting psychologist details: {str(e)}"
    
    @staticmethod
    def check_availability(psychologist_id, date_str):
        """Check available time slots for a psychologist on a specific date"""
        try:
            psychologist = Psychologist.query.get(psychologist_id)
            if not psychologist:
                return "Psychologist not found"
            
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
            day_of_week = date_obj.strftime('%A')
            
            working_hours = psychologist.get_working_hours()
            if day_of_week not in working_hours or not working_hours[day_of_week] or working_hours[day_of_week] == "Not available":
                return f"Psychologist is not available on {day_of_week}"
            
            # Generate available time slots
            day_hours = working_hours[day_of_week]
            if '-' not in day_hours:
                return f"Invalid working hours format for {day_of_week}"
            
            start_time, end_time = day_hours.split('-')
            start_hour = int(start_time.split(':')[0])
            end_hour = int(end_time.split(':')[0])
            
            available_slots = []
            for hour in range(start_hour, end_hour):
                time_slot = f"{hour:02d}:00"
                available_slots.append(time_slot)
            
            return {
                'psychologist_name': psychologist.full_name,
                'date': date_str,
                'day': day_of_week,
                'available_slots': available_slots
            }
        except Exception as e:
            return f"Error checking availability: {str(e)}"
    
    @staticmethod
    def create_appointment(psychologist_id, date_str, time_str, user_id):
        """Create an appointment for the user"""
        try:
            appointment_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            appointment_time = datetime.strptime(time_str, '%H:%M').time()
            
            appointment, message = AppointmentService.create_appointment(
                user_id=user_id,
                psychologist_id=psychologist_id,
                appointment_date=appointment_date,
                appointment_time=appointment_time
            )
            
            if appointment:
                psychologist = Psychologist.query.get(psychologist_id)
                return {
                    'success': True,
                    'message': f"Appointment successfully created with {psychologist.full_name} on {date_str} at {time_str}",
                    'appointment_id': appointment.id
                }
            else:
                return {
                    'success': False,
                    'message': message
                }
        except Exception as e:
            return {
                'success': False,
                'message': f"Error creating appointment: {str(e)}"
            }

class ChatGPTPsychologyConsultant:
    """ChatGPT-powered psychology consultant for the website"""
    
    def __init__(self):
        self.tools = PsychologyConsultantTools()
        self.system_prompt = """Sen PsikologSitesi'nde çalışan profesyonel bir psikoloji danışmanısın. Görevin kullanıcıları empatiyle dinleyip en uygun psikoloğa yönlendirmek.

ÖNEMLİ: Önceki konuşmaları hatırla ve kullanıcının durumunu sürekli tekrar sorma. Eğer kullanıcı daha önce durumunu anlattıysa, o bilgileri kullan.

TEMEL YAKLAŞIMIN:
1. Empatiyle dinle, duygularını doğrula
2. Önceki konuşmayı hatırla - tekrar sorma
3. Belirtilerden uygun branşı belirle
4. Kullanıcı hazır olduğunda psikolog ara
5. Randevu sürecinde rehberlik et

PSİKOLOJİ BRANŞLARI VE ANAHTAR KELİMELER:
- Anxiety Disorders: kaygı, endişe, panik, korku, anksiyete
- Depression: üzüntü, depresyon, mutsuzluk, motivasyon kaybı
- Anger Management: öfke, sinir, agresiflik, kızgınlık, sinirli olma, öfke kontrolü
- Trauma & PTSD: travma, şok, flashback, kabus
- Relationship Issues: ilişki, evlilik, çift, partner sorunları
- Family Therapy: aile, çocuk, ebeveyn sorunları
- Addiction: bağımlılık, madde, alkol, sigara
- Eating Disorders: yeme, anoreksiya, bulimia, kilo
- OCD: takıntı, obsesyon, kompulsif davranış
- Bipolar Disorder: bipolar, manik, aşırı enerji
- General Counseling: stres, yaşam koçluğu, genel destek

ÖNEMLI: Kullanıcı "sinirli", "öfkeli", "agresif" gibi kelimeler kullanırsa mutlaka "Anger Management" specialty'si ile psikolog ara!

PSİKOLOG LİSTELEME KURALI:
Psikologları listelerken MUTLAKA her psikoloğun veritabanındaki gerçek ID numarasını kullan. Sıralı numaralama (1, 2, 3...) YAPMA!
Örnek format: "ID 5: Dr. Mehmet Özkan" şeklinde, psikoloğun gerçek ID'sini kullan.

ARAÇLARIN: search_psychologists(), get_psychologist_details(), check_availability(), create_appointment()

UNUTMA: Önceki konuşmaları hatırla, kullanıcının dilinde yanıt ver, sadece psikoloji konularında yardım et."""

    def process_message(self, message, user_id):
        """Process user message using ChatGPT with psychology consultation"""
        if not OPENAI_AVAILABLE:
            return {
                'message': 'Üzgünüm, şu anda AI danışman hizmeti kullanılamıyor. Lütfen daha sonra tekrar deneyin.',
                'type': 'error'
            }
        
        try:
            # Test if OpenAI is working by making a simple call first
            test_response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "test"}],
                max_tokens=5
            )
        except Exception as e:
            return {
                'message': f'OpenAI servis hatası: {str(e)}. Lütfen sistem yöneticisine başvurun.',
                'type': 'error'
            }
        
        try:
            # Define available functions for ChatGPT
            functions = [
                {
                    "name": "search_psychologists",
                    "description": "Search for psychologists by specialty, gender, and language preferences",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "specialty": {
                                "type": "string",
                                "description": "Psychology specialty based on user's symptoms (e.g., Anxiety, Depression, Trauma, Anger Management, Relationship Issues, etc.)"
                            },
                            "gender": {
                                "type": "string",
                                "description": "Preferred gender (male/female/erkek/kadın) - only use if user specifically mentions gender preference"
                            },
                            "language": {
                                "type": "string",
                                "description": "Preferred language (Turkish/English) - infer from user's message language"
                            }
                        }
                    }
                },
                {
                    "name": "get_psychologist_details",
                    "description": "Get detailed information about a specific psychologist",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "psychologist_id": {
                                "type": "integer",
                                "description": "ID of the psychologist"
                            }
                        },
                        "required": ["psychologist_id"]
                    }
                },
                {
                    "name": "check_availability",
                    "description": "Check available time slots for a psychologist on a specific date",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "psychologist_id": {
                                "type": "integer",
                                "description": "ID of the psychologist"
                            },
                            "date_str": {
                                "type": "string",
                                "description": "Date in YYYY-MM-DD format"
                            }
                        },
                        "required": ["psychologist_id", "date_str"]
                    }
                },
                {
                    "name": "create_appointment",
                    "description": "Create an appointment for the user",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "psychologist_id": {
                                "type": "integer",
                                "description": "ID of the psychologist"
                            },
                            "date_str": {
                                "type": "string",
                                "description": "Date in YYYY-MM-DD format"
                            },
                            "time_str": {
                                "type": "string",
                                "description": "Time in HH:MM format"
                            },
                            "user_id": {
                                "type": "integer",
                                "description": "ID of the user creating the appointment"
                            }
                        },
                        "required": ["psychologist_id", "date_str", "time_str", "user_id"]
                    }
                }
            ]

            # Get conversation history from session
            if 'chat_history' not in session:
                session['chat_history'] = []
            
            # Initialize user context if not exists
            if 'user_context' not in session:
                session['user_context'] = {
                    'symptoms': [],
                    'preferred_specialty': None,
                    'preferred_gender': None,
                    'language': 'Turkish' if any(char in message for char in 'çğıöşüÇĞIÖŞÜ') else 'English'
                }

            # Add user message to history
            session['chat_history'].append({"role": "user", "content": message})

            # Prepare messages for ChatGPT with enhanced context
            context_summary = ""
            if session['user_context']['symptoms']:
                context_summary += f"Kullanıcının belirttiği semptomlar: {', '.join(session['user_context']['symptoms'])}. "
            if session['user_context']['preferred_specialty']:
                context_summary += f"İlgilendiği alan: {session['user_context']['preferred_specialty']}. "
            
            enhanced_system_prompt = self.system_prompt
            if context_summary:
                enhanced_system_prompt += f"\n\nKULLANICI DURUMU: {context_summary}"
            
            messages = [{"role": "system", "content": enhanced_system_prompt}]
            # Keep last 20 messages for better context (increased from 10)
            messages.extend(session['chat_history'][-20:])

            # Call ChatGPT with function calling (legacy format)
            response = openai.chat.completions.create(
                model="gpt-4",
                messages=messages,
                functions=functions,
                function_call="auto",
                temperature=0.7,
                max_tokens=1500
            )

            message_response = response.choices[0].message

            # Check if ChatGPT wants to call a function
            if message_response.function_call:
                function_name = message_response.function_call.name
                function_args = json.loads(message_response.function_call.arguments)
                
                # Call the appropriate function
                if function_name == "search_psychologists":
                    function_result = self.tools.search_psychologists(
                        specialty=function_args.get('specialty'),
                        gender=function_args.get('gender'),
                        language=function_args.get('language')
                    )
                elif function_name == "get_psychologist_details":
                    function_result = self.tools.get_psychologist_details(
                        function_args['psychologist_id']
                    )
                elif function_name == "check_availability":
                    function_result = self.tools.check_availability(
                        function_args['psychologist_id'],
                        function_args['date_str']
                    )
                elif function_name == "create_appointment":
                    function_result = self.tools.create_appointment(
                        function_args['psychologist_id'],
                        function_args['date_str'],
                        function_args['time_str'],
                        user_id
                    )
                else:
                    function_result = "Function not found"

                # Add function call and result to messages
                messages.append({
                    "role": "assistant",
                    "content": None,
                    "function_call": {
                        "name": function_name,
                        "arguments": message_response.function_call.arguments
                    }
                })
                messages.append({
                    "role": "function",
                    "name": function_name,
                    "content": json.dumps(function_result) if isinstance(function_result, (dict, list)) else str(function_result)
                })

                # Get final response from ChatGPT (legacy format)
                final_response = openai.chat.completions.create(
                    model="gpt-4",
                    messages=messages,
                    temperature=0.7,
                    max_tokens=1500
                )

                assistant_message = final_response.choices[0].message.content
            else:
                assistant_message = message_response.content

            # Add assistant response to history
            session['chat_history'].append({"role": "assistant", "content": assistant_message})
            
            # Update user context based on conversation
            self._update_user_context(message, assistant_message, session)

            return {
                'message': assistant_message,
                'type': 'text'
            }

        except Exception as e:
            return {
                'message': f'Üzgünüm, teknik bir sorun yaşıyorum. Lütfen daha sonra tekrar deneyin. Hata: {str(e)}',
                'type': 'error'
            }
    
    def _update_user_context(self, user_message, assistant_message, session):
        """Update user context based on conversation"""
        try:
            user_message_lower = user_message.lower()
            
            # Extract symptoms from user message
            symptom_keywords = {
                'kaygı': 'anxiety', 'anksiyete': 'anxiety', 'endişe': 'anxiety', 'korku': 'anxiety',
                'depresyon': 'depression', 'üzgün': 'depression', 'mutsuz': 'depression',
                'öfke': 'anger', 'agresif': 'anger', 'sinir': 'anger', 'sinirli': 'anger', 'kızgın': 'anger', 'öfkeli': 'anger',
                'travma': 'trauma', 'ptsd': 'trauma', 'şok': 'trauma',
                'ilişki': 'relationship', 'evlilik': 'relationship', 'partner': 'relationship',
                'aile': 'family', 'çocuk': 'child', 'ebeveyn': 'family',
                'bağımlılık': 'addiction', 'madde': 'addiction', 'alkol': 'addiction',
                'yeme': 'eating', 'anoreksiya': 'eating', 'bulimia': 'eating',
                'ocd': 'ocd', 'takıntı': 'ocd', 'kompulsif': 'ocd', 'obsesyon': 'ocd',
                'bipolar': 'bipolar', 'manik': 'bipolar',
                'kişilik': 'personality'
            }
            
            # Update symptoms
            for keyword, symptom in symptom_keywords.items():
                if keyword in user_message_lower and symptom not in session['user_context']['symptoms']:
                    session['user_context']['symptoms'].append(symptom)
            
            # Extract specialty preference from assistant message
            specialty_keywords = {
                'anksiyete': 'Anxiety Disorders',
                'anxiety': 'Anxiety Disorders',
                'kaygı': 'Anxiety Disorders',
                'depresyon': 'Depression',
                'depression': 'Depression',
                'travma': 'Trauma & PTSD',
                'trauma': 'Trauma & PTSD',
                'öfke': 'Anger Management',
                'anger': 'Anger Management',
                'sinir': 'Anger Management',
                'agresif': 'Anger Management',
                'ilişki': 'Relationship Issues',
                'relationship': 'Relationship Issues',
                'aile': 'Family Therapy',
                'family': 'Family Therapy',
                'bağımlılık': 'Addiction',
                'addiction': 'Addiction',
                'yeme': 'Eating Disorders',
                'eating': 'Eating Disorders',
                'ocd': 'OCD',
                'bipolar': 'Bipolar Disorder',
                'kişilik': 'Personality Disorders',
                'personality': 'Personality Disorders'
            }
            
            assistant_lower = assistant_message.lower()
            for keyword, specialty in specialty_keywords.items():
                if keyword in assistant_lower:
                    session['user_context']['preferred_specialty'] = specialty
                    break
            
            # Keep only last 10 symptoms to avoid overflow
            if len(session['user_context']['symptoms']) > 10:
                session['user_context']['symptoms'] = session['user_context']['symptoms'][-10:]
        except Exception as e:
            # Silently handle context update errors
            pass

# Initialize ChatGPT Psychology Consultant
psychology_consultant = ChatGPTPsychologyConsultant()

@chatbot_bp.route('/')
@login_required
def chat():
    """Main chatbot interface"""
    session['chat_history'] = []  # Bu satır geçmişi her zaman sıfırlar.

    # Pass existing chat history to template
    chat_history = session.get('chat_history', [])
    return render_template('chatbot/chat.html', title='AI Psychology Consultant', chat_history=chat_history)

@chatbot_bp.route('/api/message', methods=['POST'])
@login_required
def process_message():
    """Process chatbot message via API"""
    data = request.get_json()
    message = data.get('message', '').strip()
    
    if not message:
        return jsonify({'error': 'Message is required'}), 400
    
    try:
        response = psychology_consultant.process_message(message, current_user.id)
        return jsonify(response)
    except Exception as e:
        return jsonify({
            'message': 'Üzgünüm, teknik bir sorun yaşıyorum. Lütfen daha sonra tekrar deneyin.',
            'type': 'error'
        }), 500

@chatbot_bp.route('/api/clear', methods=['POST'])
@login_required
def clear_chat():
    """Clear chat history"""
    session.pop('chat_history', None)
    session.pop('user_context', None)
    return jsonify({'success': True})