from operator import index
import os
import faiss
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import current_user
from config import Config
from models import db, User, Document
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import bcrypt
from werkzeug.utils import secure_filename
from flask_migrate import Migrate
from utils.pdf_processor import extract_text_from_pdf, chunk_text
from utils.embedding import create_embeddings
from utils.vector_store import save_faiss_index, retrieve_chunks
from utils.llm import generate_answer

import pickle    # for ask route part

# -------------------- App Setup --------------------
app = Flask(__name__)
app.config.from_object(Config)
app.config["UPLOAD_FOLDER"] = "uploads"
app.config["ALLOWED_EXTENSIONS"] = {"pdf", "txt"}

db.init_app(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# -------------------- Helpers --------------------
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# -------------------- Routes --------------------
@app.route("/")
def home():
    return redirect(url_for("login"))

# -------------------- REGISTER --------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        new_user = User(username=username, email=email, password_hash=hashed_password.decode('utf-8'))
        db.session.add(new_user)
        db.session.commit()

        flash("Account created successfully!", "success")
        return redirect(url_for("login"))
    return render_template("register.html")

# -------------------- LOGIN --------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email=email).first()

        if user and bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
            login_user(user)
            return redirect(url_for("dashboard"))
        flash("Invalid credentials", "danger")
    return render_template("login.html")

# -------------------- DASHBOARD --------------------
@app.route("/dashboard", methods=["GET"])
@login_required
def dashboard():
    documents = Document.query.filter_by(user_id=current_user.id).all()
    return render_template("dashboard.html", documents=documents)

# -------------------- UPLOAD --------------------
@app.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    if request.method == "POST":
        if "file" not in request.files:
            flash("No file selected", "danger")
            return redirect(request.url)

        file = request.files["file"]
        if file.filename == "":
            flash("No file selected", "danger")
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            user_folder = os.path.join(app.config["UPLOAD_FOLDER"], f"user_{current_user.id}")
            os.makedirs(user_folder, exist_ok=True)
            file_path = os.path.join(user_folder, filename)
            file.save(file_path)

            # Save DB record first
            new_doc = Document(
                user_id=current_user.id,
                filename=filename,
                file_path=file_path,
                vector_index_path=""
            )
            db.session.add(new_doc)
            db.session.commit()

            # RAG processing
            text = extract_text_from_pdf(file_path)
            chunks = chunk_text(text)
            embeddings = create_embeddings(chunks)

            # Create vector folder
            vector_folder = os.path.join("vector_store", f"user_{current_user.id}")
            os.makedirs(vector_folder, exist_ok=True)

            index_path = os.path.join(vector_folder, f"{filename}.index")

            # ✅ Save FAISS index
            save_faiss_index(embeddings, index_path)

            # ✅ SAVE CHUNKS FILE (THIS WAS MISSING)
            import pickle

            chunks_path = index_path.replace(".index", "_chunks.pkl")

            with open(chunks_path, "wb") as f:
                pickle.dump(chunks, f)

            print("Chunks saved at:", chunks_path)

            # Save index path in DB
            new_doc.vector_index_path = index_path
            db.session.commit()

            flash("File uploaded and processed successfully!", "success")
            return redirect(url_for("dashboard"))

        flash("Invalid file type", "danger")

    return render_template("upload.html")

#########ASK ROUTE - RAG LOGIC #########
import pickle
import os

@app.route("/ask/<int:doc_id>", methods=["GET", "POST"])
@login_required
def ask(doc_id):
    from models import Document
    from utils.embedding import create_embeddings
    from utils.vector_store import retrieve_chunks
    from utils.llm import generate_answer

    document = Document.query.get_or_404(doc_id)
    answer = None

    if request.method == "POST":
        question = request.form.get("question")

        try:
            query_embedding = create_embeddings([question])

            chunks_path = document.vector_index_path.replace(".index", "_chunks.pkl")

            if not os.path.exists(chunks_path):
                answer = "Chunks file missing. Please re-upload the document."
            else:
                with open(chunks_path, "rb") as f:
                    chunks = pickle.load(f)

                relevant_chunks = retrieve_chunks(
                    document.vector_index_path,
                    query_embedding,
                    chunks
                )

                context = "\n\n".join(relevant_chunks)
                answer = generate_answer(context, question)
                print("INDEX PATH:", document.vector_index_path)

            chunks_path = document.vector_index_path.replace(".index", "_chunks.pkl")

            print("CHUNKS PATH:", chunks_path)
            print("EXISTS?", os.path.exists(chunks_path))

        except Exception as e:
            answer = f"Error: {str(e)}"

    return render_template("ask.html", document=document, answer=answer)
    


# -------------------- DELETE DOCUMENT --------------------
@app.route("/delete/<int:doc_id>")
@login_required
def delete_document(doc_id):
    doc = Document.query.get_or_404(doc_id)
    if doc.user_id != current_user.id:
        flash("Unauthorized action", "danger")
        return redirect(url_for("dashboard"))

    # Delete files
    if os.path.exists(doc.file_path):
        os.remove(doc.file_path)
    if doc.vector_index_path and os.path.exists(doc.vector_index_path):
        os.remove(doc.vector_index_path)

    db.session.delete(doc)
    db.session.commit()
    flash(f"{doc.filename} deleted successfully!", "success")
    return redirect(url_for("dashboard"))

# -------------------- LOGOUT --------------------
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

# -------------------- MAIN --------------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)