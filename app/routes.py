print("----------------------Entered routes-----------------------")
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import os

# from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_google_genai import ChatGoogleGenerativeAI

from app import auth, models, schemas, security
from app.db import get_db
from app.models import User
from ai.prompts import generate_context, qa_template

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

import logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - line:%(lineno)d - %(message)s'
)

router = APIRouter()

print("===============================")
respons=schemas.UserInDBBase
print("Fields in UserInDBBase:", respons.__fields__.keys())
print("\schemas.UserInDBBase\n",respons)
print("===============================")

@router.post("/register/", response_model=schemas.UserInDBBase)
async def register(user_in: schemas.UserIn, db: Session = Depends(get_db)):
    db_user = auth.get_user(db, username=user_in.username)
    print("\nuser_in\n",user_in,"\ntype:  ",type(user_in))
    print("===============================")
    print("\ndb\n",db,"\ntype:  ",type(db))
    print("===============================")
    print("\ndb_user\n",db_user,"\ntype:  ",type(db_user))
    print("===============================")
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    db_user = db.query(models.User).filter(models.User.email == user_in.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = security.get_password_hash(user_in.password)
    print("\nhashed_password\n",hashed_password)
    print("===============================")

    db_user = models.User(
        **user_in.dict(exclude={"password"}), hashed_password=hashed_password
    )
    print("\ndb_user\n",db_user)
    print("===============================")
    print("\ndb\n",db)
    print("===============================")
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

print("===============================")
respons=schemas.Token
print("Fields in schemas.Token:", respons.__fields__.keys())
print("\nschemas.Token\n",respons)
print("===============================")

@router.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):  
    print("\nform_data\n",form_data,"\ntype:  ",type(form_data))
    print("===============================")
    logger.info(
        "Login attempt - username: %s (type: %s)", 
        form_data.username, 
        type(form_data.username).__name__
    )
    
    user = auth.get_user(db, username=form_data.username)
    
    print("\nuser\n",user,"\ntype:  ",type(user))
    print("===============================")
    logger.debug(
        "User lookup result: %s (exists: %s)", 
        form_data.username, 
        bool(user)
    )
    
    if not user or not security.pwd_context.verify(
        form_data.password, user.hashed_password
    ):
        logger.warning(
            "Failed login for username: %s (invalid credentials)", 
            form_data.username
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    logger.info(
        "Successful login - username: %s, token expires in: %s mins", 
        user.username, 
        security.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/conversation/")
async def read_conversation(
    query: schemas.ConversationQuery,
    current_user: schemas.UserInDB = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    print("\ncurrent_user\n", current_user, "\ntype:  ", type(current_user))
    print("===============================")
    
    db_user = db.query(User).get(current_user.id)
    print("\ndb_user\n", db_user, "\ntype:  ", type(db_user))
    print("===============================")
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    context = generate_context(db_user)

    GEMINI_API_KEY = "AIzaSyAX9FB7lVP-5dDYGsri3cHMd9di6ebp0eQ"

    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    print("\n env key:", GEMINI_API_KEY)
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.2, google_api_key=GEMINI_API_KEY)
    
    print("\nllm:", llm)
    prompt = PromptTemplate(
        input_variables=["context", "question"], template=qa_template
    )
    chain = LLMChain(llm=llm, prompt=prompt)
    print("\nchain\n", chain)

    response = chain.run(context=context, question=query)

    print("\nresponse\n", response, "\ntype:  ", type(response))

    return {"response": response}
