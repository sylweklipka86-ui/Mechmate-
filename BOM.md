# 📋 Bill of Materials (BOM) – KnightShift

This document lists the components required to build **KnightShift**, a robotic chess player. It includes components to be purchased and equipment already owned.

## 🛒 Components to Purchase (Grant Budget)

| No. | Component | Specification / Model | Qty | Unit Price (USD) | Total (USD) | Unit Price (PLN) | Total (PLN) | Supplier / Product Link | Purpose |
|---:|---|---|---:|---:|---:|---:|---:|---|---|
| 1 | PWM Servo Driver | PCA9685, 16-channel, 12-bit, I2C | 1 | $4.50 | $4.50 | 18.00 zł | 18.00 zł | Add link | Controls servo signals via I2C |
| 2 | High-Torque Servos | MG996R, metal gear, 180° | 2 | $6.00 | $12.00 | 24.00 zł | 48.00 zł | Add link | Base rotation and shoulder joint |
| 3 | Micro Servos | MG90S, metal gear, 180° | 4 | $3.50 | $14.00 | 14.00 zł | 56.00 zł | Add link | Upper arm, wrist and gripper |
| 4 | Power Supply | 6V, 5A DC adapter, 5.5 × 2.1 mm | 1 | $11.00 | $11.00 | 45.00 zł | 45.00 zł | Add link | Dedicated servo power supply |
| 5 | DC Power Jack | 5.5 × 2.1 mm, panel-mount female socket | 1 | $1.00 | $1.00 | 4.00 zł | 4.00 zł | Add link | External power connection |
| 6 | Fuse and Holder | 5 × 20 mm fuse and inline holder | 1 set | $1.50 | $1.50 | 6.00 zł | 6.00 zł | Add link | Power-line protection |
| 7 | Electrolytic Capacitor | 1000 µF, 16 V | 1 | $0.50 | $0.50 | 2.00 zł | 2.00 zł | Add link | Filtering on the servo power rail |
| 8 | Fasteners and Bearings | M3/M4 bolts, locknuts and ball bearings | 1 set | $5.00 | $5.00 | 20.00 zł | 20.00 zł | Add link | Mechanical assembly and joint rotation |

## 🏠 Already Owned Components

These components are already available and are excluded from the grant budget.

| No. | Component | Specification | Qty | Cost to Grant | Purpose |
|---:|---|---|---:|---:|---|
| 9 | Microcontroller | ESP32-S3-DevKitC-1 (USB-C) | 1 | $0.00 | Main controller |
| 10 | Wiring | Power wires and jumper cables | 1 set | $0.00 | Electrical connections |
| 11 | 3D Printing Equipment | 3D printer and PLA/PETG filament | 1 set | $0.00 | Manufacturing mechanical parts |
| 12 | Camera and Chessboard | USB webcam and physical chess set | 1 set | $0.00 | Chessboard monitoring and testing |

## 💰 Total Grant Cost

- **New Parts Total (USD): $49.50**
- **New Parts Total (PLN): 199.00 zł**

*Prices are preliminary estimates and may change depending on the supplier.*

## ⚠️ Technical Notes

- The PCA9685 communicates with the ESP32-S3 through I2C.
- The PCA9685 generates servo control signals; servos require a separate power supply.
- The ESP32-S3 and servo controller must share a common ground with the servo power supply.
- The capacitor is connected across the servo power rail (V+ and GND), with correct polarity.
- The power supply current capacity and fuse rating must be verified against the actual servo specifications before assembly.
- Exact fastener and bearing dimensions will be finalized according to the mechanical design.
