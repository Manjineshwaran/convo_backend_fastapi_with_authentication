print("----------------------Entered security-----------------------")
from datetime import datetime, timedelta
from typing import Optional

from jose import jwt
from passlib.context import CryptContext

SECRET_KEY = "YOUR_SECRET_KEY"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30   #only authentication work for 30 minutes

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str):
    print("============password=============")
    print("\npassword\n",hash)
    print("=================================")
    print("============hash password=============")
    n=pwd_context.hash(password)
    print("\nhash password\n",n)
    print("=================================")
    return pwd_context.hash(password)


def create_access_token(*, data: dict, expires_delta: Optional[timedelta] = None):
    print("\ndata\n",data)
    print("=================================")
    print("\nexpires_delta\n",expires_delta)
    print("=================================")
    to_encode = data.copy()
    print("\nto_encode\n",to_encode)
    print("=================================")
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})

    m=to_encode.update({"exp": expire})
    print("\nm=to_encode.update({exp: expire)\n",m)
    print("=================================")
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    print("\nencoded_jwt\n",encoded_jwt)
    print("=================================")
    return encoded_jwt
