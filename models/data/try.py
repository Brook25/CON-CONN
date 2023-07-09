#!/usr/bin/env python3

from pymongo import MongoClient
from models.engine import engine

engine.places_equipments(**{'materials': sorted(['Sand', 'CoarseAggregate', 'Re-bar 8mm', 'Re-bar 12mm', 'Re-bar 14mm', 'Re-bar 16mm', 'Re-bar 20mm', 'Dangote Cement', 'Ethio Cement', 'Stone Masonery'])})
engine.places_equipments(**{'equipments': ["Mixer", "Vibrator", "Compactor", "Excavator", "Bulldozer", "Backhoe", "Grader", "Loader", "Trencher" ]})
#engine.places_equipments(**{'place': {'cities': {'Addis': {'Kolfe': ['Tor-Hailoch', 'Total'], 'Lafto': ['Gabriel', 'Sar-Bet', 'Abo'], 'Arada': ['Piassa', 'Arat-Kilo', 'Amist-Kilo'], 'Lideta': ['Balcha'], 'Addis-Ketmea': ['Merkato', 'Tekle-Haymanot']}, 'Hawassa': {'Hayek-Dare': ['Hayk', 'Zeor-Amist'], 'Menahariya': ['Referal', 'Atote', 'Harar-Sefer'], 'Misrake': ['Wolde-Amanuel', 'Arab-Sefer']} } }})

