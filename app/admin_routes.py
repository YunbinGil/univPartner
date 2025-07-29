from flask import Blueprint, render_template, session, redirect, url_for, request, send_from_directory
from app import mysql
import os

admin = Blueprint('admin', __name__, template_folder='templates')

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '../uploads')

@admin.route('/admin/editor-applications')
def editor_applications():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))

    user_id = session['user_id']
    cur = mysql.connection.cursor()
    cur.execute("SELECT role FROM users WHERE user_id = %s", (user_id,))
    user = cur.fetchone()
    if not user or user['role'] != 'admin':
        return "접근 불가: 관리자만 이용 가능합니다.", 403

    cur.execute("SELECT * FROM editors ORDER BY submitted_at DESC")
    editors = cur.fetchall()
    cur.close()

    return render_template('admin_editor_list.html', editors=editors)


@admin.route('/uploads/<filename>')
def uploaded_file_admin(filename):
    if 'user_id' not in session:
        return "로그인 필요", 401

    cur = mysql.connection.cursor()
    cur.execute("SELECT role FROM users WHERE user_id = %s", (session['user_id'],))
    user = cur.fetchone()
    cur.close()

    if not user or user['role'] != 'admin':
        return "접근 불가", 403

    return send_from_directory(UPLOAD_FOLDER, filename)
