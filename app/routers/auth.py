import os
from datetime import datetime
from datetime import timedelta

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from jose import jwt
import bcrypt
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import User
from app.schemas.schemas import Token
from app.schemas.schemas import UserCreate
from app.schemas.schemas import UserLogin
from app.schemas.schemas import UserOut

router = APIRouter(prefix="/auth", tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

if not SECRET_KEY:
	raise RuntimeError("SECRET_KEY is not set")


def get_password_hash(password: str) -> str:
	salt = bcrypt.gensalt()
	hashed_bytes = bcrypt.hashpw(password.encode("utf-8"), salt)
	return hashed_bytes.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
	try:
		return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
	except Exception:
		return False


def create_access_token(subject: str) -> str:
	expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
	to_encode = {"sub": subject, "exp": expire}
	return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_user_by_email(db: Session, email: str) -> User | None:
	return db.query(User).filter(User.email == email).first()


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
	credentials_exception = HTTPException(
		status_code=status.HTTP_401_UNAUTHORIZED,
		detail="Credenciales invalidas",
		headers={"WWW-Authenticate": "Bearer"},
	)
	try:
		payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
		email = payload.get("sub")
		if not email:
			raise credentials_exception
	except JWTError as exc:
		raise credentials_exception from exc

	user = get_user_by_email(db, email)
	if not user:
		raise credentials_exception
	return user


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)) -> UserOut:
	existing_user = get_user_by_email(db, user_in.email)
	if existing_user:
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email ya registrado")

	user = User(
		nombre=user_in.nombre,
		email=user_in.email,
		password_hash=get_password_hash(user_in.password),
	)
	db.add(user)
	db.commit()
	db.refresh(user)
	return user


@router.post("/login", response_model=Token)
def login(user_in: UserLogin, db: Session = Depends(get_db)) -> Token:
	user = get_user_by_email(db, user_in.email)
	if not user or not verify_password(user_in.password, user.password_hash):
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales invalidas")

	access_token = create_access_token(subject=user.email)
	return Token(access_token=access_token, token_type="bearer")
