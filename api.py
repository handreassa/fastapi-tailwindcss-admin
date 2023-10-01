from fastapi import FastAPI, Request, Depends, Form
from fastapi.responses import HTMLResponse
from fastapi import FastAPI, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from fastapi.templating import Jinja2Templates
from typing import Union, Optional
import jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from fastapi import FastAPI, Depends, HTTPException, Request
from pydantic import BaseModel
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError, DecodeError


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/src", StaticFiles(directory="src"), name="src")

templates = Jinja2Templates(directory="templates")

# Secret key for JWT
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"

# Sample user data (to be replaced with user database)
users_db = {
    "user1": {
        "username": "user1@test.com",
        "password_hash": "$2b$12$MhvChXs.Zuk8z3jwTNMCiOt2nvw0.cToC7kJ5YrA0LOrgktJx2IQy",  # Password: password1
    }
}


class User(BaseModel):
    username: str


class UserInDB(User):
    password_hash: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Union[str, None] = None


class UnicornException(Exception):
    def __init__(self, name: str):
        self.name = name


# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 password flow
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# Generate JWT token
def create_access_token(data: dict, expires_delta: timedelta = timedelta(hours=1)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# Verify user credentials
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


# Get user by username
def get_user(username: str):
    if username in users_db:
        user_dict = users_db[username]
        return UserInDB(**user_dict)


# Authenticate user
def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user.password_hash):
        return False
    return user


# Create a token route
@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("landing_page.html", {"request": request})


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return templates.TemplateResponse(
        "exception.html", {"request": request, "error": exc}
    )


def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=401, detail="Could not validate credentials"
            )
        token_data = TokenData(username=username)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.DecodeError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    return token_data


# Middleware to check for authentication
@app.middleware("http")
async def check_authentication(request: Request, call_next):
    if (
        not request.url.path.startswith("/login")
        and not request.url.path.startswith("/password-reset")
        and request.url.path != "/"
    ):
        # Redirect unauthenticated users to the login page
        try:
            token = request.cookies.get("access_token")
            get_current_user(token)  # Validate the token
        except ExpiredSignatureError:
            response = templates.TemplateResponse(
                "login.html", {"request": request, "message": "Token has expired"}
            )
            response.status_code = 401
            return response
        except DecodeError:
            response = templates.TemplateResponse(
                "login.html", {"request": request, "message": "Invalid token"}
            )
            response.status_code = 401
            return response
    response = await call_next(request)
    return response


@app.get("/login", response_class=HTMLResponse)
async def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login", response_class=HTMLResponse)
async def login_submit(
    request: Request, username: str = Form(...), password: str = Form(...)
):
    user = authenticate_user(username, password)
    if not user:
        # Authentication failed
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "message": "Incorrect username or password"},
        )

    # Authentication successful, generate a JWT token
    access_token = create_access_token(data={"sub": user.username})
    return templates.TemplateResponse(
        "login.html",
        {"request": request, "message": "Login successful", "token": access_token},
    )


@app.get("/register", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


# Create a new POST endpoint for user registration
@app.post("/register", response_class=HTMLResponse)
async def register(
    request: Request, username: str = Form(...), password: str = Form(...)
):
    # Check if the username is already registered (you should implement your own logic here)
    if username in users_db:
        return templates.TemplateResponse(
            "register.html", {"request": request, "message": "Username already exists"}
        )

    # Hash the user's password (you should use a more secure method for production)
    password_hash = pwd_context.hash(password)

    # Store the user data (in-memory, replace with your own database logic)
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
