from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy import event, text

from .database import db


class Role(db.Model):
    __tablename__ = "role"
    role_id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(128), nullable=False)

    created_at = db.Column(db.DateTime(timezone=True), default=datetime.now())
    changed_at = db.Column(db.DateTime(timezone=True), default=datetime.now())

    def __init__(self, data: dict):
        self.role_id = data["USER_ROLE_ID"]
        self.role_name = data["USER_ROLE"]


class Lpu(db.Model):
    __tablename__ = "lpus"
    id = db.Column(db.String(32), primary_key=True)
    lpu_name = db.Column(db.String(255))
    ogrn = db.Column(db.String(16))

    created_at = db.Column(db.DateTime(timezone=True), default=datetime.now())
    changed_at = db.Column(db.DateTime(timezone=True), default=datetime.now())

    def __init__(self, data: dict):
        self.id = data["LPU_ID"] if "LPU_ID" in data else data["MO_ID"]
        self.lpu_name = data["LPU_NAME"] if "LPU_NAME" in data else data["MO_NAME"]
        self.ogrn = data["OGRN"] if "OGRN" in data else None


class Specialities(db.Model):
    __tablename__ = "specialities"
    spec_code = db.Column(db.Integer, primary_key=True)
    spec_name = db.Column(db.String(255), nullable=False)

    created_at = db.Column(db.DateTime(timezone=True), default=datetime.now())
    changed_at = db.Column(db.DateTime(timezone=True), default=datetime.now())

    def __init__(self, data):
        self.spec_code = data["SPEC_CODE"]
        self.spec_name = data["SPEC_NAME"]


class UsersRole(db.Model):
    __tablename__ = "users_to_role"
    id = db.Column(db.Integer, primary_key=True)
    users_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    role_id = db.Column(db.Integer, db.ForeignKey("role.role_id", ondelete="CASCADE"))

    created_at = db.Column(db.DateTime(timezone=True), default=datetime.now())
    changed_at = db.Column(db.DateTime(timezone=True), default=datetime.now())

    def __init__(self, data: dict):
        self.users_id = data["USER_ID"]
        self.role_id = data["USER_ROLE_ID"]


class UsersSpec(db.Model):
    __tablename__ = "users_to_specialisation"
    id = db.Column(db.Integer, primary_key=True)
    users_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    spec_id = db.Column(
        db.Integer, db.ForeignKey("specialities.spec_code", ondelete="CASCADE")
    )

    created_at = db.Column(db.DateTime(timezone=True), default=datetime.now())
    changed_at = db.Column(db.DateTime(timezone=True), default=datetime.now())

    def __init__(self, data: dict):
        self.users_id = data["USER_ID"]
        self.spec_id = data["SPEC_CODE"]


class UsersLpu(db.Model):
    __tablename__ = "users_to_lpu"
    id = db.Column(db.Integer, primary_key=True)
    users_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    lpu_id = db.Column(db.String(32), db.ForeignKey("lpus.id", ondelete="CASCADE"))

    created_at = db.Column(db.DateTime(timezone=True), default=datetime.now())
    changed_at = db.Column(db.DateTime(timezone=True), default=datetime.now())

    def __init__(self, data: dict):
        self.users_id = data["USER_ID"]
        self.lpu_id = data["LPU_ID"]


class LpusMo(db.Model):
    __tablename__ = "lpus_to_mo"
    id = db.Column(db.Integer, primary_key=True)
    lpu_id = db.Column(
        db.String(32),
        db.ForeignKey("lpus.id", ondelete="CASCADE"),
        nullable=False,
    )
    mo_id = db.Column(
        db.String(32),
        db.ForeignKey("lpus.id", ondelete="CASCADE"),
    )

    created_at = db.Column(db.DateTime(timezone=True), default=datetime.now())
    changed_at = db.Column(db.DateTime(timezone=True), default=datetime.now())

    def __init__(self, data: dict):
        self.lpu_id = data["LPU_ID"]
        self.mo_id = data["MO_ID"]


