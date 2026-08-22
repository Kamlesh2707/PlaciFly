"""
Authentication Service — User Registration, Password Management, OTP & Session Handling
Placifly Platform Auth
"""

import random
import time
import threading
import hashlib
import json
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Thread-safe locks
_lock = threading.Lock()

# File path for persisted users
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
USERS_FILE = os.path.join(DATA_DIR, 'users.json')

# In-memory OTP storage: { email: { otp, purpose, expires_at, attempts, temp_data } }
_otp_store = {}

# Session storage: { token: { email, name, created_at } }
_sessions = {}

OTP_EXPIRY_SECONDS = 300  # 5 minutes
MAX_ATTEMPTS = 5

SMTP_EMAIL = os.environ.get('PLACIFLY_SMTP_EMAIL', '')
SMTP_PASSWORD = os.environ.get('PLACIFLY_SMTP_PASSWORD', '')
SMTP_HOST = os.environ.get('PLACIFLY_SMTP_HOST', 'smtp.gmail.com')
SMTP_PORT = int(os.environ.get('PLACIFLY_SMTP_PORT', '587'))
DEV_MODE = not SMTP_EMAIL


def _ensure_data_dir():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR, exist_ok=True)


def _load_users():
    _ensure_data_dir()
    if not os.path.exists(USERS_FILE):
        return {}
    try:
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}


def _save_users(users):
    _ensure_data_dir()
    try:
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(users, f, indent=2)
    except Exception as e:
        print(f"[Auth Service] Could not save users: {e}")


def _hash_password(password, salt=None):
    if not salt:
        salt = hashlib.sha256(str(time.time()).encode()).hexdigest()[:16]
    hashed = hashlib.sha256((password + salt).encode('utf-8')).hexdigest()
    return f"{salt}:{hashed}"


def _verify_password(password, stored_hash):
    try:
        salt, hashed = stored_hash.split(':')
        test_hash = hashlib.sha256((password + salt).encode('utf-8')).hexdigest()
        return test_hash == hashed
    except Exception:
        return False


def generate_otp(email, purpose='register', temp_data=None):
    """
    Generate 6-digit OTP for registration or password reset.
    """
    otp = str(random.randint(100000, 999999))
    email_key = email.lower().strip()
    
    with _lock:
        _otp_store[email_key] = {
            'otp': otp,
            'purpose': purpose,
            'expires_at': time.time() + OTP_EXPIRY_SECONDS,
            'attempts': 0,
            'temp_data': temp_data or {}
        }
    
    return otp


def send_otp_email(email, otp, purpose='Verification'):
    """
    Send OTP email to user or log in dev mode.
    """
    email_key = email.lower().strip()
    
    if DEV_MODE:
        print(f"\n{'='*55}")
        print(f"  [DEV MODE] Placifly {purpose} OTP for {email_key}: {otp}")
        print(f"{'='*55}\n")
        return {
            'success': True,
            'message': f'OTP sent successfully! (Dev mode: check console or on-screen code)',
            'dev_mode': True,
            'dev_otp': otp
        }
    
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f'Placifly — Your {purpose} Code: {otp}'
        msg['From'] = SMTP_EMAIL
        msg['To'] = email_key
        
        html_body = f"""
        <div style="font-family: 'Inter', Arial, sans-serif; max-width: 500px; margin: 0 auto; padding: 32px; background: #030B1E; border-radius: 16px; color: #f8fafc; border: 1px solid rgba(0, 210, 255, 0.2);">
            <div style="text-align: center; margin-bottom: 24px;">
                <div style="font-size: 28px; font-weight: 900; letter-spacing: -0.5px; color: #ffffff;">
                    <span style="color: #00D2FF;">P</span>lacifly
                </div>
                <p style="color: #00D2FF; font-size: 13px; margin: 4px 0 0; letter-spacing: 2px; text-transform: uppercase;">Discover. Choose. Go.</p>
            </div>
            
            <p style="font-size: 14px; color: #cbd5e1; line-height: 1.6; margin-bottom: 20px;">
                Use the 6-digit verification code below to complete your {purpose.lower()}:
            </p>
            
            <div style="text-align: center; margin: 28px 0;">
                <div style="display: inline-block; padding: 16px 40px; background: #0A1128; border: 2px solid #00D2FF; border-radius: 12px; letter-spacing: 8px; font-size: 32px; font-weight: 800; color: #00F0FF; box-shadow: 0 0 20px rgba(0,210,255,0.2);">
                    {otp}
                </div>
            </div>
            
            <p style="font-size: 12px; color: #64748b; text-align: center; margin-top: 24px;">
                This code expires in 5 minutes. If you did not request this, please ignore this email.
            </p>
        </div>
        """
        msg.attach(MIMEText(html_body, 'html'))
        
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_EMAIL, SMTP_PASSWORD)
            server.sendmail(SMTP_EMAIL, email_key, msg.as_string())
        
        return {
            'success': True,
            'message': f'Verification code sent to {email_key}. Please check your inbox.',
            'dev_mode': False
        }
    except Exception as e:
        print(f"[Auth Service] Failed to send email to {email_key}: {e}")
        return {
            'success': True,
            'message': 'OTP generated. Check console in dev mode.',
            'dev_mode': True,
            'dev_otp': otp
        }


