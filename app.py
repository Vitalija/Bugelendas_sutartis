import os
import smtplib
import ssl
from flask import Flask, render_template, request, redirect, flash
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

EMAIL_SIUNTEJAS = os.getenv("EMAIL_USER")
EMAIL_SLAPTAZODIS = os.getenv("EMAIL_PASS")

app = Flask(__name__)
app.secret_key = 'slaptas_raktas_saugumui'

def send_email_with_attachment(data, filepath):
    recipient = data.get("email", "")
    subject = "Stovyklos Bugelendas sutartis"
    body = "Laba diena,\n\nPateikta vaiko stovyklos sutartis. Priede rasite dokumentą.\n\nVitalija Jermolavičienė"

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = EMAIL_SIUNTEJAS
    msg["To"] = [EMAIL_SIUNTEJAS, recipient]
    msg.set_content(body)

    with open(filepath, "rb") as f:
        file_data = f.read()
        msg.add_attachment(file_data, maintype="application", subtype="octet-stream", filename=os.path.basename(filepath))

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
        failo_pavadinimas = f"{vardas}_{pavarde}.txt"
        failo_kelias = os.path.join("sutartys", failo_pavadinimas)

        os.makedirs("sutartys", exist_ok=True)
        sutarties_tekstas = f"""STOVYKLOS „BUGELENDAS“ SUTARTIS

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
Vaikų vasaros stovykla „Bugelendas“, Skuodo g. 88, Bugeniai, Mažeikių raj.
Tel. 0-654-01662, el. p. info@bugelendas.lt
Organizatorė: Vitalija Jermolavičienė

Sutinku, kad mano vaikas dalyvaus stovykloje nurodytą datą, įsipareigojame laikytis visų taisyklių.
Taip pat sutinku, kad paspaudus mygtuką „SUTINKU“ tai būtų laikoma rašytine sutartimi.
Įsipareigoju 100 € sumokėti sutarties pasirašymo dieną, o likusius 190 € – likus 2 savaitėms iki stovyklos pradžios.

Tėvų parašas: ______________________
"""

        with open(failo_kelias, "w", encoding="utf-8") as f:
            f.write(sutarties_tekstas)

        send_email_with_attachment(data, failo_kelias)
        return redirect('/')
    return render_template('form.html')

if __name__ == "__main__":
    app.run()
