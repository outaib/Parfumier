import logging  # Delete this for prod
from werkzeug.security import check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from app import login_manager, mongo, app

# LOGGING
logging.basicConfig(level=logging.DEBUG, filename='app.log', filemode='w',
                    format='%(asctime)s %(name)s - %(filename)s :: %(lineno)d - %(levelname)s - %(message)s\n', datefmt='%Y-%m-%d %H:%M:%S')


class User():
    '''
    DESCRIPTION
    '''
    def __init__(self, username, first_name, last_name, email, _id, is_admin, avatar):
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self._id = _id
        self.is_admin = is_admin
        self.avatar = avatar

    def is_authenticated(self):
        '''
        DESCRIPTION
        '''
        return True

    def is_active(self):
        '''
        DESCRIPTION
        '''       
        return True

    def is_anonymous(self):
        '''
        DESCRIPTION
        '''
        return False

    def get_id(self):
        '''
        DESCRIPTION
        '''
        return self.email

    @staticmethod
    def check_password(password_hash, password):
        '''
        DESCRIPTION
        '''
        return check_password_hash(password_hash, password)

    def get_reset_token(self, expires_sec=1800):
        '''
        DESCRIPTION
        '''
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'email': self.email}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        '''
        DESCRIPTION
        '''
        s = Serializer(app.config['SECRET_KEY'])
        try:
            email = s.loads(token)['email']
        except Exception:
            return None
        return mongo.db.users.find_one({'email': email})


@login_manager.user_loader
def load_user(email):
    '''
    DESCRIPTION
    '''
    user = mongo.db.users.find_one({'email': email})
    if not user:
        return None
    return User(user['username'], user['first_name'], user['last_name'],
                user['email'], user['_id'], user['is_admin'], user['avatar'])
