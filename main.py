from state import load_state
from line import send_message


def main():

    state = load_state()

    send_message(
        "✅ Hay Day News Bot v1 เริ่มทำงานแล้ว"
    )

    print(state)


if __name__ == "__main__":
    main()
