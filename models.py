from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String,index=True)
    email = Column(String, unique=True, index=True)
    phone = Column(String, unique=True, index=True)
    role = Column(String, index=True)
    hashed_password = Column(String)
    addresses = relationship("Address", back_populates="user", cascade="all, delete-orphan")
    cart_items = relationship("CartItem", back_populates="user", cascade="all, delete-orphan")

class Address(Base):
    __tablename__ = 'addresses'
    
    id = Column(Integer, primary_key=True, index=True)
    street = Column(String)
    city = Column(String)
    zip = Column(String)
    
    # ForeignKey to link the Address to the User
    user_id = Column(Integer, ForeignKey('users.id'))
    
    # Relationship to the User model
    user = relationship("User", back_populates="addresses")

class CartItem(Base):
    __tablename__ = 'cart_items'
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer)
    quantity = Column(Integer)
    
    # ForeignKey to link the CartItem to the User
    user_id = Column(Integer, ForeignKey('users.id'))
    
    # Relationship to the User model
    user = relationship("User", back_populates="cart_items")