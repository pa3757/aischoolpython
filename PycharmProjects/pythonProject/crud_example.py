from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# 데이터베이스 URI 설정 (MySQL 데이터베이스 정보 입력)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://username:password@localhost/db_name'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# SQLAlchemy 객체 생성
db = SQLAlchemy(app)

# Post 모델 정의 (게시글을 나타내는 테이블)
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)

# 모든 게시글을 가져오는 엔드포인트
@app.route('/posts', methods=['GET'])
def get_posts():
    posts = Post.query.all()
    return jsonify([{'id': post.id, 'title': post.title, 'content': post.content} for post in posts])

# 새로운 게시글을 추가하는 엔드포인트
@app.route('/posts', methods=['POST'])
def add_post():
    data = request.get_json()
    new_post = Post(title=data['title'], content=data['content'])
    db.session.add(new_post)
    db.session.commit()
    return jsonify({'id': new_post.id, 'title': new_post.title, 'content': new_post.content}), 201

# 기존 게시글을 수정하는 엔드포인트
@app.route('/posts/<int:id>', methods=['PUT'])
def update_post(id):
    data = request.get_json()
    post = Post.query.get_or_404(id)
    post.title = data['title']
    post.content = data['content']
    db.session.commit()
    return jsonify({'id': post.id, 'title': post.title, 'content': post.content})

# 기존 게시글을 삭제하는 엔드포인트
@app.route('/posts/<int:id>', methods=['DELETE'])
def delete_post(id):
    post = Post.query.get_or_404(id)
    db.session.delete(post)
    db.session.commit()
    return jsonify({'message': 'Post deleted'})

# Flask 애플리케이션 실행
if __name__ == '__main__':
    db.create_all()  # 데이터베이스 테이블 생성
    app.run(debug=True)
