import os
import smtplib
import ssl
from flask import Flask, render_template, request, redirect, flash
from email.message import EmailMessage
from dotenv import load_dotenv
from fpdf import FPDF

load_dotenv()

EMAIL_SIUNTEJAS = os.getenv("EMAIL_USER")
EMAIL_SLAPTAZODIS = os.getenv("EMAIL_PASS")

app = Flask(__name__)
app.secret_key = 'slaptas_raktas_saugumui'

def generate_pdf(data, failo_kelias):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    lines = [
        "STOVYKLOS „BUGELENDAS“ SUTARTIS",
        "",
        f"1. Vaiko vardas: {data.get('vaiko_vardas')}",
        f"2. Vaiko pavardė: {data.get('vaiko_pavarde')}",
        f"3. Gimimo data: {data.get('gimimo_data')}",
        f"4. Vaiko adresas: {data.get('vaiko_adresas')}",
        f"5. Vaiko telefonas: {data.get('vaiko_tel')}",
        f"6. Tėvų vardas: {data.get('tevu_vardas')}",
        f"7. Tėvų telefonas: {data.get('tevu_tel')}",
        f"8. Tėvų el. paštas: {data.get('email')}",
        f"9. Tėvų adresas: {data.get('tevu_adresas')}",
        f"10. Stovyklos pamaina: {data.get('stovyklos_data')}",
        f"11. Alergijos ar sveikatos problemos: {data.get('vaiko_alergijos')}",
        "",
        "Sąlygos:",
        "Vaikas dalyvauja stovykloje nuo pirmadienio iki penktadienio.",
        "Kaina 290 EUR, sumokama pavedimu per 3 d. d.",
        "Tėvai įsipareigoja atvežti ir pasiimti vaiką laiku.",
        "Stovykloje vaikas laikysis vidaus tvarkos taisyklių.",
        "",
        "Tėvų, vaiko ir stovyklos rengėjo įsipareigojimai.",
        "",
        "Stovyklos kontaktai:",
        "Vaikų vasaros stovykla „Bugelendas“, Skuodo g. 88, Bugeniai, Mažeikių raj.",
        "Tel. 0-654-01662, el. p. info@bugelendas.lt",
        "Organizatorė: Vitalija Jermolavičienė",
        "",
        "Sutinku, kad mano vaikas dalyvaus stovykloje nurodytą datą, įsipareigojame laikytis visų taisyklių.",
        "Taip pat sutinku, kad paspaudus mygtuką „SUTINKU“ tai būtų laikoma rašytine sutartimi.",
        "Įsipareigoju 100 € sumokėti sutarties pasirašymo dieną, o likusius 190 € – likus 2 savaitėms iki stovyklos pradžios.",
        "",
        "Tėvų parašas: ______________________",
    ]

    for line in lines:
        pdf.cell(200, 10, txt=line, ln=True)

    pdf.output(failo_kelias)

def send_email_with_attachment(data, failo_kelias):
    recipient = data.get("email", "")
    subject = "Stovyklos Bugelendas sutartis"
    body = "Laba diena,\n\nPateikta vaiko stovyklos sutartis. Priede rasite PDF dokumentą.\n\nVitalija Jermolavičienė"

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = EMAIL_SIUNTEJAS
    msg["To"] = [EMAIL_SIUNTEJAS, recipient]
    msg.set_content(body)

    with open(failo_kelias, "rb") as f:
        file_data = f.read()
        msg.add_attachment(file_data, maintype="application", subtype="pdf", filename=os.path.basename(failo_kelias))

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("tamarina.serveriai.lt", 465, context=context) as server:
        server.login(EMAIL_SIUNTEJAS, EMAIL_SLAPTAZODIS)
        server.send_message(msg)

@app.route('/', methods=['GET', 'POST'])
def form():
    if request.method == 'POST':
        data = request.form.to_dict()
        flash("Sutartis pateikta sėkmingai!", "success")

        vardas = data.get("vaiko_vardas", "vardas")
        pavarde = data.get("vaiko_pavarde", "pavarde")
        failo_pavadinimas = f"{vardas}_{pavarde}.pdf"
        failo_kelias = os.path.join("/tmp", failo_pavadinimas)

        generate_pdf(data, failo_kelias)
        send_email_with_attachment(data, failo_kelias)

        return redirect('/')
    return render_template('form.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

