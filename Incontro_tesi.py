import streamlit as st
import sqlite_utils
from datetime import datetime, date
import calendar
import pandas as pd

# --- DB setup ---
db = sqlite_utils.Database("scheduler.db")
if "bookings" not in db.table_names():
    db["bookings"].create({"datetime": str, "user": str}, pk="id")

st.title("🗓️ Disponibilità incontro tesi/tirocinio")

user = st.text_input("Digitare il proprio nome per creare o modificiare una data", value="Nome")

st.markdown("---")
chosen = st.date_input("Seleziona data")
time = st.time_input("Seleziona orario")
if st.button("Conferma"):
    dt = datetime.combine(chosen, time).isoformat()
    db["bookings"].insert({"datetime": dt, "user": user})
    st.success("Slot registrato")
    st.rerun()

st.markdown("---")
st.subheader("⏱️ Date attuali")

for row in db["bookings"].rows:
    cols = st.columns([4,1])
    dt = datetime.fromisoformat(row["datetime"])
    cols[0].write(dt.strftime("%d/%m/%Y %H:%M") + f" — **{row['user']}**")

    if row["user"] == user:
        if cols[1].button("✏️ Modifica", key=f"edit_{row['id']}"):
            st.session_state.editing = row["id"]

    if st.session_state.get("editing") == row["id"]:
        new_date = st.date_input("Nuova data", value=datetime.fromisoformat(row["datetime"]).date())
        new_time = st.time_input("Nuovo orario", value=datetime.fromisoformat(row["datetime"]).time())
        c1, c2 = st.columns(2)
        if c1.button("💾 Salva", key=f"save_{row['id']}"):
            new_iso = datetime.combine(new_date, new_time).isoformat()
            db["bookings"].update(row["id"], {"datetime": new_iso})
            st.success("Modifica salvata")
            st.session_state.pop("editing")
            st.rerun()
        if c2.button("🗑️ Cancella", key=f"delete_{row['id']}"):
            db["bookings"].delete(row["id"])
            st.success("Prenotazione cancellata")
            st.session_state.pop("editing")
            st.rerun()


st.markdown("---")
st.subheader("🤝🏻 Data/ora condivisa da tutti i partecipanti")

# Raggruppa prenotazioni per datetime
slots = {}
for row in db["bookings"].rows:
    slots.setdefault(row["datetime"], set()).add(row["user"])

# Slot scelti da almeno 2 persone
slots_min2 = sorted((dt for dt, users in slots.items() if len(users) >= 2))
# Slot scelti da almeno 3 persone
slots_min3 = sorted((dt for dt, users in slots.items() if len(users) > 2))

if slots_min2:
    for dt in slots_min2:
        users_list = ", ".join(slots[dt])
        dt_obj = datetime.fromisoformat(dt)
        st.write("✅ " + dt_obj.strftime("%d/%m/%Y %H:%M") + f" — {len(slots[dt])} partecipanti: {users_list}")
else:
    st.info("Nessuna data con 2 partecipanti.")

if slots_min3:
    for dt in slots_min3:
        dt_obj = datetime.fromisoformat(dt)
        st.write("✅ " + dt_obj.strftime("%d/%m/%Y %H:%M") + f" — {len(slots[dt])} partecipanti")
else: 
    st.info("Nessuna data con 3 partecipanti.")

st.markdown("---")
st.subheader("📆 Calendario mensile")

# Raccoglie tutti i mesi/anni con prenotazioni
booked = {datetime.fromisoformat(r["datetime"]).date() for r in db["bookings"].rows}
if booked:
    months = sorted({(d.year, d.month) for d in booked})
    options = [f"{y}-{m:02d}" for y, m in months]
    selected = st.selectbox("Seleziona mese", options)
    year, month = map(int, selected.split("-"))
else:
    year, month = date.today().year, date.today().month

# Costruisce calendario
cal = calendar.monthcalendar(year, month)
df = pd.DataFrame(cal, columns=["Mon","Tue","Wed","Thu","Fri","Sat","Sun"])

# Evidenzia i giorni prenotati
def mark(day):
    if day != 0 and date(year, month, day) in booked:
        return f"🟢 {day}"
    return day if day != 0 else ""

df = df.applymap(mark)
st.table(df)
