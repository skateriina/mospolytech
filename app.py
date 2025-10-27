from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/chat', methods=['POST'])
def chat():
    user_msg = request.json.get('message', '').strip().lower()
    reply = ""

    if user_msg == 'расчет стоимости':
        reply = ("Чтобы рассчитать стоимость, напишите сообщение в формате: "
                 "<br><b>площадь=50 этаж=3 тип=энерго</b><br>"
                 "Где площадь — м², этаж — этаж окна, тип — обычное/энерго/прем")

    elif any(word in user_msg for word in ['площадь', 'этаж', 'тип']):
        try:
            params = {}
            for item in user_msg.replace(',', ' ').split():
                if '=' in item:
                    key, value = item.split('=', 1)
                    params[key.strip()] = value.strip()

            area = float(params.get('площадь', 0))
            floor = int(params.get('этаж', 1))
            glass = params.get('тип', 'обычное')
            base = 250
            price = area * base
            if floor > 2:
                price *= 1 + 0.1 * (floor - 2)
            if 'энерго' in glass:
                price *= 1.2
            if 'прем' in glass:
                price *= 1.5

            reply = f'Примерная стоимость: {round(price, 2)} руб.'
        except:
            reply = 'Введите корректные данные, например: площадь=50 этаж=3 тип=энерго'

    elif 'галере' in user_msg:
        images = [
            "static/img/polirovka1.jpg",
            "static/img/polirovka2.jpg",
        ]
        reply = ''.join([f'<img src="/{img}" style="width:200px;margin:5px;border-radius:10px;">' for img in images])

    elif any(word in user_msg for word in ['заявка', 'оставить заявку']):
        reply = '''
        <b>Форма заявки:</b>
        <form id="chat-order-form">
            <input type="text" name="name" placeholder="Ваше имя" required><br>
            <input type="text" name="phone" placeholder="Телефон" required><br>
            <textarea name="comment" placeholder="Комментарий"></textarea><br>
            <button type="submit">Отправить заявку</button>
        </form>
        <script>
        const form = document.getElementById("chat-order-form");
        form.addEventListener("submit", async function(e){
            e.preventDefault();
            const formData = new FormData(form);
            const res = await fetch("/order", {method:"POST", body: formData});
            const result = await res.text();
            form.outerHTML = "<b>"+result+"</b>";
        });
        </script>
        '''

    elif 'контакт' in user_msg or 'телефон' in user_msg:
        reply = 'Наш телефон: +7 123 456 78 90<br>Email: info@glassglow.ru<br>Адрес: г. Москва, ул. Примерная, д.1'

    elif any(word in user_msg for word in ['привет', 'здравствуй', 'добрый']):
        reply = 'Здравствуйте! Мы – <b>GlassGlow</b>. Первая полировка со скидкой 10%! Выберите действие с помощью кнопок ниже.'

    elif any(word in user_msg for word in ['сколько', 'длится', 'гарантия', 'результат', 'услуги', 'скидки', 'оплата']):
        faq_answers = {
            "сколько": "Полировка занимает примерно 2-3 часа.",
            "гарантия": "Да, мы предоставляем гарантию на все виды работ.",
            "результат": "После полировки стекла становятся прозрачными и блестящими.",
            "услуги": "Мы предоставляем полировку стекол, расчёт стоимости, консультации.",
            "скидки": "Первая полировка со скидкой 10%.",
            "оплата": "Можно оплатить наличными или картой."
        }
        found = False
        for key, answer in faq_answers.items():
            if key in user_msg:
                reply = answer
                found = True
                break
        if not found:
            reply = "Извините, я не знаю ответа на этот вопрос. Попробуйте другой вопрос."

    else:
        reply = 'Извините, я не понял. Используйте кнопки для выбора действия.'

    return jsonify({'reply': reply})


@app.route('/order', methods=['POST'])
def order():
    name = request.form.get('name')
    phone = request.form.get('phone')
    comment = request.form.get('comment')
    with open('orders.txt', 'a', encoding='utf-8') as f:
        f.write(f"{name}, {phone}, {comment}\n")
    return "Заявка успешно отправлена! Мы с вами скоро свяжемся."


if __name__ == '__main__':
    app.run(debug=True)
