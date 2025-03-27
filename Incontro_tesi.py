import streamlit as st
import sqlite_utils
from datetime import datetime

# --- DB setup ---
db = sqlite_utils.Database("scheduler.db")
if "bookings" not in db.table_names():
    db["bookings"].create({"datetime": str, "user": str}, pk="id")

st.title("📅 Shared Date‑Time Scheduler")

# — Input nome all’inizio —
user = st.text_input("Il tuo nome", value="Anonimo")

st.markdown("---")
chosen = st.date_input("Seleziona data")
time = st.time_input("Seleziona orario")
if st.button("Prenota"):
    dt = datetime.combine(chosen, time).isoformat()
    db["bookings"].insert({"datetime": dt, "user": user})
    st.success(f"Slot registrato: {dt}")
    st.experimental_rerun()

st.markdown("---")
st.subheader("⏱️ Prenotazioni attuali")

for row in db["bookings"].rows:
    cols = st.columns([4,1])
    cols[0].write(f"{row['datetime']} — **{row['user']}**")
    # Mostra il pulsante Cancella solo se il booking appartiene all’utente corrente
    if row["user"] == user:
        if cols[1].button("❌ Cancella", key=row["id"]):
            db["bookings"].delete(row["id"])
            st.success("Prenotazione cancellata")
            st.experimental_rerun()

