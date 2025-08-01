# GameKeep# Game-Keep README

Pre-requisites and installation steps for running the `gamekeep.py` script on your Batocera Raspberry Pi.

---

## 1. Network & SSH Access

* Ensure your mini-pc is on the same LAN as your PC.
* Verify you can SSH in as root:

  ```bash
  ssh root@<PI_IP>
  ```

  Replace `<PI_IP>` with your Pi’s IP address (e.g., `192.167.9.70`).

---

## 2. Directory Setup on the Pi

SSH into the mini-PC and create the necessary folders:

```bash
ssh root@<PI_IP>

# Create the script directory
d mkdir -p /userdata/game-keep
```

---

## 3. Copying the Files

On your development PC, assuming your local project lives in `~/projects/game-keep/` (change the path to the path of your script):

```bash
# Copy the main script\scp ~/projects/game-keep/gamekeep.py root@<PI_IP>:/userdata/game-keep/gamekeep.py

# Copy the custom launch script\scp ~/projects/game-keep/custom.sh root@<PI_IP>:/userdata/system/custom.sh
```

Back on the mini-pc, set execute permissions:

```bash
ssh root@<PI_IP>
chmod +x /userdata/game-keep/gamekeep.py
chmod +x /userdata/system/custom.sh
```

---

## 4. Python & Virtualenv

1. **Create a virtual environment** inside `/userdata/game-keep`:

   ```bash
   cd /userdata/game-keep
   python3 -m venv venv
   ```
2. **How to activate/ deactivate the python virtual env**:

   ```bash
   source venv/bin/activate
   deactivate
   ```

   * **Flask** is required only if your script uses the built-in control page.
---
