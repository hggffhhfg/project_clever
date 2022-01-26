from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import csv

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sleepdairy.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Notation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    leg = db.Column(db.Time, nullable=False)
    usnul = db.Column(db.Time, nullable=False)
    prosnul = db.Column(db.Time, nullable=False)
    vstal = db.Column(db.Time, nullable=False)
    nespal = db.Column(db.INT, nullable=False)
    spal = db.Column(db.INT, nullable=False)
    vkrovati = db.Column(db.INT, nullable=False)

    def __repr__(self):
        return '<Notation %r>' % self.id


def str_to_time(s):
    return datetime.time(datetime.strptime(s, '%H:%M'))


def str_to_ymd(s):
    return datetime.date(datetime.strptime(s, '%Y-%m-%d'))


def timedelta_to_minutes(s):
    return s.seconds / 60


@app.route('/sleep')
def basesleep():
    def h_m(vremya):
        if type(vremya) == int:
            if vremya % 60 < 10:
                hm = str(vremya // 60) + ':0' + str(vremya % 60)
            else:
                hm = str(vremya // 60) + ':' + str(vremya % 60)
        else:
            hm = vremya.strftime('%H:%M')
        return hm

    def eff(spal, vkrovati):
        if spal == 0:
            return 0
        else:
            return round((spal / vkrovati * 100), 2)

    def eff_sleep_of_week(nedelya):
        sum_eff = 0
        elem_of_week = 0
        for day in range(1 + 7 * (nedelya - 1), 8 * nedelya - (nedelya - 1)):
            for elem in notations:
                if elem.id == day:
                    elem_of_week += 1
                    if elem.spal != elem.nespal:
                        sum_eff += (elem.spal - elem.nespal) / elem.vkrovati
        if elem_of_week == 0:
            return 0
        else:
            eff_count = (sum_eff / elem_of_week) * 100
            eff_count = round(eff_count, 2)
            return eff_count

    def avg_duration_sleep_of_week(nedelya):
        sum_min = 0
        elem_of_week = 0
        for day in range(1 + 7 * (nedelya - 1), 8 * nedelya - (nedelya - 1)):
            for elem in notations:
                if elem.id == day:
                    elem_of_week += 1
                    sum_min += elem.spal - elem.nespal
        if elem_of_week == 0:
            return 0
        else:
            avg = sum_min / elem_of_week
            return int(avg)

    def check_notations(nedelya):
        amount = 0
        for day in range(1 + 7 * (nedelya - 1), 8 * nedelya - (nedelya - 1)):
            for elem in notations:
                if elem.id == day:
                    amount += 1
        if amount == 0:
            return 0
        else:
            return amount

    def last_day(day_number):
        day = 0
        for elem in notations:
            day += 1
        if day_number == day:
            return True
        else:
            return False

    def dmy_today():
        return datetime.date(datetime.today())

    notations = db.session.query(Notation).order_by(Notation.id)
    db_elem_counter = db.session.query(Notation).count()

    return render_template("sleep.html", notations=notations, h_m=h_m, eff=eff, db_elem_counter=db_elem_counter,
                           eff_sleep_of_week=eff_sleep_of_week, avg_duration_sleep_of_week=avg_duration_sleep_of_week,
                           check_notations=check_notations, last_day=last_day, dmy_today=dmy_today)


@app.route('/sleep/<int:id>/delete')
def delete_notation(id):
    notations = Notation.query.get_or_404(id)

    try:
        db.session.delete(notations)
        db.session.commit()
        return redirect('/sleep')
    except:
        return "При удалении записи произошла ошибка"


@app.route('/sleep/<int:id>/update', methods=['POST', 'GET'])
def update(id):
    notations = Notation.query.get(id)
    if request.method == "POST":
        notations.date = str_to_ymd(request.form['date'])
        notations.leg = str_to_time(request.form['leg'])
        notations.usnul = str_to_time(request.form['usnul'])
        notations.prosnul = str_to_time(request.form['prosnul'])
        notations.vstal = str_to_time(request.form['vstal'])
        notations.nespal = str_to_time(request.form['nespal']).hour * 60 + str_to_time(request.form['nespal']).minute
        delta_spal = datetime.combine(notations.date, notations.prosnul) - datetime.combine(notations.date, notations.usnul)
        delta_vkrovati = datetime.combine(notations.date, notations.vstal) - datetime.combine(notations.date, notations.leg)
        notations.spal = timedelta_to_minutes(delta_spal) - notations.nespal
        notations.vkrovati = timedelta_to_minutes(delta_vkrovati)

        try:
            db.session.commit()
            return redirect('/sleep')
        except:
            return "При редактировании статьи статьи произошла ошибка"
    else:
        return render_template("notation_update.html", notations=notations)


@app.route('/sleep', methods=['POST', 'GET'])
def add_notation():
    if request.method == "POST":
        date = str_to_ymd(request.form['date'])
        leg = str_to_time(request.form['leg'])
        usnul = str_to_time(request.form['usnul'])
        prosnul = str_to_time(request.form['prosnul'])
        vstal = str_to_time(request.form['vstal'])
        nespal = str_to_time(request.form['nespal']).hour * 60 + str_to_time(request.form['nespal']).minute
        delta_spal = datetime.combine(date, prosnul) - datetime.combine(date, usnul)
        delta_vkrovati = datetime.combine(date, vstal) - datetime.combine(date, leg)
        spal = timedelta_to_minutes(delta_spal) - nespal
        vkrovati = timedelta_to_minutes(delta_vkrovati)

        notation = Notation(date=date, spal=spal, vkrovati=vkrovati, leg=leg, usnul=usnul,
                            prosnul=prosnul, vstal=vstal, nespal=nespal)
        try:
            db.session.add(notation)
            db.session.commit()
            return redirect('/')
        except:
            return "При добавлении статьи произошла ошибка"
    else:
        return render_template('sleep.html')


@app.route('/edit', methods=['POST', 'GET'])
def edit_dairy():
    notations = db.session.query(Notation).order_by(Notation.id)
    if request.method == 'POST':
        if request.form['export'] == 'Экспортировать дневник':
            try:
                with open("export_dairy.csv", "w") as file:
                    writer = csv.writer(file)
                    writer.writerow(
                        ('Дата', 'Лег', 'Уснул', 'Проснулся', 'Встал', 'Не спал', 'Время сна', 'Время в кровати',
                         'Эффективность сна')
                    )
                    for elem in notations:
                        writer.writerow(
                            [elem.date, elem.leg, elem.usnul, elem.prosnul, elem.vstal, elem.nespal, elem.spal,
                             elem.vkrovati]
                        )
                return "Экспортировано успешно"
            except:
                return "При эспортировании произошла ошибка"
    else:
        return render_template("edit_dairy.html")


@app.route('/')
@app.route('/main')
def main():
    return render_template("main.html")


@app.route('/login')
def login():
    return render_template("login.html")


@app.route('/data_form')
def data():
    return render_template("data-form.html")


@app.route('/analytics')
def analytics():
    return render_template('analytics.html')


@app.route('/support')
def support():
    return render_template('support.html')


if __name__ == "__main__":
    app.run(debug=True)
