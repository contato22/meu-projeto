class Claw:
    def __init__(self):
        self.is_open = False

    def open(self):
        if self.is_open:
            print("Claw is already open.")
            return
        self.is_open = True
        print("Claw opened.")

    def close(self):
        if not self.is_open:
            print("Claw is already closed.")
            return
        self.is_open = False
        print("Claw closed.")

    def status(self):
        state = "open" if self.is_open else "closed"
        print(f"Claw is {state}.")
        return state


if __name__ == "__main__":
    claw = Claw()
    claw.status()
    claw.open()
    claw.status()
    claw.close()
    claw.status()
