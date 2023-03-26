from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import validates


from config import db, bcrypt

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'

    serialize_rules = ("-recipes.user", "-_password_hash",)

    id = db.Column(db.Integer, primary_key=True)
    # validate the user's username to ensure that it is present and unique (no two users can have the same username).
    username = db.Column(db.String, unique=True, nullable=False)
    _password_hash = db.Column(db.String)
    image_url = db.Column(db.String)
    bio = db.Column(db.String)

    # have many recipes.
    recipes = db.relationship("Recipe", backref='user')

    # @validates("username")
    # def validate_username(self, key, username):
    #     if not username:
    #         raise ValueError("Must have username.")
    
    # ================= incorporate bcrypt to create a secure password. ====================
    @hybrid_property
    def password_hash(self):
        # Attempts to access the password_hash should be met with an AttributeError.
        raise AttributeError("Password hashes may not be accessed")
    
    @password_hash.setter
    def password_hash(self, password):
        password_hash = bcrypt.generate_password_hash(
            password.encode('utf-8')
        )
        self._password_hash = password_hash.decode('utf-8')
    
    def authenticate(self, password):
        return bcrypt.check_password_hash(
            self._password_hash, password.encode('utf-8')
        )
    # =====================================================================================

    def __repr__(self):
        return f'''<User {self.id}: Username: {self.username}>'''

class Recipe(db.Model, SerializerMixin):
    __tablename__ = 'recipes'
    __table_args__ = (
        db.CheckConstraint('length(instructions) >= 50'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    instructions = db.Column(db.String, nullable=False)
    minutes_to_complete = db.Column(db.Integer)

    # a recipe belongs to a user.
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    
    # validates decorator is for complicated python level check????
    # @validates("instructions")
    # def validate_instructions(self, key, instructions):
    #     if len(instructions) < 50:
    #         raise ValueError("instructions must be present and at least 50 characters long.")


    def __repr__(self):
        return f'''<Recipe {self.id}: Title: {self.title}>'''