from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy import event, text

from .database import db


"""
CREATE OR REPLACE FUNCTION update_time()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE users
    SET changed_at = NOW() 
    WHERE id = NEW.users_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER update_time_trigger_usc
AFTER UPDATE ON user_to_specialisation
FOR EACH ROW
EXECUTE FUNCTION update_time();

CREATE TRIGGER update_time_trigger_utr
AFTER UPDATE ON users_to_role 
FOR EACH ROW
EXECUTE FUNCTION update_time();

CREATE TRIGGER update_time_trigger_utl
AFTER UPDATE ON user_to_lpu 
FOR EACH ROW
EXECUTE FUNCTION update_time();

CREATE OR REPLACE FUNCTION update_changed_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.changed_at := NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_time_trigger_u
BEFORE UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION update_changed_at();

CREATE INDEX idx_role ON role (role_id);
CREATE INDEX idx_lpus ON lpus (lpus_id);
CREATE INDEX idx_specialities ON specialities (spec_code);
CREATE INDEX idx_users_additional_info ON users_additional_info (user_id);
CREATE INDEX idx_users_to_role ON users_to_role (users_id, role_id);
CREATE INDEX idx_users_to_specialisation ON users_to_specialisation (users_id, spec_id);
CREATE INDEX idx_user_to_lpu ON user_to_lpu (users_id, lpus_id);
CREATE INDEX idx_lpus_to_mo ON lpus_to_mo (mo_id, lpus_id);
CREATE INDEX idx_users ON users (login);
"""


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
        db.ForeignKey("users.id"),
        nullable=False,
    )
    role_id = db.Column(db.Integer, db.ForeignKey("role.role_id"))

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
        db.ForeignKey("users.id"),
        nullable=False,
    )
    spec_id = db.Column(db.Integer, db.ForeignKey("specialities.spec_code"))

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
        db.ForeignKey("users.id"),
        nullable=False,
    )
    lpu_id = db.Column(db.String(32), db.ForeignKey("lpus.id"))

    created_at = db.Column(db.DateTime(timezone=True), default=datetime.now())
    changed_at = db.Column(db.DateTime(timezone=True), default=datetime.now())


class LpusMo(db.Model):
    __tablename__ = "lpus_to_mo"
    id = db.Column(db.Integer, primary_key=True)
    lpu_id = db.Column(
        db.String(32),
        db.ForeignKey("lpus.id"),
        nullable=False,
    )
    mo_id = db.Column(
        db.String(32),
        db.ForeignKey("lpus.id"),
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
        db.ForeignKey("users.id"),
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


@event.listens_for(AdditionalInfo, "before_update")
def user_update_handler(mapper, connection, target):
    connection.execute(
        text("UPDATE users SET changed_at = NOW() WHERE id = :user_id").params(
            user_id=target.users_id
        )
    )


@event.listens_for(UsersRole, "before_update")
@event.listens_for(UsersLpu, "before_update")
@event.listens_for(UsersSpec, "before_update")
def user_update_handler(mapper, connection, target: User):
    target.changed_at = datetime.now()


@event.listens_for(User, "before_update")
def user_update_handler(mapper, connection, target: User):
    target.changed_at = datetime.now()
