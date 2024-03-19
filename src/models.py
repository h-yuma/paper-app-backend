from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import (Boolean, Column, Date, DateTime, Float, ForeignKey,
                        Integer, BigInteger, String, ARRAY)
import os
from datetime import datetime
import semantic_kernel as sk
from dotenv import load_dotenv

load_dotenv()


DATABASE_PATH = f'postgresql://{os.environ["DATABASE_USER"]}' + \
                f':{os.environ["DATABASE_PASSWORD"]}' + \
                f'@{os.environ["DATABASE_ENDPOINT"]}:5432' + \
                f'/{os.environ["DATABASE_NAME"]}'

db = SQLAlchemy()

# setup function
def setup_db(app, database_path=DATABASE_PATH):
    """Binds a flask application and a SQLAlchemy service.

    Arguments:
        app (flask instance): flask app instance
        database_path (string): database uri

    Returns:
        None
    """
    app.config['SQLALCHEMY_DATABASE_URI'] = database_path
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)


# --------------------------------------------------------------------------- #
# User
# Have id, user_id, name, email, created_at
# --------------------------------------------------------------------------- #
class User(db.Model):
    __tablename__ = 'users'

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    created_at = Column(Date, nullable=False)
    papers = db.relationship(
        'Paper', backref='user', order_by='Paper.id',
        cascade='all, delete-orphan', cascade_backrefs=False
    )
    results_abst_summary = db.relationship(
        'ResultAbstSummary', backref='user', order_by='ResultAbstSummary.id',
        cascade='all, delete-orphan', cascade_backrefs=False
    )
    results_paper_summary = db.relationship(
        'ResultPaperSummary', backref='user', order_by='ResultPaperSummary.id',
        cascade='all, delete-orphan', cascade_backrefs=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.init_on_load()
    
    def init_on_load(self):
        self.created_at = datetime.now()
    
    def __repr__(self):
        return f'<User {self.id} {self.name}>'
    
    def insert(self):
        db.session.add(self)
        db.session.commit()
    
    def update(self):
        db.session.commit()
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()
    
    def rollback(self):
        db.session.rollback()

    def close_session(self):
        db.session.close()

    def format(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'created_at': self.created_at
        }

# --------------------------------------------------------------------------- #
# Paper
# Have id, title, last_author, publication_date, url, abstract,
# translated_abstract, tags, ai_tags, created_at
# --------------------------------------------------------------------------- #
class Paper(db.Model):
    __tablename__ = 'papers'

    id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    pmid = Column(String, nullable=False)
    title = Column(String, nullable=False)
    last_author = Column(String, nullable=False)
    publication_date = Column(Date, nullable=False)
    url = Column(String, nullable=False)
    abstract = Column(String, nullable=False)
    created_at = Column(Date, nullable=False)
    tags = db.relationship(
        'PaperTag', backref='paper', order_by='PaperTag.id',
        cascade='all, delete-orphan', cascade_backrefs=False
    )
    results_abst_translation = db.relationship(
        'ResultAbstTranslation', backref='paper', order_by='ResultAbstTranslation.id',
        cascade='all, delete-orphan', cascade_backrefs=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.init_on_load()
    
    def init_on_load(self):
        self.created_at = datetime.now()
    
    def __repr__(self):
        return f'<Paper {self.id} {self.title}>'
    
    def insert(self):
        db.session.add(self)
        db.session.commit()
    
    def update(self):
        db.session.commit()
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()
    
    def rollback(self):
        db.session.rollback()
    
    def close_session(self):
        db.session.close()
    
    def format(self):
        return {
            'id': self.id,
            'title': self.title,
            'last_author': self.last_author,
            'publication_date': self.publication_date,
            'url': self.url,
            'abstract': self.abstract,
            'created_at': self.created_at
        }

# --------------------------------------------------------------------------- #
# PaperTag
# Have id, paper_id, tag, created_at
# --------------------------------------------------------------------------- #
class PaperTag(db.Model):
    __tablename__ = 'paper_tags'

    id = Column(Integer, primary_key=True)
    paper_id = Column(Integer, ForeignKey('papers.id'), nullable=False)
    tag = Column(String, nullable=False)
    created_at = Column(Date, nullable=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.init_on_load()
    
    def init_on_load(self):
        self.created_at = datetime.now()
    
    def __repr__(self):
        paper = db.session.get(Paper, self.paper_id)
        return f'<PaperTag {self.id} {paper.title} {self.tag}>'
    
    def insert(self):
        db.session.add(self)
        db.session.commit()
    
    def update(self):
        db.session.commit()
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()
    
    def rollback(self):
        db.session.rollback()
    
    def close_session(self):
        db.session.close()
    
    def format(self):
        return {
            'id': self.id,
            'paper_id': self.paper_id,
            'tag': self.tag,
            'created_at': self.created_at
        }

# --------------------------------------------------------------------------- #
# ResultAbstTranslation
# Have id, paper_id, translated_abstract, language, created_at
# --------------------------------------------------------------------------- #
class ResultAbstTranslation(db.Model):
    __tablename__ = 'results_abst_translation'

    id = Column(Integer, primary_key=True)
    paper_id = Column(Integer, ForeignKey('papers.id'), nullable=False)
    translated_abstract = Column(String, nullable=False)
    language = Column(String, nullable=False)
    created_at = Column(Date, nullable=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.init_on_load()
    
    def init_on_load(self):
        self.created_at = datetime.now()
    
    def __repr__(self):
        paper = db.session.get(Paper, self.paper_id)
        return f'<ResultAbstTranslation {self.id} {paper.title}>'
    
    def insert(self):
        db.session.add(self)
        db.session.commit()
    
    def update(self):
        db.session.commit()
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()
    
    def rollback(self):
        db.session.rollback()
    
    def close_session(self):
        db.session.close()
    
    def format(self):
        return {
            'id': self.id,
            'paper_id': self.paper_id,
            'translated_abstract': self.translated_abstract,
            'language': self.language,
            'created_at': self.created_at
        }
    

# --------------------------------------------------------------------------- #
# ResultAbstSummary
# Have id, paper_id, summary, created_at
# --------------------------------------------------------------------------- #
class ResultAbstSummary(db.Model):
    __tablename__ = 'results_abst_summary'

    id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    abst_summary = Column(String, nullable=False)
    language = Column(String, nullable=False)
    created_at = Column(Date, nullable=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.init_on_load()
    
    def init_on_load(self):
        self.created_at = datetime.now()
    
    def __repr__(self):
        return f'<ResultAbstSummary {self.id} {self.search_words}>'
    
    def insert(self):
        db.session.add(self)
        db.session.commit()
    
    def update(self):
        db.session.commit()
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()
    
    def rollback(self):
        db.session.rollback()
    
    def close_session(self):
        db.session.close()
    
    def format(self):
        return {
            'id': self.id,
            'abst_summary': self.abst_summary,
            'language': self.language,
            'created_at': self.created_at
        }


# --------------------------------------------------------------------------- #
# ResultPaperSummary
# Have id, paper_id, summary, created_at
# --------------------------------------------------------------------------- #
class ResultPaperSummary(db.Model):
    __tablename__ = 'results_paper_summary'

    id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    paper_summary = Column(String, nullable=False)
    length = Column(String, nullable=False)
    language = Column(String, nullable=False)
    created_at = Column(Date, nullable=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.init_on_load()

    def init_on_load(self):
        self.created_at = datetime.now()
    
    def __repr__(self):
        return f'<ResultPaperSummary {self.id}>'
    
    def insert(self):
        db.session.add(self)
        db.session.commit()
    
    def update(self):
        db.session.commit()
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()
    
    def rollback(self):
        db.session.rollback()

    def close_session(self):
        db.session.close()
    
    def format(self):
        return {
            'id': self.id,
            'paper_summary': self.paper_summary,
            'length': self.length,
            'language': self.language,
            'created_at': self.created_at
        }

class AIModel:
    def __init__(self, model_name, function, kernel, context=None):
        self.role = model_name
        self.kernel = kernel  # kernelをプロパティとして追加
        self.function = function  # chat_function
        self.history = context  # チャットの履歴を格納

    async def invoke(self, context_variables=None):
        if context_variables is None:
            language = "japanese"
            abstract = "None"
            abstract_list = "None"
        else:
            language = context_variables.get("language", "japanese")
            abstract = context_variables.get("abstract", "abstract")
            abstract_list = context_variables.get(
                "abstract_list", "abstract_list"
            )
        arguments = sk.KernelArguments(
            language=language,
            abstract=abstract,
            abstract_list=abstract_list,
        )
        response = await self.kernel.invoke(
            self.function, arguments
        )  # kernel.invokeを使用
        return str(response)