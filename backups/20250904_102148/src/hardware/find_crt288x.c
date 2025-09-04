#include "crt_288x_ur.h"
#include <stdio.h>
#include <unistd.h>
#include <sys/stat.h>

void check_usb_devices() {
    printf("=== Controllo dispositivi USB ===\n");
    printf("Esegui 'lsusb' per vedere tutti i dispositivi collegati.\n");
    printf("Cerca un dispositivo che NON sia:\n");
    printf("- Linux Foundation (hub)\n");
    printf("- Intel Bluetooth\n");
    printf("- Devantech USB-RLY08\n");
    printf("\nSe vedi un nuovo dispositivo, quello potrebbe essere il CRT288x.\n\n");
}

void check_serial_devices() {
    printf("=== Controllo dispositivi seriali ===\n");
    
    const char* devices[] = {
        "/dev/ttyUSB0", "/dev/ttyUSB1", "/dev/ttyUSB2", "/dev/ttyUSB3",
        "/dev/ttyACM1", "/dev/ttyACM2", "/dev/ttyACM3", // ACM0 è già il Devantech
        "/dev/ttyS0", "/dev/ttyS1"
    };
    
    int found_new = 0;
    
    for (int i = 0; i < sizeof(devices)/sizeof(devices[0]); i++) {
        struct stat st;
        if (stat(devices[i], &st) == 0) {
            printf("✓ Trovato: %s\n", devices[i]);
            found_new++;
        }
    }
    
    if (found_new == 0) {
        printf("- Nessun nuovo dispositivo seriale trovato\n");
        printf("- /dev/ttyACM0 è il Devantech (già identificato)\n");
    }
    
    printf("\n");
}

int test_crt288x_connection() {
    printf("=== Test connessione CRT288x ===\n");
    
    // Test connessione USB
    printf("1. Test modalità USB...\n");
    int result = CRT288x_OpenConnection(CRT_OPEN_TYPEUSB, 0, 0);
    if (result == 0) {
        printf("✓ SUCCESSO! CRT288x trovato in modalità USB!\n");
        
        // Test funzionalità base
        int card_status = CRT288x_GetCardStatus();
        printf("Status carta: %d\n", card_status);
        
        int lock_status = CRT288x_GetLockStatus();
        printf("Status lock: %d\n", lock_status);
        
        // Test LED per confermare che funziona
        printf("Test LED (rosso per 2 secondi)...\n");
        CRT288x_LEDProcess(CRT_LED_RED, CRT_LED_ON);
        sleep(2);
        CRT288x_LEDProcess(CRT_LED_RED, CRT_LED_OFF);
        
        CRT288x_CloseConnection();
        return 0;
    } else {
        printf("✗ Connessione USB fallita: errore %d\n", result);
    }
    
    // Test connessioni seriali
    printf("\n2. Test modalità seriale (RS232)...\n");
    for (int com = 0; com <= 10; com++) {
        printf("   Provo COM%d...\n", com);
        result = CRT288x_OpenConnection(CRT_OPEN_TYPERS232, com, 9600);
        if (result == 0) {
            printf("✓ SUCCESSO! CRT288x trovato su COM%d!\n", com);
            
            int card_status = CRT288x_GetCardStatus();
            printf("Status carta: %d\n", card_status);
            
            CRT288x_CloseConnection();
            return 0;
        }
    }
    
    printf("✗ Nessuna connessione riuscita\n");
    return -1;
}

void show_error_codes() {
    printf("=== Codici errore comuni CRT288x ===\n");
    printf("-201: Errore carattere comando\n");
    printf("-202: Errore parametri comando\n");
    printf("-203: Comando non può essere eseguito\n");
    printf("-204: Hardware non supporta\n");
    printf("-205: Errore dati comando\n");
    printf("-280: Timeout comunicazione\n");
    printf("-284: Comando cancellato\n");
    printf("-299: Errore sconosciuto\n");
    printf("\n");
}

int main() {
    printf("=== Ricerca lettore CRT288x ===\n\n");
    
    check_usb_devices();
    check_serial_devices();
    
    // Verifica se la libreria è installata
    printf("=== Verifica libreria CRT288x ===\n");
    struct stat st;
    if (stat("/usr/local/lib/crt_288x_ur.so", &st) == 0) {
        printf("✓ Libreria trovata in /usr/local/lib/\n");
    } else {
        printf("✗ Libreria non trovata!\n");
        printf("Esegui: sudo cp crt_288x_ur.so /usr/local/lib/\n");
        printf("        sudo ldconfig\n");
        return -1;
    }
    
    if (stat("/usr/local/include/crt_288x_ur.h", &st) == 0) {
        printf("✓ Header trovato in /usr/local/include/\n");
    } else {
        printf("- Header non trovato (opzionale)\n");
    }
    
    printf("\n");
    
    int success = test_crt288x_connection();
    
    if (success != 0) {
        show_error_codes();
        printf("=== Cosa fare ===\n");
        printf("1. Assicurati che il lettore CRT288x sia collegato via USB\n");
        printf("2. Controlla che appaia in 'lsusb' come nuovo dispositivo\n");
        printf("3. Verifica che il dispositivo sia alimentato (LED acceso?)\n");
        printf("4. Prova un cavo USB diverso\n");
        printf("5. Controlla i permessi: groups | grep dialout\n");
    }
    
    return success;
}

