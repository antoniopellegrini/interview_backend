from flask import Flask, request
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
api = Api(app)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(app)
db.init_app(app)





class PostModel(db.Model):

    __tablename__ = 'post'

    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.String(80), nullable=False)
    title = db.Column(db.String(120))
    body = db.Column(db.Text())

    def __init__(self,userId,title,body):
        self.userId = userId
        self.title = title
        self.body=body

    def json(self):
        return {
            'id': self.id,
            'userId':self.userId,
            'title':self.title,
            'body':self.body
        }

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
    
    @classmethod
    def get_all(cls):
        return cls.query.all()


    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter_by(id = _id).first()

    def edit_parameter(self,params):
        print("editing parameters")
        try:
            for param in params:
                if param != 'id':
                    self.query.filter_by(id = self.id).update({param:params[param]})
                    print(f"Parametro modificato: '{param}':'{params[param]}'")

        except Exception as e:
            print("Exception DB modifica_parametro:",e)
        db.session.commit()

class Post(Resource):
          
    def post(self):
        post = PostModel(request.args['userId'],request.args['title'],request.args['body'])
        post.save_to_db()
        return post.json(),200
    
    def patch(self):
        args = request.args
        print(args)
        postToEdit = PostModel.find_by_id(request.args['id'])
        if not postToEdit:
            return { 'message':'post not found'},400
        postToEdit.edit_parameter(args)
       
        return postToEdit.json(),200
    
    def delete(self):
       
        postToDelete = PostModel.find_by_id(request.args['id'])
        if not postToDelete:
            return { 'message':'post not found'},400
        postToDelete.delete_from_db()
        return 200


class Posts(Resource):
    def get(self):
        return  [post.json() for post in PostModel.get_all()],200

@app.before_first_request
def create_tables():
    db.create_all()

api.add_resource(Post, '/post')
api.add_resource(Posts, '/posts')

if __name__ == '__main__':
    app.run(debug=True)
