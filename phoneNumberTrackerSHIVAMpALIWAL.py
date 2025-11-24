import tkinter as tk
from tkinter import messagebox
import webbrowser
import phonenumbers
from phonenumbers import geocoder, carrier, timezone

def track_phone_number(number):
    try:
        parsed_number = phonenumbers.parse(number)
        tz = timezone.time_zones_for_number(parsed_number)
        loc = geocoder.description_for_number(parsed_number, "en")
        prov = carrier.name_for_number(parsed_number, "en")

        google_maps_url = f"https://www.google.com/maps/search/{loc.replace(' ', '+')}"

        return {
            "number": phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.INTERNATIONAL),
            "timezone": tz,
            "location": loc,
            "carrier": prov,
            "maps_url": google_maps_url
        }
    except Exception as e:
        return {"error": str(e)}

def open_map():
    if 'maps_url' in current_results:
        webbrowser.open(current_results['maps_url'])
    else:
        messagebox.showinfo("Info", "No map URL available to open.")

def on_track():
    global current_results
    phone_number = entry.get()
    if not phone_number.startswith('+'):
        messagebox.showwarning("Input Error", "Please enter the phone number with country code starting with +")
        return
    current_results = track_phone_number(phone_number)
    output_text.delete("1.0", tk.END)
    if "error" in current_results:
        output_text.insert(tk.END, f"Error: {current_results['error']}")
    else:
        output = (
            f"Number: {current_results['number']}\n"
            f"Time Zone(s): {current_results['timezone']}\n"
            f"Location: {current_results['location']}\n"
            f"Carrier: {current_results['carrier']}\n"
            f"Google Maps URL: {current_results['maps_url']}\n\n"
            "Click 'Open Map' to see location on Google Maps."
        )
        output_text.insert(tk.END, output)

# Tkinter UI setup
root = tk.Tk()
root.title("Phone Number Tracker with Google Maps Link")
root.geometry("600x400")

tk.Label(root, text="Enter Phone Number (+CountryCodeNumber):").pack(pady=10)
entry = tk.Entry(root, width=40, font=('Arial', 14))
entry.pack()

track_button = tk.Button(root, text="Track", command=on_track)
track_button.pack(pady=10)

open_map_button = tk.Button(root, text="Open Map", command=open_map)
open_map_button.pack(pady=5)

output_text = tk.Text(root, height=15, width=70)
output_text.pack(pady=10)

current_results = {}

root.mainloop()
