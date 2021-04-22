from app import app
from flask import render_template, redirect, url_for, flash, Markup, request, session
from app.modelet import User, db_session, Punonjes, select, delete

from flask_login import current_user, login_user, login_required, logout_user
from datetime import datetime
import calendar





@app.route('/login', methods=['GET', 'POST'])
@db_session
def login():
    if request.method == 'GET':
        if current_user.is_authenticated:
            return redirect(url_for('kryefaqja'))
        else:
            return render_template('login.html', title='Hyr')
    elif request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.get(email=request.form['email'])

        if user is None:
            flash(Markup(
                'Kontrolloni emailin, sepse nuk ka llogari me kete email.'))
            return redirect(url_for('login'))
        elif not user.check_password(password):
            flash('Fjalekalim i gabuar. Provoni perseri.')
            return redirect(url_for('login'))
        else:
            login_user(user)
            return redirect(url_for('kryefaqja'))


@app.route('/dil')
@login_required
def dil():
    logout_user()
    return redirect(url_for('login'))

@app.route('/', methods=['GET', 'POST'])
@db_session
@login_required
def kryefaqja():
    if request.method == 'GET':
        table = select(p for p in Punonjes if int(p.owner) == current_user.id)
        dita = str(current_user.data).split("-")[2][:2]
        return render_template('kryefaqja.html', table=table, dita=dita)

    elif request.method == 'POST':
        data_sot = datetime.strptime(request.form['data'], '%d/%m/%Y')
        current_user.vendos_daten(data_sot)
        dita = str(data_sot).split("-")[2][:2]
        dita = int(dita)
        muaji = str(data_sot).split("-")[1][:2]
        muaji = int(muaji)
        viti =  str(data_sot).split("-")[0][:4]
        viti = int(viti)
        dita_e_fundit_e_muajit = calendar.monthrange(viti, muaji)[1]
        table = select(p for p in Punonjes if int(p.owner) == current_user.id)
        return render_template('kryefaqja.html', table=table, data_sot=current_user.data, dita=dita)

@app.route('/shto_punonjes', methods=['GET', 'POST'])
@db_session
@login_required
def shto_punonjes():
    if request.method == 'GET':
        print(type(str(current_user.data)))
        return render_template('shto_punonjes.html', title='Shto punonjes')

    elif request.method == 'POST':
        data_regjistrimit = current_user.data
        current_user.set_data_te_punonjesve([request.form['emer'], request.form['mbiemer'], request.form['pozicion'],request.form['paga_per_ore'], data_regjistrimit])
        
        punonjes = Punonjes(emer = request.form['emer'],
                            mbiemer = request.form['mbiemer'],
                            pozicion = request.form['pozicion'],
                            paga_per_ore = request.form['paga_per_ore'],
                            data_regjistrimit=data_regjistrimit, owner=current_user.id)

        table = select(p for p in Punonjes if int(p.owner) == current_user.id)
        if punonjes.pozicion =='Mjek':
            for i in table:
                if (i.pozicion == 'Infermiere' and i.paga_per_ore > punonjes.paga_per_ore) or (i.pozicion == 'Sanitare' and i.paga_per_ore > punonjes.paga_per_ore):
                    delete(p for p in Punonjes if int(p.owner) == current_user.id and p.id == punonjes.id)
                    flash(Markup('Ky punonjes nuk mund te shtohet, sepse paga e tij eshte me e ulet se e nje mjeku ose infermieri. Provoni perseri.'))
                    return redirect(url_for('shto_punonjes'))
        elif punonjes.pozicion =='Infermier':
            for i in table:
                if (i.pozicion == 'Mjek' and i.paga_per_ore < punonjes.paga_per_ore) or (i.pozicion == 'Sanitare' and i.paga_per_ore > punonjes.paga_per_ore):
                    delete(p for p in Punonjes if int(p.owner) == current_user.id and p.id == punonjes.id)
                    flash(Markup('Ky punonjes nuk mund te shtohet, sepse paga eshte me e larte se e nje mjeku ose me e ulet se e nje sanitareje. Provoni perseri.'))
                    return redirect(url_for('shto_punonjes'))
        elif punonjes.pozicion =='Sanitare':
            for i in table:
                if (i.pozicion == 'Mjek' and i.paga_per_ore < punonjes.paga_per_ore) or (i.pozicion == 'Infermier' and i.paga_per_ore < punonjes.paga_per_ore):
                    delete(p for p in Punonjes if int(p.owner) == current_user.id and p.id == punonjes.id)
                    flash(Markup('Ky punonjes nuk mund te shtohet, sepse paga eshte me e larte se e nje mjeku/infermieri. Provoni perseri.'))
                    return redirect(url_for('shto_punonjes'))
        
        flash(Markup('Punonjesi u shtua me sukses.'))
        return redirect(url_for('kryefaqja'))

@app.route('/shiko_punonjes/<id>', methods=['GET', 'POST'])
@db_session
@login_required
def shiko_punonjes(id):
    if request.method == 'GET':
        table = select(p for p in Punonjes if int(p.owner) == current_user.id and int(p.id) == id )
        count = table.count()
        dita = str(current_user.data).split("-")[2][:2]
        dita = int(dita)
        muaji = str(current_user.data).split("-")[1][:2]
        muaji = int(muaji)
        viti =  str(current_user.data).split("-")[0][:4]
        viti = int(viti)
        dita_e_fundit_e_muajit = calendar.monthrange(viti, muaji)[1]
        for i in table:
            if int(i.id) == int(id):
                i.vendos_ore_pune(dita*8)
                i.vendos_pagen()

                
        stable = select(p for p in Punonjes if int(p.owner) == current_user.id and int(p.id) == id )

        return render_template('punonjes.html', table=table, id=id, count=count, dita_e_fundit_e_muajit=dita_e_fundit_e_muajit, dita=dita)
            

    elif request.method == 'POST':
        delete (p for p in Punonjes if int(p.owner) == current_user.id and int(p.id) == int(request.form['fshi_punonjes']))
        table = select(p for p in Punonjes if int(p.owner) == current_user.id and int(p.id) == id )
        count = table.count()
        muaji = str(current_user.data).split("-")[1][:2]
        muaji = int(muaji)
        viti =  str(current_user.data).split("-")[0][:4]
        viti = int(viti)
        dita_e_fundit_e_muajit = calendar.monthrange(viti, muaji)[1]
        flash(Markup('Punonjesi u fshi. <br>Shkoni ne <a href="/" id="index_link">faqen kryesore.</a>.'))

        return render_template('punonjes.html', count=count, dita_e_fundit_e_muajit=dita_e_fundit_e_muajit)


