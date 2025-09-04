# Installazione e Verifica Driver Hardware

## Requisiti Hardware
- Lettore tessere USB (Vendor 0x0483, Product 0x2150)
- Relè USB (Vendor 0x16c0, Product 0x05df)
- Porte USB disponibili

## Dipendenze di Sistema
- Ubuntu 22.04 consigliato
- Pacchetti: libpcsclite-dev, pcscd, swig, libtool, libudev-dev, libusb-1.0-0, libusb-1.0-0-dev, python3-pip, pyusb, pyserial

## Procedura Installazione Driver

1. **Installazione pacchetti di sistema**
   ```bash
   sudo apt update
   sudo apt install libpcsclite-dev pcscd swig libtool libudev-dev libusb-1.0-0 libusb-1.0-0-dev python3-pip
   ```

2. **Installazione dipendenze Python**
   ```bash
   python3 -m pip install --upgrade pip
   python3 -m pip install pyusb pyserial
   ```

3. **Regole udev**
   - Verificare presenza file: `/etc/udev/rules.d/99-access-control.rules`
   - Se assente, creare regole per accesso ai dispositivi USB:
     ```
     # Esempio regola per lettore tessere
     SUBSYSTEM=="usb", ATTR{idVendor}=="0483", ATTR{idProduct}=="2150", MODE="0666"
     # Esempio regola per relè USB
     SUBSYSTEM=="usb", ATTR{idVendor}=="16c0", ATTR{idProduct}=="05df", MODE="0666"
     ```
   - Ricaricare regole:
     ```bash
     sudo udevadm control --reload-rules
     sudo udevadm trigger
     ```

4. **Verifica permessi**
   ```bash
   ls -l /dev/bus/usb
   # Deve essere accessibile in lettura/scrittura dall’utente del servizio
   ```

5. **Test hardware**
   ```bash
   cd /opt/access_control/installazione/scripts
   python3 test_hardware.py --verbose
   # Output: ✓ Lettore tessere trovato e configurato correttamente
   #         ✓ Relè USB trovato e configurato correttamente
   ```

6. **Troubleshooting**
   - Se i dispositivi non sono rilevati:
     - Verificare connessione fisica USB
     - Verificare regole udev e permessi
     - Riavviare il servizio systemd: `sudo systemctl restart access-control`
     - Consultare i log: `sudo journalctl -u access-control -f`

## Note
- L’utente di sistema (es. wlkr42) deve essere nei gruppi `dialout` e `plugdev` per accesso hardware.
- Tutte le dipendenze sono installate automaticamente da `install.sh` se si segue la procedura standard.
- Per testare i dispositivi manualmente, usare sempre lo script test_hardware.py.
