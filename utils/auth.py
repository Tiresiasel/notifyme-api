from flask_httpauth import HTTPTokenAuth
from notifyme.error import *
from notifyme import app
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import BadSignature, SignatureExpired

auth = HTTPTokenAuth()

@auth.verify_token
def verify_token(token):
    s = Serializer(app.config['SECRET_KEY'])
    try:
        s.loads(token)
    except BadSignature:
        # AuthFailed 自定义的异常类型
        raise AuthFailed(msg='token is invalid', error_code=1002)
    except SignatureExpired:
        raise AuthFailed(msg='token is expired', error_code=1001)
    # 校验通过返回True
    return True


