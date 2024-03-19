from flask import (Flask, abort, flash, jsonify, redirect, render_template,
                   request, session, url_for)
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import (Boolean, Column, Date, DateTime, Float, ForeignKey,
                        Integer, BigInteger, String)
from flask_migrate import Migrate
from models import db, setup_db
import logging
from logging import getLogger, StreamHandler
import colorlog
from datetime import datetime
import pytz
import sys
import asyncio
from models import (User, Paper, PaperTag, ResultAbstTranslation,
                    ResultAbstSummary, ResultPaperSummary)
from skills import get_module_response
from set_log import setup_logger
from dotenv import load_dotenv
from lib import (get_paper_info, get_paper_abstract, get_paper_abstracts_from_words,
                 translate_by_deepl)
import json

load_dotenv()


logger = setup_logger(__name__) 



def create_app(db_uri="", test_config=None):
    app = Flask(__name__)
    if db_uri:
        setup_db(app, db_uri)
    else:
        setup_db(app)

    @app.route('/')
    def hello():
        return 'Hello, World!'
    
    @app.route('/api/users', methods=('POST',))
    def register_user():
        """Register a new user.
        request body:
        {
            "user_id": "josjovp",
            "name": "Taro",
            "email": "0000000@gmail.com",
        }

        return:
        {
            "success": True,
            "user": formatted user
        }
        """
        # set error status
        error = False

        # verify request body
        body = request.get_json()

        if body is None:
            abort(400)
        keys = body.keys()
        if not "user_id" in keys:
            abort(400)
        if not "name" in keys:
            abort(400)
        if not "email" in keys:
            abort(400)
        
        # create new user
        try:
            user = User(
                id=body["user_id"].lower(),
                name=body["name"],
                email=body["email"]
            )
            user.insert()
            formatted_user = user.format()
        except Exception:
            user.rollback()
            error = True
            logger.warning(sys.exc_info())
        finally:
            db.session.close()
        
        if error:
            abort(422)
        
        return jsonify({
            "success": not error,
            "user": formatted_user
        })
    
    @app.route('/api/users/<string:user_id>', methods=('GET',))
    def get_user(user_id):
        """Get user information.
        return:
        {
            "success": True,
            "user": formatted user
        }
        """
        # set error status
        error = False

        # get user
        try:
            user = db.session.get(User, user_id)
            if user is None:
                abort(404)
            formatted_user = user.format()
        except Exception:
            error = True
            logger.warning(sys.exc_info())
        finally:
            db.session.close()
        
        if error:
            abort(422)
        
        return jsonify({
            "success": not error,
            "user": formatted_user
        })

    @app.route('/api/users/<string:user_id>/papers', methods=('GET',))
    def get_user_papers(user_id):
        """Get papers written by the user.
        return:
        {
            "success": True,
            "papers": formatted papers
        }
        """
        # set error status
        error = False

        # verity that the user exists
        try:
            user = db.session.get(User, user_id)
            if user is None:
                abort(404)
        except Exception:
            error = True
            logger.warning(sys.exc_info())

        if not error:
            try:
                papers = user.papers
                formatted_papers = []
                for paper in papers:
                    formatted_paper = paper.format()
                    formatted_paper['tag'] = [tag.tag for tag in paper.tags]
                    formatted_papers.append(formatted_paper)
            except Exception:
                error = True
                logger.warning(sys.exc_info())
            finally:
                db.session.close()
        
        if error:
            abort(422)
        
        return jsonify({
            "success": not error,
            "papers": formatted_papers
        })
    
    @app.route('/api/users/<string:user_id>/results-paper-summary', methods=('GET',))
    def get_user_results_paper_summary(user_id):
        """Get paper summary
        return:
        {
            "success": True,
            "results_paper_summary": formatted results_paper_summary
        }
        """
        # set error status
        error = False

        # verity that the user exists
        try:
            user = db.session.get(User, user_id)
            if user is None:
                abort(404)
        except Exception:
            error = True
            logger.warning(sys.exc_info())

        if not error:
            try:
                results_paper_summary = user.results_paper_summary
                formatted_results_paper_summary = []
                for results_paper_summary in results_paper_summary:
                    formatted_results_paper_summary = results_paper_summary.format()
            except Exception:
                error = True
                logger.warning(sys.exc_info())
            finally:
                db.session.close()
        
        if error:
            abort(422)
        
        return jsonify({
            "success": not error,
            "results_paper_summary": formatted_results_paper_summary
        })
    
    @app.route('/api/users/<string:user_id>/results-abst-summary', methods=('POST',))
    def register_user_result_abst_summary(user_id):
        """Register a new result abst summary.
        request body:
        {
            "search_words": ["word1", "word2", ...],
            "language": "English"
        }

        return:
        {
            "success": True,
            "result_abst_summary": formatted result_abst_summary
        }
        """

        # set error status
        error = False

        # verify request body
        body = request.get_json()

        if body is None:
            abort(400)
        keys = body.keys()
        if not "search_words" in keys:
            abort(400)
        search_words = body["search_words"]
        if not "language" in keys:
            abort(400)
        language = body["language"]

        # retrieve user
        try:
            user = db.session.get(User, user_id)
            if user is None:
                abort(404)
        except Exception:
            error = True
            logger.warning(sys.exc_info())
        
        # create new result abst summary
        if not error:
            try:
                abstract_list = asyncio.run(get_paper_abstracts_from_words(
                                                words=search_words
                                            )
                )
                if abstract_list is None:
                    abort(404)
                # summarize each abstract
                summarized_abstract_list = []
                for i, abstract in enumerate(abstract_list):
                    content_variables = {
                        "language": "English",
                        "abstract": abstract
                    }
                    json_response = get_module_response("abst_sum", content_variables)
                    summarized_abstract = json.loads(json_response)["summary"]
                    summarized_abstract_list.append(summarized_abstract)
                    logger.info(f"Summarized abstract {i+1} of {len(abstract_list)}.")

            except Exception:
                error = True
                logger.warning(sys.exc_info())
            
            try:
                result_abst_summary = ResultAbstSummary(
                    abst_summary=summarized_abstract,
                    language=language
                )
                result_abst_summary.user = user
                result_abst_summary.insert()
                formatted_result_abst_summary = result_abst_summary.format()
            except Exception:
                error = True
                logger.warning(sys.exc_info())
            
            if error:
                abort(422)
            
        return jsonify({
            "success": not error,
            "result_abst_summary": formatted_result_abst_summary
        })
    
    @app.route('/api/users/<string:user_id>/results-abst-summary', methods=('GET',))
    def get_user_results_abst_summary(user_id):
        """Get abstract summary
        return:
        {
            "success": True,
            "results_abst_summary": formatted results_abst_summary
        }
        """
        # set error status
        error = False

        # verity that the user exists
        try:
            user = db.session.get(User, user_id)
            if user is None:
                abort(404)
        except Exception:
            error = True
            logger.warning(sys.exc_info())

        if not error:
            try:
                results_abst_summary = user.results_abst_summary
                formatted_results_abst_summary = []
                for results_abst_summary in results_abst_summary:
                    formatted_results_abst_summary = results_abst_summary.format()
            except Exception:
                error = True
                logger.warning(sys.exc_info())
            finally:
                db.session.close()
        
        if error:
            abort(422)
        
        return jsonify({
            "success": not error,
            "results_abst_summary": formatted_results_abst_summary
        })
    
    @app.route('/api/users/<string:user_id>/papers', methods=('POST',))
    def register_paper(user_id):
        """Register a new paper.
        request body:
        {
            "pmid": 12345678,
        }

        return:
        {
            "success": True,
            "paper": formatted paper
        }
        """
        # set error status
        error = False

        # verify request body
        body = request.get_json()

        if body is None:
            abort(400)
        keys = body.keys()
        if not "pmid" in keys:
            abort(400)
        pmid = body["pmid"]

        # retrieve user
        try:
            user = db.session.get(User, user_id)
            if user is None:
                abort(404)
        except Exception:
            error = True
            logger.warning(sys.exc_info())
        
        # create new paper
        try:
            # get paper info from Pubmed
            paper_info = asyncio.run(get_paper_info(pmid))
            if paper_info is None:
                abort(404)
            # get paper abstract
            paper_abstract = asyncio.run(get_paper_abstract(pmid))
            if paper_abstract is None:
                abort(404)
            paper = Paper(
                pmid=paper_info["pmid"],
                title=paper_info["title"],
                last_author=paper_info["last_author"],
                publication_date=paper_info["publication_date"],
                url=paper_info["url"],
                abstract=paper_abstract
            )
            paper.user = user
            paper.insert()
            formatted_paper = paper.format()
        except Exception:
            error = True
            logger.warning(sys.exc_info())
        finally:
            db.session.close()
        
        if error:
            abort(422)
        
        return jsonify({
            "success": not error,
            "paper": formatted_paper
        })
    
    @app.route('/api/papers/<int:id>', methods=('GET',))
    def get_paper(id):
        """Get paper information.
        return:
        {
            "success": True,
            "paper": formatted paper
        }
        """
        # set error status
        error = False

        # get paper
        try:
            paper = db.session.get(Paper, id)
            if paper is None:
                abort(404)
            formatted_paper = paper.format()
            formatted_paper['tag'] = [tag.tag for tag in paper.tags]
        except Exception:
            error = True
            logger.warning(sys.exc_info())
        finally:
            db.session.close()
        
        if error:
            abort(422)
        
        return jsonify({
            "success": not error,
            "paper": formatted_paper
        })
    
    @app.route('/api/papers/<int:id>/tags', methods=('PATCH',))
    def edit_paper_tags(id):
        """Edit paper tags.
        request body:
        {
            "tags": ["tag1", "tag2", ...]
        }

        return:
        {
            "success": True,
            "paper": formatted paper
        }
        """
        # set error status
        error = False

        # verify request body
        body = request.get_json()

        if body is None:
            abort(400)
        keys = body.keys()
        if not "tags" in keys:
            abort(400)
        tags = body["tags"]

        # retrieve paper
        try:
            paper = db.session.get(Paper, id)
            formatted_paper = paper.format()
            if paper is None:
                abort(404)
        except Exception:
            error = True
            logger.warning(sys.exc_info())
        
        # edit paper tags
        try:
            formatted_tags = []
            for tag in tags:
                paper_tag = PaperTag(
                    tag=tag
                )
                paper_tag.paper = paper
                db.session.add(paper_tag)
                formatted_tags.append(paper_tag.format())
            db.session.commit()
            formatted_paper['tag'] = formatted_tags
        except Exception:
            error = True
            logger.warning(sys.exc_info())
        
        if error:
            db.session.rollback()
            abort(422)
        
        return jsonify({
            "success": not error,
            "paper": formatted_paper
        })
    
    @app.route('/api/papers/<int:id>', methods=('DELETE',))
    def delete_paper(id):
        """Delete paper.
        return:
        {
            "success": True,
            "deleted_paper": formatted paper
        }
        """
        # set error status
        error = False

        # retrieve paper
        try:
            paper = db.session.get(Paper, id)
            formatted_paper = paper.format()
            if paper is None:
                abort(404)
            paper.delete()
        except Exception:
            error = True
            logger.warning(sys.exc_info())
        finally:
            db.session.close()
        
        if error:
            abort(422)
        
        return jsonify({
            "success": not error,
            "deleted_paper": formatted_paper
        })
    
    @app.route('/api/papers/<int:id>/results-abst-translation', methods=('POST',))
    def register_result_abst_translation(id):
        """Register a new result abst translation.
        request body:
        {
            "language": "Japanese"
        }

        return:
        {
            "success": True,
            "result_abst_translation": formatted result_abst_translation
        }
        """
        # set error status
        error = False

        # verify request body
        body = request.get_json()

        if body is None:
            abort(400)
        keys = body.keys()
        if not "language" in keys:
            abort(400)
        language = body["language"]

        # retrieve paper
        try:
            paper = db.session.get(Paper, id)
            if paper is None:
                abort(404)
        except Exception:
            error = True
            logger.warning(sys.exc_info())
        
        # create new result abst translation
        try:
            abstract = paper.abstract
            translated_abstract = translate_by_deepl(
                abstract,
                language
            )
            result_abst_translation = ResultAbstTranslation(
                translated_abstract=translated_abstract,
                language=language
            )
            result_abst_translation.paper = paper
            result_abst_translation.insert()
            formatted_result_abst_translation = result_abst_translation.format()
        except Exception:
            error = True
            logger.warning(sys.exc_info())
        finally:
            db.session.close()
        
        if error:
            abort(422)
        
        return jsonify({
            "success": not error,
            "result_abst_translation": formatted_result_abst_translation
        })
    
    @app.route('/api/results-paper-summary/<int:id>', methods=('DELETE',))
    def delete_result_paper_summary(id):
        """Delete results_paper_summary.
        return:
        {
            "success": True,
            "results_paper_summary_id": id
        }
        """
        # set error status
        error = False

        # retrieve results_paper_summary
        try:
            results_paper_summary = db.session.get(ResultPaperSummary, id)
            if results_paper_summary is None:
                abort(404)
            results_paper_summary.delete()
        except Exception:
            error = True
            logger.warning(sys.exc_info())
        finally:
            db.session.close()
        
        if error:
            abort(422)
        
        return jsonify({
            "success": not error,
            "results_paper_summary_id": id
        })
    
    @app.route('/api/results-abst-summary/<int:id>', methods=('DELETE',))
    def delete_result_abst_summary(id):
        """Delete results_abst_summary.
        return:
        {
            "success": True,
            "results_abst_summary_id": id
        }
        """
        # set error status
        error = False

        # retrieve results_abst_summary
        try:
            results_abst_summary = db.session.get(ResultAbstSummary, id)
            if results_abst_summary is None:
                abort(404)
            results_abst_summary.delete()
        except Exception:
            error = True
            logger.warning(sys.exc_info())
        finally:
            db.session.close()
        
        if error:
            abort(422)
        
        return jsonify({
            "success": not error,
            "results_abst_summary_id": id
        })

        
    


    
    




    return app
app = create_app()
migrate = Migrate(app, db)
if __name__ == '__main__':
    app.run(debug=True)