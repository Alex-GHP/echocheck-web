from app.services.classifier import PoliticalClassifier, get_classifier
from app.services.database import Database, database, get_database
from app.services.email import EmailService, get_email_service
from app.services.file_extractor import FileExtractor, get_file_extractor
from app.services.jwt import JWTService, get_jwt_service
from app.services.password import hash_password, verify_password
from app.services.users import UserService, get_user_service
from app.services.verification import VerificationService, get_verification_service

__all__ = [
    "PoliticalClassifier",
    "get_classifier",
    "Database",
    "database",
    "get_database",
    "EmailService",
    "get_email_service",
    "FileExtractor",
    "get_file_extractor",
    "JWTService",
    "get_jwt_service",
    "hash_password",
    "verify_password",
    "UserService",
    "get_user_service",
    "VerificationService",
    "get_verification_service",
]
