from sqlalchemy import create_engine, event, select, ForeignKey, delete, update, func, desc, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session
from sqlalchemy.exc import IntegrityError
from datetime import date
from pathlib import Path
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
import uuid

dbPath = Path(__file__).resolve().parent / 'db'
dbPath.mkdir(parents=True, exist_ok=True)
dbFilePath = dbPath.joinpath('images.db')
engine = create_engine(f'sqlite+pysqlite:///{dbFilePath.as_posix()}')

# Database Definitions

class Base(DeclarativeBase):
    pass    

class Users(Base):

    __tablename__ = 'Users'

    UserName: Mapped[str] = mapped_column(primary_key=True, index=True)
    UserPassword: Mapped[str] = mapped_column()

class Images(Base):
    
    __tablename__ = 'Images'

    ImageId : Mapped[bytes] = mapped_column(primary_key=True, index=True)
    ImageName : Mapped[str] = mapped_column()
    ImageXRes : Mapped[int] = mapped_column()
    ImageYRes : Mapped[int] = mapped_column()
    DateTaken : Mapped[date] = mapped_column()

class Albums(Base):
    
    __tablename__ = 'Albums'

    AlbumId : Mapped[str] = mapped_column(primary_key=True, index=True)
    AlbumName : Mapped[str] = mapped_column()
    AlbumOwner : Mapped[str] = mapped_column(ForeignKey('Users.UserName', ondelete="CASCADE"))

class UserImages(Base):

    __tablename__ = 'UserImages'

    ImageId : Mapped[bytes] = mapped_column(ForeignKey('Images.ImageId', ondelete="CASCADE"), primary_key=True)
    UserName: Mapped[str] = mapped_column(ForeignKey('Users.UserName', ondelete="CASCADE"), primary_key=True)

class AlbumImages(Base):
    
    __tablename__ = 'ImageAlbums'

    ImageId : Mapped[bytes] = mapped_column(ForeignKey('Images.ImageId', ondelete="CASCADE"), primary_key=True)
    AlbumId : Mapped[str] = mapped_column(ForeignKey('Albums.AlbumId', ondelete="CASCADE"), primary_key=True)

@event.listens_for(engine, 'connect')
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute('PRAGMA foreign_keys=ON;')
    cursor.execute('PRAGMA journal_mode = WAL;')
    cursor.close()

Base.metadata.create_all(engine)

# Database User Operations

def add_user(username, user_password):
    with Session(engine) as session:
        try:
            hasher = PasswordHasher()
            user_password_hash = hasher.hash(user_password)
            added_user = Users(UserName = username, UserPassword = user_password_hash)
            session.add(added_user)
            session.flush()
            all_album = Albums(AlbumId = uuid.uuid4().hex, AlbumName = 'All', AlbumOwner = username)
            fav_album = Albums(AlbumId = uuid.uuid4().hex, AlbumName = 'Favourite', AlbumOwner = username)
            session.add_all([all_album, fav_album])
            session.commit()
        except IntegrityError:
            session.rollback()

def delete_user(user_id):
    with Session(engine) as session:
        delete_stmt = delete(Users).where(Users.UserName == user_id)
        result = session.execute(delete_stmt)
        session.commit()

def get_user_statistics():
    with Session(engine) as session:
        user_stmt = select(Users)
        user_data = session.scalars(user_stmt).all()
        user_dict = {}
        for user in user_data:
            image_stmt = select(func.count()).select_from(UserImages).where(UserImages.UserName == user.UserName)
            image_count = session.scalars(image_stmt).one()
            user_dict[user.UserName] = image_count

        return user_dict
            
def authenticate_user_with_db(user_id, password):
    with Session(engine) as session:
        hasher = PasswordHasher()
        select_stmt = select(Users.UserPassword).where(Users.UserName == user_id)
        hash_from_db = session.scalars(select_stmt).first()
        try:
            if hasher.verify(hash_from_db, password):
                return True
        except VerifyMismatchError:
            return False

# Database Image Operations

