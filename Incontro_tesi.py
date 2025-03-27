import streamlit as st
import sqlite_utils
from datetime import datetime

# --- DB setup ---
db = sqlite_utils.Database("scheduler.db")
if "bookings" not in db.table_names():
    db["bookings"].create({"datetime": str, "user": str}, pk="id")

st.title("🗓️ Disponibilità per incontro")

# Show calendar picker
chosen = st.date_input("Seleziona data")
time = st.time_input("Seleziona orario")
user = st.text_input("Il tuo nome", value="Nome")
if st.button("Conferma"):
    dt = datetime.combine(chosen, time).isoformat()
    db["bookings"].insert({"datetime": dt, "user": user})
    st.success(f"Slot registrato: {dt}")

# Display all bookings
st.subheader("⏱️ Giorni attuali")
for row in db["bookings"].rows:
    st.write(f"{row['datetime']} — {row['user']}")
