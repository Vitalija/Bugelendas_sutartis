import os
import smtplib
import ssl
from flask import Flask, render_template, request, redirect, flash
from email.message import EmailMessage
from fpdf import FPDF
from dotenv import load_dotenv

load_dotenv()

EMAIL_SIUNTEJAS = os.getenv("EMAIL_USER")
EMAIL_SLAPTAZODIS = os.getenv("EMAIL_PASS")

app = Flask(__name__)
app.secret_key = 'slaptas_raktas_saugumui'

# PDF generavimas be specialių kabučių
def generate_pdf(data, failo_kelias):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    
    pdf.multi_cell(0, 10, f"""STOVYKLOS "BUGELENDAS" SUTARTIS

1. Vaiko vardas: {data.get('vaiko_vardas')}
2. Vaiko pavardė: {data.get('vaiko_pavarde')}
3. Gimimo data: {data.get('gimimo_data')}
4. Vaiko adresas: {data.get('vaiko_adresas')}
5. Vaiko telefonas: {data.get('vaiko_tel')}
6. Tėvų vardas: {data.get('tevu_vardas')}
7. Tėvų telefonas: {data.get('tevu_tel')}
8. Tėvų el. paštas: {data.get('email')}
9. Tėvų adresas: {data.get('tevu_adresas')}
10. Stovyklos pamaina: {data.get('stovyklos_data')}
11. Alergijos ar sveikatos problemos: {data.get('vaiko_alergijos')}

Sąlygos:
Tėvų, vaiko ir stovyklos rengėjo įsipareigojimai.

Stovyklos kontaktai:
Vaikų vasaros stovykla "Bugelendas", Skuodo g. 88, Bugeniai, Mažeikių raj.
Tel. 0-654-01662, el. p. info@bugelendas.lt
Organizatorė: Vitalija Jermolavičienė

Sutinku, kad mano vaikas dalyvaus stovykloje nurodytą datą, įsipareigoju laikytis visų taisyklių.
Sutinku, kad paspaudus mygtuką "SUTINKU", tai prilygsta rašytinei sutarčiai.
Įsipareigoju 100 EUR sumokėti sutarties pasirašymo dieną, o likusius 190 EUR – likus 2 savaitėms iki stovyklos pradžios.

Tėvų parašas: __________________________
""")
    
    pdf.output(failo_kelias)

# El. laiško siuntimas
def send_email_with_attachment(data, failo_kelias):
    recipient = data.get("email", "")
    subject = "Stovyklos Bugelendas sutartis"
    body = "Laba diena,\n\nPateikta vaiko stovyklos sutartis. Priede rasite dokumentą.\n\nVitalija Jermolavičienė"

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = EMAIL_SIUNTEJAS
    msg["To"] = [EMAIL_SIUNTEJAS, recipient]
    msg.set_content(body)

    with open(failo_kelias, "rb") as f:
        msg.add_attachment(f.read(), maintype="application", subtype="pdf", filename=os.path.basename(failo_kelias))

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("tamarina.serveriai.lt", 465, context=context) as server:
        server.login(EMAIL_SIUNTEJAS, EMAIL_SLAPTAZODIS)
        server.send_message(msg)

# Forma
@app.route('/', methods=['GET', 'POST'])
def form():
    if request.method == 'POST':
        data = request.form.to_dict()
        flash("Sutartis pateikta sėkmingai!", "success")
        print("Gauti duomenys:", data)

        vardas = data.get("vaiko_vardas", "vardas")
        pavarde = data.get("vaiko_pavarde", "pavarde")
        failo_pavadinimas = f"{vardas}_{pavarde}.pdf"
        failo_kelias = os.path.join("/tmp", failo_pavadinimas)

        generate_pdf(data, failo_kelias)
        send_email_with_attachment(data, failo_kelias)

        return redirect('/')
    return render_template('form.html')

if __name__ == '__main__':
    app.run()