def insert_image(img_id, img_name, img_x_res, img_y_res, img_date_taken, username):
    with Session(engine) as session:
        try:

            select_stmt = select(Images).where(Images.ImageId == img_id)
            result = session.scalars(select_stmt).first()

            if result is None:
                session.add(Images(ImageId=img_id, ImageName=img_name, ImageXRes=img_x_res, ImageYRes=img_y_res, DateTaken=img_date_taken)) 
            
            user_linker = UserImages(ImageId=img_id, UserName=username)
            session.add(user_linker)
            session.flush()

            album = session.scalars(select(Albums).where(Albums.AlbumOwner == username, Albums.AlbumName == "All")).first()
            album_linker = AlbumImages(ImageId=img_id, AlbumId=album.AlbumId)
            session.add(album_linker)
            session.commit()

        except IntegrityError:
            session.rollback()

def find_image(username, img_id):
    with Session(engine) as session:
        select_stmt = select(Images).join(UserImages, UserImages.ImageId == Images.ImageId).where(Images.ImageId == img_id, UserImages.UserName == username)
        values = session.scalars(select_stmt).first()
        return (values.ImageId.hex(), values.ImageName, values.ImageXRes, values.ImageYRes, values.DateTaken)
    
def get_list_offset(username, offset, album_id):
    with Session(engine) as session:
        select_stmt = select(Images).select_from(AlbumImages).join(Images, AlbumImages.ImageId == Images.ImageId).join(Albums, AlbumImages.AlbumId == Albums.AlbumId).where(AlbumImages.AlbumId == album_id, Albums.AlbumOwner == username).limit(50).offset(offset).order_by(desc(Images.DateTaken))
        data = session.scalars(select_stmt).all()
        return data

def check_owner_match(username, img_id):
    with Session(engine) as session:
        select_stmt = select(func.count()).select_from(UserImages).where(UserImages.UserName == username, UserImages.ImageId == img_id)
        result = session.scalar(select_stmt)
        if result == 0:
            return False
        else:
            return True

def delete_image(username, img_id):
    with Session(engine) as session:

        select_albums_stmt = select(AlbumImages).join(Albums, AlbumImages.AlbumId == Albums.AlbumId).where(AlbumImages.ImageId == img_id, Albums.AlbumOwner == username)

        album_images = session.scalars(select_albums_stmt).all()
        
        for entry in album_images:
            delete_stmt = delete(AlbumImages).where(AlbumImages.AlbumId == entry.AlbumId, AlbumImages.ImageId == entry.ImageId)
            session.execute(delete_stmt)
            
        session.execute(delete(UserImages).where(UserImages.ImageId == img_id, UserImages.UserName == username))

        select_user_stmt = select(func.count()).select_from(UserImages).where(UserImages.ImageId == img_id)
        result = session.scalar(select_user_stmt)

        print(result)

        if (result == 0) or (result is None):
            session.execute(delete(Images).where(Images.ImageId == img_id))
            session.commit()
            return True

        session.commit()
        return False

# Album Operations

def get_album_list(username):
    with Session(engine) as session:
        select_stmt = select(Albums).where(Albums.AlbumOwner == username)
        album_list = session.scalars(select_stmt).all()
        return album_list

def create_album(username, album_name):
    with Session(engine) as session:
        album = Albums(AlbumId=uuid.uuid4().hex, AlbumName=album_name, AlbumOwner=username)
        session.add(album)
        session.commit()

def delete_album(username, album_id):
    with Session(engine) as session:
        del_stmt = delete(Albums).where(Albums.AlbumId == album_id, Albums.AlbumOwner == username)
        session.execute(del_stmt)
        session.commit()

def add_image_to_album(username, img_id, album_id):
    with Session(engine) as session:
        album = session.scalars(select(Albums).where(Albums.AlbumId == album_id)).first()
        user_image = session.scalars(select(UserImages).where(UserImages.UserName == username, UserImages.ImageId == img_id)).one_or_none()
        if (album is not None) and (user_image is not None) and (album.AlbumOwner == username):
            album_image_linker = AlbumImages(AlbumId = album_id, ImageId = img_id)
            session.add(album_image_linker)
            session.commit()
            return True
        else:
            session.rollback()
            return False

def del_image_from_album(username, img_id, album_id):
    with Session(engine) as session:
        album = session.scalars(select(Albums).where(Albums.AlbumId == album_id)).first()
        user_image = session.scalars(select(UserImages).where(UserImages.UserName == username, UserImages.ImageId == img_id)).one_or_none()
        if (album is not None) and (user_image is not None) and (album.AlbumOwner == username):
            del_stmt = delete(AlbumImages).where(AlbumImages.AlbumId == album_id, AlbumImages.ImageId == img_id)
            session.execute(del_stmt)
            session.commit()
        else:
            session.rollback()