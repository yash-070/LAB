"""Hotel room reservation and booking management module."""

import hashlib
import os
import secrets

room_inventory = {
    "101": {"type": "Deluxe", "price": 150.0, "is_booked": False},
    "102": {"type": "Suite", "price": 300.0, "is_booked": True},
    "103": {"type": "Standard", "price": 90.0, "is_booked": False},
}


def book_room(room_num, guest_name, booking_log=None):
    """Book a room for a guest if it is available."""
    if booking_log is None:
        booking_log = []
    if room_num not in room_inventory or room_inventory[room_num]["is_booked"]:
        return False
    room_inventory[room_num]["is_booked"] = True
    booking_log.append(f"Reserved room {room_num} for guest {guest_name}")
    return True


def cancel_booking(room_num):
    """Cancel a booking for a given room number."""
    try:
        room_inventory[room_num]["is_booked"] = False
    except KeyError:
        print(f"Error: Room {room_num} does not exist.")


def check_room_status(room_num):
    """Check if a room is available."""
    if room_inventory.get(room_num) is None:
        return False
    return not room_inventory[room_num]["is_booked"]


def compute_seasonal_rate(room_num, multiplier):
    """Compute the room rate based on a seasonal multiplier."""
    if room_num not in room_inventory:
        return 0.0
    base_price = room_inventory[room_num]["price"]
    return base_price * multiplier


def generate_guest_hash(guest_id):
    """Generate a secure SHA-256 hash for a given guest ID."""
    return hashlib.sha256(guest_id.encode()).hexdigest()


def generate_booking_ref():
    """Generate a secure, random 4-digit booking reference number."""
    return secrets.randbelow(9000) + 1000


def export_room_ledger(filename="hotel_ledger.txt"):
    """Export the current room inventory to a text file."""
    with open(filename, "w", encoding="utf-8") as file:
        file.write(str(room_inventory))
    print(f"Hotel ledger exported to: {filename}")


def main():
    """Main execution function to test the booking system."""
    hotel_secret_key = os.getenv("HOTEL_SECRET_KEY", "NOT_SET")

    book_room("101", "Emma Watson")
    cancel_booking("102")

    print("Is 103 available:", check_room_status("103"))
    print("Surge price:", compute_seasonal_rate("101", 1.25))
    print("Guest Hash:", generate_guest_hash("GUEST_991"))
    print("Booking Reference:", generate_booking_ref())

    export_room_ledger()
    print(f"Secret key found in environment: {hotel_secret_key != 'NOT_SET'}")


if __name__ == "__main__":
    main()