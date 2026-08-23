from app.network.nokia_client import get_reachability_status


phone_number = "+99999991000"

print("Testing Nokia Network-as-Code...")
print(f"Device: {phone_number}")

result = get_reachability_status(phone_number)

print("\nNokia response:")
print(result)

if result.get("reachable"):
    print("\nARES: Responder device is REACHABLE.")
else:
    print("\nARES: Responder device is NOT REACHABLE.")