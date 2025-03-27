import streamlit as st
import sqlite_utils
from datetime import datetime

# --- DB setup ---
db = sqlite_utils.Database("scheduler.db")
if "bookings" not in db.table_names():
    db["bookings"].create({"datetime": str, "user": str}, pk="id")

st.title("📅 Shared Date‑Time Scheduler")

user = st.text_input("Il tuo nome", value="Anonimo")

st.markdown("---")
chosen = st.date_input("Seleziona data")
time = st.time_input("Seleziona orario")
if st.button("Prenota"):
    dt = datetime.combine(chosen, time).isoformat()
    db["bookings"].insert({"datetime": dt, "user": user})
    st.success("Slot registrato")
    st.rerun()

st.markdown("---")
st.subheader("⏱️ Prenotazioni attuali")

for row in db["bookings"].rows:
    cols = st.columns([4,1])
    cols[0].write(f"{row['datetime']} — **{row['user']}**")

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