def register_user_initiate(name, email, password):
    """
    Start registration by generating and sending an OTP.
    """
    email_key = email.lower().strip()
    users = _load_users()
    
    if email_key in users and users[email_key].get('verified', False):
        return {'success': False, 'message': 'An account with this email already exists. Please log in.'}
    
    otp = generate_otp(email_key, purpose='Registration', temp_data={
        'name': name.strip(),
        'password': password
    })
    
    send_res = send_otp_email(email_key, otp, purpose='Registration')
    send_res['email'] = email_key
    return send_res


def verify_registration_otp(email, submitted_otp):
    """
    Verify registration OTP and create user record.
    """
    email_key = email.lower().strip()
    
    with _lock:
        record = _otp_store.get(email_key)
        if not record:
            return {'success': False, 'message': 'No verification request found for this email. Please request a new code.'}
        
        if time.time() > record['expires_at']:
            del _otp_store[email_key]
            return {'success': False, 'message': 'Verification code has expired. Please request a new code.'}
        
        record['attempts'] += 1
        if record['attempts'] > MAX_ATTEMPTS:
            del _otp_store[email_key]
            return {'success': False, 'message': 'Too many failed attempts. Please request a new code.'}
        
        if record['otp'] == str(submitted_otp).strip():
            temp = record.get('temp_data', {})
            name = temp.get('name', 'User')
            raw_pwd = temp.get('password', '')
            
            users = _load_users()
            users[email_key] = {
                'email': email_key,
                'name': name,
                'password_hash': _hash_password(raw_pwd) if raw_pwd else '',
                'verified': True,
                'created_at': time.time(),
                'favorites': []
            }
            _save_users(users)
            del _otp_store[email_key]
            
            token = f"pf-auth-{random.randint(100000000, 999999999)}-{int(time.time())}"
            _sessions[token] = {
                'email': email_key,
                'name': name,
                'created_at': time.time()
            }
            
            return {
                'success': True,
                'message': 'Account verified successfully!',
                'token': token,
                'user': {
                    'email': email_key,
                    'name': name
                }
            }
        else:
            remaining = MAX_ATTEMPTS - record['attempts']
            return {
                'success': False,
                'message': f'Invalid code. {remaining} attempt(s) remaining.'
            }

# Backward compatible alias
verify_otp = verify_registration_otp



def login_user(email, password):
    """
    Authenticate an existing user.
    """
    email_key = email.lower().strip()
    users = _load_users()
    
    if email_key not in users:
        return {'success': False, 'message': 'Account not found with this email. Please register.'}
    
    user = users[email_key]
    if not user.get('verified', False):
        return {'success': False, 'message': 'Email address not verified yet. Please complete verification.'}
    
    if not _verify_password(password, user.get('password_hash', '')):
        return {'success': False, 'message': 'Incorrect password. Please check your credentials.'}
    
    token = f"pf-auth-{random.randint(100000000, 999999999)}-{int(time.time())}"
    _sessions[token] = {
        'email': email_key,
        'name': user.get('name', 'User'),
        'created_at': time.time()
    }
    
    return {
        'success': True,
        'message': 'Logged in successfully!',
        'token': token,
        'user': {
            'email': email_key,
            'name': user.get('name', 'User')
        }
    }


def request_password_reset(email):
    """
    Initiate password reset via OTP.
    """
    email_key = email.lower().strip()
    users = _load_users()
    
    if email_key not in users:
        return {'success': False, 'message': 'No account found with this email address.'}
    
    otp = generate_otp(email_key, purpose='Password Reset')
    send_res = send_otp_email(email_key, otp, purpose='Password Reset')
    send_res['email'] = email_key
    return send_res


def complete_password_reset(email, submitted_otp, new_password):
    """
    Verify OTP and reset password.
    """
    email_key = email.lower().strip()
    
    with _lock:
        record = _otp_store.get(email_key)
        if not record or record.get('purpose') != 'Password Reset':
            return {'success': False, 'message': 'No password reset in progress for this email.'}
        
        if time.time() > record['expires_at']:
            del _otp_store[email_key]
            return {'success': False, 'message': 'Reset code has expired. Please request a new one.'}
        
        if record['otp'] == str(submitted_otp).strip():
            users = _load_users()
            if email_key in users:
                users[email_key]['password_hash'] = _hash_password(new_password)
                _save_users(users)
            del _otp_store[email_key]
            return {'success': True, 'message': 'Password has been reset successfully! You can now log in.'}
        else:
            return {'success': False, 'message': 'Invalid reset code. Please try again.'}


def create_anonymous_session():
    token = f"pf-anon-{random.randint(100000000, 999999999)}-{int(time.time())}"
    _sessions[token] = {
        'email': 'guest@placifly.com',
        'name': 'Guest User',
        'created_at': time.time()
    }
    return {
        'success': True,
        'token': token,
        'user': {'email': 'guest@placifly.com', 'name': 'Guest User'}
    }


def get_user_favorites(email):
    users = _load_users()
    email_key = email.lower().strip()
    return users.get(email_key, {}).get('favorites', [])


def toggle_user_favorite(email, place_id):
    users = _load_users()
    email_key = email.lower().strip()
    if email_key in users:
        favs = users[email_key].setdefault('favorites', [])
        if place_id in favs:
            favs.remove(place_id)
            is_fav = False
        else:
            favs.append(place_id)
            is_fav = True
        _save_users(users)
        return {'success': True, 'is_favorite': is_fav, 'favorites': favs}
    return {'success': False, 'message': 'User not found.'}
