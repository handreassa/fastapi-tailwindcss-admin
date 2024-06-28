from datetime import datetime, timedelta, timezone
from typing import Annotated, Optional, Union
import jwt
from fastapi import Depends, FastAPI, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse,RedirectResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from jwt.exceptions import DecodeError, ExpiredSignatureError, InvalidTokenError
from passlib.context import CryptContext
from pydantic import BaseModel
import logging
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/src", StaticFiles(directory="src"), name="src")

logger = logging.getLogger("uvicorn.error")
logger.setLevel(logging.DEBUG)

templates = Jinja2Templates(directory="templates")

# to get a secret key string like this example, run this command on terminal:
# openssl rand -hex 32
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Sample user data (this is a placeholder to be replaced with user database)
users_db = {
    "placeholder123": {
        "username": "placeholder123",
        "email": "test@example.com",
        "password_hash": "$2b$12$ugtN8kcm5z/dAMAx7faQkeny9Y.PgYZnQJX/VJc7K/DfdgrVJpwEa",  # Password: password1
    }
}

class UserInDB:
    def __init__(self, username, email, password_hash):
        self.username = username
        self.email = email
        self.password_hash = password_hash

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Union[str, None] = None

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_password(plain_password, password_hash):
    return pwd_context.verify(plain_password, password_hash)

def get_user(db, username: str):
    if username in db:
        # logger.debug(f"Username: {username}")
        user_dict = db[username]
        return UserInDB(**user_dict)
    # else:
    #     logger.debug(f"Username not found: {username}")

def authenticate_user(db, username: str, password: str):
    user = get_user(db, username)
    logger.debug(f"User: {user}")
    if not user:
        return False
    if not verify_password(password, user.password_hash):
        return False
    return user

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        logger.debug(f"Username: {username}")
        if username is None:
            logger.debug("Username is None")
            raise credentials_exception
        token_data = TokenData(username=username)
        logger.debug(f"token_data: {token_data}")
    except InvalidTokenError:
        raise credentials_exception
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


@app.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
)-> Token:
    user = authenticate_user(users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    # return Token(access_token=access_token, token_type="bearer")
    response = RedirectResponse(url="/charts", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
    return response

@app.get("/login", response_class=HTMLResponse)
async def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/register", response_class=HTMLResponse)
async def register(
    request: Request, username: str = Form(...), password: str = Form(...)
):
    if username in users_db:
        return templates.TemplateResponse(
            "register.html", {"request": request, "message": "Username already exists"}
        )
    password_hash = pwd_context.hash(password)
    users_db[username] = {"username": username, "password_hash": password_hash}

    response = templates.TemplateResponse(
        "login.html", {"request": request, "flash_message": "Registration successful"}
    )
    response.set_cookie("flash_message", "Registration successful")
    return response

@app.get("/password-reset", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("password-reset.html", {"request": request})

@app.post("/password-reset", response_class=HTMLResponse)
async def password_reset(
    request: Request, username: str = Form(...), new_password: str = Form(...)
):
    # Check if the username exists in your user database (you should implement your own logic here)
    if username not in users_db:
        return templates.TemplateResponse(
            "password-reset.html", {"request": request, "message": "User not found"}
        )

    # Update the user's password (you should use a more secure method for password hashing in production)
    password_hash = pwd_context.hash(new_password)
    users_db[username]["password_hash"] = password_hash

    # Return a success message or redirect to a login page
    response = templates.TemplateResponse(
        "login.html", {"request": request, "flash_message": "Password reset successful"}
    )
    response.set_cookie("flash_message", "Password reset successful")
    return response

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return templates.TemplateResponse(
        "exception.html", {"request": request, "error": exc}
    )
# Landing page
@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("landing_page.html", {"request": request})

# Protected dashboard
# @app.get("/chart", response_class=HTMLResponse)
# def charts(request: Request, current_user: TokenData = Depends(get_current_user)):
#     return templates.TemplateResponse("chart2.html", {"request": request, "user": current_user})


@app.get("/dashboard", response_class=HTMLResponse)
def dash(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})