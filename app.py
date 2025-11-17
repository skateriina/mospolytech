from flask import Flask, render_template, request, jsonify, redirect, session, url_for
import pymysql
import traceback

app = Flask(__name__)
app.secret_key = "supersecretkey123" 

def get_db_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="",
        db="glassglow",
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor
    )



@app.route('/')
def index():
    return render_template('index.html')



@app.route('/chat', methods=['POST'])
def chat():
    user_msg = request.json.get('message', '').strip().lower()
    reply = ""

    try:

        if any(w in user_msg for w in ['привет', 'здрав', 'добрый', 'добрый день', 'добрыйвечер', 'hello']):
            reply = (
                "Здравствуйте! Мы – <b>GlassGlow</b> 💎<br>"
                "Профессиональная полировка стекол в Москве.<br>"
                "Выберите действие 👇"
            )

        elif user_msg in ['расчет стоимости', 'расчёт стоимости', 'расчет', 'расчёт', 'расчитать', 'расчитать стоимость']:
            reply = (
                "Введите параметры:<br>"
                "<b>площадь=50 этаж=3 тип=энерго</b>"
            )

        elif any(w in user_msg for w in ['площадь', 'этаж', 'тип']):
            try:
                params = {}
                for item in user_msg.replace(',', ' ').split():
                    if '=' in item:
                        k, v = item.split('=', 1)
                        params[k.strip()] = v.strip()

                area = float(params.get('площадь', 0))
                floor = int(params.get('этаж', 1))
                gtype = params.get('тип', 'обычное').lower()

                base = 250
                price = area * base

                if floor > 2:
                    price *= 1 + (floor - 2) * 0.1
                if 'энерго' in gtype:
                    price *= 1.2
                if 'прем' in gtype:
                    price *= 1.5

                reply = f"💰 Стоимость: <b>{round(price,2)} руб.</b>"
            except:
                reply = "Ошибка! Формат: площадь=50 этаж=3 тип=энерго"


        elif 'галере' in user_msg or 'фото' in user_msg or 'работ' in user_msg:
            imgs = [
                "static/img/polirovka1.jpg",
                "static/img/polirovka2.jpg",
                "static/img/polirovka3.jpg",
            ]
            reply = "".join([f'<img src="/{i}" width="200" style="margin:5px;">' for i in imgs])

        elif 'заявк' in user_msg or 'заказ' in user_msg or 'хочу' in user_msg and 'заяв' in user_msg:
            reply = '''
                <b>Оставьте заявку:</b><br><br>
                <form id="orderForm">
                    <input name="name" placeholder="Ваше имя" required><br>
                    <input name="phone" placeholder="Телефон" required><br>
                    <textarea name="comment" placeholder="Комментарий"></textarea><br>
                    <label><input type="checkbox" name="consent" required> Согласен на обработку данных</label><br><br>
                    <button type="submit">Отправить</button>
                </form>
            '''

        # Контакты
        elif 'контакт' in user_msg or 'телефон' in user_msg or 'email' in user_msg:
            reply = (
                "📞 <b>Телефон:</b> +7 999 123 45 67<br>"
                "📍 Москва<br>"
                "🌐 <a href='https://glassglow.ru' target='_blank'>glassglow.ru</a>"
            )

        elif any(word in user_msg for word in ['сколько', 'гарантия', 'результат', 'услуги', 'оплата', 'сколько времени', 'время']):
            faq = {
                "сколько": "⏱ Полировка обычно занимает 2–3 часа в зависимости от площади и степени загрязнения.",
                "сколько времени": "⏱ Полировка обычно занимает 2–3 часа в зависимости от площади и степени загрязнения.",
                "гарантия": "✔️ Мы даём гарантию на выполненные работы — сроки и условия оговариваются индивидуально.",
                "результат": "✨ Результат: прозрачные и блестящие стекла без поверхностных царапин (в пределах технических возможностей).",
                "услуги": "🔧 Мы предлагаем полировку стекол, оценку состояния, выезд на объект и консультации.",
                "оплата": "💳 Оплата наличными или картой на месте; возможна предоплата по договорённости."
            }
            for key in faq:
                if key in user_msg:
                    reply = faq[key]
                    break
            if not reply:

                reply = "Напишите, пожалуйста, конкретно: «сколько времени», «гарантия», «оплата» или «результат»."

        else:
            reply = "Команда не распознана 🤔"

    except:
        traceback.print_exc()
        reply = "Серверная ошибка."

    return jsonify({"reply": reply})



@app.route('/order', methods=['POST'])
def order():
    try:
        name = request.form.get("name")
        phone = request.form.get("phone")
        comment = request.form.get("comment")

        conn = get_db_connection()
        with conn.cursor() as cur:
            sql = "INSERT INTO orders (name, phone, comment) VALUES (%s, %s, %s)"
            cur.execute(sql, (name, phone, comment))
        conn.commit()
        conn.close()

        return jsonify({"status": "ok", "msg": "Спасибо! Мы свяжемся 👌"})

    except:
        traceback.print_exc()
        return jsonify({"status": "error", "msg": "Ошибка записи"}), 500



ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "1234" 


@app.route('/admin', methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        if request.form.get("username") == ADMIN_USERNAME and request.form.get("password") == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect('/admin/panel')
        return render_template("admin_login.html", error="Неверный логин или пароль")

    return render_template("admin_login.html")


@app.route('/admin/panel')
def admin_panel():
    if not session.get("admin"):
        return redirect('/admin')

    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM orders ORDER BY id DESC")
        orders = cur.fetchall()
    conn.close()

    return render_template("admin_panel.html", orders=orders)


@app.route('/admin/status', methods=['POST'])
def change_status():
    if not session.get("admin"):
        return jsonify({"status": "denied"})

    order_id = request.form.get("id")
    new_status = request.form.get("status")

    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("UPDATE orders SET status=%s WHERE id=%s", (new_status, order_id))
    conn.commit()
    conn.close()

    return jsonify({"status": "ok"})


@app.route('/admin/delete', methods=['POST'])
def delete_order():
    if not session.get("admin"):
        return jsonify({"status": "denied"})

    order_id = request.form.get("id")
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("DELETE FROM orders WHERE id=%s", (order_id,))
    conn.commit()
    conn.close()

    return jsonify({"status": "ok"})


if __name__ == '__main__':
    app.run(debug=True)
