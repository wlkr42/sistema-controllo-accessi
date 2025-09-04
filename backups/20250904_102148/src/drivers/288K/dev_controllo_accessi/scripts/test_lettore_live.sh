#!/bin/bash

echo "🎯 TEST LETTORE CRT-285 LIVE"
echo "============================"
echo ""
echo "📋 ISTRUZIONI:"
echo "1. Inserire una tessera sanitaria nel lettore"
echo "2. Il sistema leggerà automaticamente il codice fiscale"
echo "3. Premere Ctrl+C per fermare"
echo ""
echo "Avvio lettore con sudo..."
echo ""

sudo /opt/access_control/venv/bin/python /opt/access_control/src/hardware/crt285_reader.py