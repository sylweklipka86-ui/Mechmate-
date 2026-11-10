# KnightShift – Bill of Materials (BOM)

This document contains the components required to build the KnightShift robotic chess system.

## 1. Electronics

Component | Quantity | Purpose | Status 
 ESP32-S3 DevKit | 1 | Main controller | Owned 
 PCA9685 | 1 | Servo controller | Planned 
 MG90S servo | TBD | Joint actuation | To be confirmed 
 MG996R servo | TBD | High-torque joint actuation | To be confirmed 
 Camera  1  Chessboard monitoring  To be confirmed 
 DC power supply  1  Power source  To be determined 
|Wires and connectors  TBD  Electrical connections  Planned 

## 2. Mechanical Components

| Component | Quantity | Material | Status |
|---|---:|---|---
 Robot arm links | TBD | PLA | In design 
 Base | 1 | PLA | In design |
 Gripper | 1 | PLA | Planned |
 Screws and nuts | TBD | Metal | To be determined |
 Bearings | TBD | Metal | To be determined |

## 3. Software

| Component | Purpose |
|---|---|
Python | Main programming language 
OpenCV | Image processing |
YOLO | Chess piece detection |
python-chess | Chess game state management |
Stockfish | Chess engine |

## 4. Notes

- Quantities and specifications may change during development.
- Some components are still being evaluated.
- The mechanical design is still under development.
