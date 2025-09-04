import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, time
import sqlite3
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.api.modules.configurazione_accessi import verifica_orario, verifica_limite_mensile
from src.database.database_manager import DatabaseManager

class TestConfigurazioneAccessi(unittest.TestCase):
    def setUp(self):
        """Setup per ogni test"""
        self.db_path = ':memory:'  # Usa database in memoria per i test
        self.db = DatabaseManager(self.db_path)
        
    def tearDown(self):
        """Cleanup dopo ogni test"""
        self.db.close()

    @patch('src.api.modules.configurazione_accessi.get_db_connection')
    def test_verifica_orario_dentro_orario(self, mock_get_db):
        """Test verifica orario quando siamo in orario consentito"""
        # Mock della connessione
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Mock risultato query per orari
        mock_cursor.fetchone.return_value = (
            'Lunedi',  # giorno
            True,      # aperto
            '09:00',   # mattina_inizio
            '12:00',   # mattina_fine
            '14:00',   # pomeriggio_inizio
            '18:00'    # pomeriggio_fine
        )
        
        # Test con orario mattina valido
        with patch('datetime.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2025, 7, 19, 10, 30)  # 10:30
            self.assertTrue(verifica_orario())
        
        # Test con orario pomeriggio valido
        with patch('datetime.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2025, 7, 19, 15, 30)  # 15:30
            self.assertTrue(verifica_orario())

    @patch('src.api.modules.configurazione_accessi.get_db_connection')
    def test_verifica_orario_fuori_orario(self, mock_get_db):
        """Test verifica orario quando siamo fuori orario"""
        # Mock della connessione
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Mock risultato query per orari
        mock_cursor.fetchone.return_value = (
            'Lunedi',  # giorno
            True,      # aperto
            '09:00',   # mattina_inizio
            '12:00',   # mattina_fine
            '14:00',   # pomeriggio_inizio
            '18:00'    # pomeriggio_fine
        )
        
        # Test con orario mattina non valido
        with patch('datetime.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2025, 7, 19, 8, 30)  # 8:30
            self.assertFalse(verifica_orario())
        
        # Test con orario pausa pranzo
        with patch('datetime.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2025, 7, 19, 13, 0)  # 13:00
            self.assertFalse(verifica_orario())
        
        # Test con orario sera
        with patch('datetime.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2025, 7, 19, 19, 0)  # 19:00
            self.assertFalse(verifica_orario())

    @patch('src.api.modules.configurazione_accessi.get_db_connection')
    def test_verifica_limite_mensile(self, mock_get_db):
        """Test verifica limite mensile accessi"""
        # Mock della connessione
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Mock limite configurato (3 accessi)
        mock_cursor.fetchone.side_effect = [(3,), (2,)]  # Prima chiamata per limite, seconda per conteggio
        
        # Test con accessi sotto il limite
        self.assertTrue(verifica_limite_mensile('RSSMRA80A01H501Z'))
        
        # Test con limite raggiunto
        mock_cursor.fetchone.side_effect = [(3,), (3,)]
        self.assertFalse(verifica_limite_mensile('RSSMRA80A01H501Z'))
        
        # Test con limite superato
        mock_cursor.fetchone.side_effect = [(3,), (4,)]
        self.assertFalse(verifica_limite_mensile('RSSMRA80A01H501Z'))

    def test_integrazione_verifiche(self):
        """Test integrazione delle verifiche nel DatabaseManager"""
        test_cf = 'RSSMRA80A01H501Z'
        
        # Mock delle funzioni di verifica
        with patch('src.api.modules.configurazione_accessi.verifica_orario') as mock_orario, \
             patch('src.api.modules.configurazione_accessi.verifica_limite_mensile') as mock_limite:
            
            # Test con tutte le verifiche ok
            mock_orario.return_value = True
            mock_limite.return_value = True
            
            success, _ = self.db.verify_access(test_cf)
            self.assertTrue(success)
            
            # Test con orario non valido
            mock_orario.return_value = False
            mock_limite.return_value = True
            
            success, _ = self.db.verify_access(test_cf)
            self.assertFalse(success)
            
            # Test con limite superato
            mock_orario.return_value = True
            mock_limite.return_value = False
            
            success, _ = self.db.verify_access(test_cf)
            self.assertFalse(success)

if __name__ == '__main__':
    unittest.main()
