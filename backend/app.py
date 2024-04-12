from fastapi import FastAPI, HTTPException, Depends, status
# from tortoise.contrib.fastapi import register_tortoise
# from models import(user_pydantic, user_pydanticIn, User)
import models
from typing import Annotated
from database import engine, SessionLocal
from sqlalchemy.orm import Session

#import AI
from fastapi import File, UploadFile
from fastapi.responses import StreamingResponse
from decouple import config
import openai

#Custom Function Imports
from functions.openai_requests import convert_audio_to_text, get_chat_response
from functions.databaseai import store_messages, reset_messages
from functions.text_to_speech import convert_text_to_speech

# Email
from typing import List
from fastapi import BackgroundTasks, FastAPI
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import BaseModel, EmailStr
from starlette.responses import JSONResponse

# Import dotenv to load values
from dotenv import dotenv_values

# Load credentials from .env file
credentials = dotenv_values(".env")

# Adding cors headers
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

#-------------------------------------Connect database------------------------------------------------
models.Base.metadata.create_all(bind = engine)


class QnABase(BaseModel):
    tile    : str
    content : str
    user_id : str

class UserBase(BaseModel):
    username             : str
    password             : str
    firstname            : str
    lastname             : str
    DoB                  : str
    address              : str
    email                : str
    phone_number         : str
    roleID               : int
    
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

        
db_dependency = Annotated[Session, Depends(get_db)]
        
    
#-------------------------------------Adding CORS Url--------------------------------------------------
origins = [
    'http://localhost:3000'
    
]
# Add midlleware 
app.add_middleware(
    CORSMiddleware,
    allow_origins     = origins,
    allow_credentials = True,
    allow_methods     = ["*"],
    allow_headers     = ["*"],
)

#---------------------------------------CRUD API------------------------------------------------------------
@app.get('/')
def index():
    return {"message": "Hello"}

# Create
@app.post('/user/', status_code=status.HTTP_201_CREATED)
async def add_user(user: UserBase, db: db_dependency):
    db_user = models.User(**user.dict(exclude_unset = True))
    db.add(db_user)  
    db.commit()
    db.refresh(db_user)  
    return {"status": "ok", "data": user}

# Read
@app.get('/user')
async def get_all_users(db: db_dependency):
        db_users =  db.query(models.User).all()
        return {"status": "ok", "data": db_users}

# @app.get('/user/{User_ID}')
# async def get_specific_user(User_ID: int, db: db_dependency):
#     db_user = db.query(models.User).filter(models.User.id == User_ID).first()
#     if db_user is None:
#         HTTPException(status_code=404, detail="User not found!")
#     return {"status": "ok", "data": db_user}

@app.get('/user/{username}')
async def get_user_username(username: str, db: db_dependency):
    db_user = db.query(models.User).filter(models.User.username == username).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return {"status": "ok", "data": (db_user)}

# Update
@app.put('/user/{User_ID}')
async def update_user(User_ID: int, db: db_dependency, update_info: UserBase):
    db_user = db.query(models.User).filter(models.User.id == User_ID).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    update_data = update_info.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_user, key, value)
    db.commit()
    db.refresh(db_user)
    return {"status": "ok", "data": db_user}

# Delete
@app.delete('/user/{User_ID}')
async def delete_user(User_ID: int, db: db_dependency):
    db_user = db.query(models.User).filter(models.User.id == User_ID).first()
    if db_user is None:
        HTTPException(status_code=404 , detail="User not Found")
    db.delete(db_user)
    db.commit()
    return "ok"

#-----------------------------------------------Email function-----------------------------------------------
class EmailSchema(BaseModel):
    email: List[EmailStr]
    
class EmailContent(BaseModel):
    message: str
    subject: str


conf = ConnectionConfig(
    MAIL_USERNAME   = credentials['EMAIL'],
    MAIL_PASSWORD   = credentials['PASSWORD'],
    MAIL_FROM       = credentials["EMAIL"],
    MAIL_PORT       = 465,
    MAIL_SERVER     = "smtp.gmail.com",
    MAIL_STARTTLS   = False,
    MAIL_SSL_TLS    = True,
    USE_CREDENTIALS = True,
    VALIDATE_CERTS  = True
)

@app.post("/email/{User_ID}")
async def send_email(User_ID: int, content: EmailContent):
    user_gui        = await UserBase.get(id = User_ID)
    user_nhan       = await user_gui
    user_nhan_email = [user_nhan.email]
    
    html = f"""
    <h5>Công ty phatAI</h5> 
    <br>
    <p>{content.message}</p>
    <br>
    <h6>Chúc bạn một ngày tốt lành</h6>
    <h6>Công ty phatAI</h6>
    """


    message     = MessageSchema(
    subject     = content.subject,
    recipients  = user_nhan_email,
    body        = html,
    subtype     ="html")

    fm = FastMail(conf)
    await fm.send_message(message)
    return {"status": "ok"}  

#--------------------------------------AI-----------------------------------------------
#Reset Messages
@app.get("/reset")
async def reset_conversation():
    reset_messages()
    return {"message": "Conversation reset"}

#Get Audio  
@app.post("/post-audio-get")
async def get_audio():
# @app.post("/post-audio")
# async def post_audio(file: UploadFile = File(...)):
    
    #Get saved audio
    audio_input = open("tomvoice.mp3", "rb")
    
    # #save file from Frontend
    # with open (file.filename, "wb") as buffer:
    #     buffer.write(file.file.read())
    # audio_input = open(file.filename, "rb")
    
    # with open(file.filename, "wb") as buffer: 
    #     buffer.write(file.file.read())  
    # audio_input = open(file.filename, "rb")
    
    #Decode Audio
    message_decoded = convert_audio_to_text(audio_input)
    
    print(message_decoded)
    
    #Guard: Ensure message decoded
    if not message_decoded:
        return HTTPException(status_code=400, detail="Failed to decode audio")
    
    #Get Chat GPT response
    chat_response = get_chat_response(message_decoded)
    
    #Guard: Ensure message decoded
    if not chat_response:
        return HTTPException(status_code=400, detail="Failed to get chat response")
    
    #Store messages
    store_messages(message_decoded, chat_response)
    
    #Convert chat response to audio
    audio_output = convert_text_to_speech(chat_response)
    
    #Guard: Ensure message decoded
    if not audio_output:
        return HTTPException(status_code=400, detail="Failed to get ElevenLabs audio response")
    
    #Create a generator that yields chunks of data
    def iterfile():
        yield audio_output
        
    #Return audio file 
    return StreamingResponse(iterfile(), media_type = "audio/mpeg") 