class AdditionalInfo(db.Model):
    __tablename__ = "users_additional_info"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    phone = db.Column(db.String(64))
    email = db.Column(db.String(255))
    region = db.Column(db.String(128))

    created_at = db.Column(db.DateTime(timezone=True), default=datetime.now())
    changed_at = db.Column(db.DateTime(timezone=True), default=datetime.now())

    def __init__(self, data: dict):
        self.user_id = data.get("USER_ID")
        self.phone = data.get("PHONE", None)
        self.email = data.get("EMAIL", None)
        self.region = data.get("REGION_NAME", None)


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(
        db.Integer,
        primary_key=True,
        nullable=False,
    )
    login = db.Column(db.String(128), unique=True)
    last_name = db.Column(db.String(64))
    first_name = db.Column(db.String(64))
    second_name = db.Column(db.String(64))
    snils = db.Column(db.String(12))

    created_at = db.Column(db.DateTime(timezone=True), default=datetime.now())
    changed_at = db.Column(db.DateTime(timezone=True), default=datetime.now())

    def __init__(self, data: dict):
        self.login = data.get("LOGIN")
        self.last_name = data.get("LAST_NAME", None)
        self.first_name = data.get("FIRST_NAME", None)
        self.second_name = data.get("SECOND_NAME", None)
        self.snils = data.get("SNILS", None)

    lpu = relationship(UsersLpu, backref="user", cascade="all, delete-orphan")
    role = relationship(UsersRole, backref="user", cascade="all, delete-orphan")
    spec = relationship(UsersSpec, backref="user", cascade="all, delete-orphan")
    addit = relationship(AdditionalInfo, backref="user", cascade="all, delete-orphan")


# MODELS
"""
CREATE TABLE role (
    role_id SERIAL PRIMARY KEY,
    role_name VARCHAR(128) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    changed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE lpus (
    id VARCHAR(32) PRIMARY KEY,
    lpu_name VARCHAR(255),
    ogrn VARCHAR(16),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    changed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE specialities (
    spec_code INTEGER PRIMARY KEY,
    spec_name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    changed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE users_to_role (
    id SERIAL PRIMARY KEY,
    users_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role_id INTEGER REFERENCES role(role_id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    changed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE users_to_specialisation (
    id SERIAL PRIMARY KEY,
    users_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    spec_id INTEGER REFERENCES specialities(spec_code) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    changed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE users_to_lpu (
    id SERIAL PRIMARY KEY,
    users_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    lpu_id VARCHAR(32) REFERENCES lpus(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    changed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE lpus_to_mo (
    id SERIAL PRIMARY KEY,
    lpu_id VARCHAR(32) NOT NULL REFERENCES lpus(id) ON DELETE CASCADE,
    mo_id VARCHAR(32) REFERENCES lpus(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    changed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE users_additional_info (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    phone VARCHAR(64),
    email VARCHAR(255),
    region VARCHAR(128),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    changed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE users (
    id SERIAL PRIMARY KEY NOT NULL,
    login VARCHAR(128) UNIQUE,
    last_name VARCHAR(64),
    first_name VARCHAR(64),
    second_name VARCHAR(64),
    snils VARCHAR(12),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    changed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
"""

# Triggers and functions from '../../migration/versions/38a3b26752b9_add_triggers.py'
"""
CREATE OR REPLACE FUNCTION update_time()
RETURNS TRIGGER AS $$
BEGIN
NEW.changed_at = NOW(); 
RETURN NEW;
END;
$$ LANGUAGE plpgsql;
"""

"""
CREATE OR REPLACE TRIGGER update_changed_time_tr_on_{table_name}
BEFORE UPDATE ON {table_name}
FOR EACH ROW
EXECUTE FUNCTION update_time();
"""
