import heapq
import time
import threading
import streamlit as st

# Priority queue to handle ICU alerts based on severity
icu_alert_queue = []
queue_lock = threading.Lock()
new_alert_event = threading.Event()  # Event to notify when a new alert is added

# Function to add an alert to the queue based on priority
def add_alert(patient_id, severity_level):
    with queue_lock:
        heapq.heappush(icu_alert_queue, (severity_level, patient_id))
        new_alert_event.set()  # Notify that a new alert has been added

# Function to handle alerts (process the most critical one first)
def handle_alerts():
    while True:
        new_alert_event.wait()  # Wait until a new alert is added
        with queue_lock:
            if icu_alert_queue:
                severity, patient_id = heapq.heappop(icu_alert_queue)
                st.session_state.alert_messages.append(f"🚨 [CRITICAL] Processing alert for patient {patient_id} with severity {severity}.")
                time.sleep(2)  # Simulate time taken to handle an alert
                st.session_state.alert_messages.append(f"✅ Finished processing alert for patient {patient_id}.")
            if not icu_alert_queue:
                new_alert_event.clear()  # Reset the event if no more alerts remain

# Function to display the current queue of alerts
def display_alert_queue():
    while True:
        time.sleep(5)  # Display every 5 seconds
        with queue_lock:
            if icu_alert_queue:
                alert_status = "### Current Alerts in Queue\n"
                for severity, patient_id in sorted(icu_alert_queue):
                    alert_status += f"Patient {patient_id} with severity {severity}\n"
                st.session_state.queue_display.text(alert_status)
            else:
                if not new_alert_event.is_set():  # Only print if no new alert is being added
                    st.session_state.queue_display.text("✅ No pending alerts.")

# Streamlit app setup
st.title("ICU Real-Time Alert Monitoring System")
st.write("""
This system monitors and processes ICU patient alerts based on their severity levels:
- **1 (Critical)**: Immediate action required
- **2 (Moderate)**: Important but not life-threatening
- **3 (Non-Critical)**: Routine monitoring
""")

# Initialize session state for alert messages and queue display
if 'alert_messages' not in st.session_state:
    st.session_state.alert_messages = []
if 'queue_display' not in st.session_state:
    st.session_state.queue_display = st.empty()

# Streamlit input form for adding alerts
with st.form("add_alert_form"):
    st.subheader("Add a New Patient Alert")
    patient_id = st.text_input("Enter patient ID (e.g., 101, 102)")
    severity_level = st.selectbox("Enter severity level", [1, 2, 3], format_func=lambda x: {1: "Critical", 2: "Moderate", 3: "Non-Critical"}[x])
    submit = st.form_submit_button("Add Alert")
    
    # Adding the alert to the queue
    if submit:
        if patient_id:
            add_alert(patient_id, severity_level)
            st.session_state.alert_messages.append(f"✅ Alert added! Patient {patient_id} with severity {severity_level} has been added to the queue.")
        else:
            st.error("❌ Please enter a valid Patient ID.")

# Display alert messages in real-time
for message in st.session_state.alert_messages:
    st.write(message)

# Start alert handler thread (for processing alerts)
handler_thread = threading.Thread(target=handle_alerts, daemon=True)
handler_thread.start()

# Start thread to display the alert queue
display_thread = threading.Thread(target=display_alert_queue, daemon=True)
display_thread.start()

# Streamlit's main loop to keep the app running
while True:
    time.sleep(1)  # Prevent the app from crashing
