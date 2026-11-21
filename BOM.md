# 📋 Bill of Materials (BOM) – KnightShift

Complete list of electronic, power, and mechanical components required to build **KnightShift** (using modular off-the-shelf electronics instead of a custom PCB).

## 🔌 Electronics & Actuators

| Item | Component | Specification / Model | Qty | Unit Price (USD) | Total (USD) | Unit Price (PLN) | Total (PLN) | Notes / Connection |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **1** | **Microcontroller** | `ESP32-S3-DevKitC-1` (USB-C) | 1 | $8.50 | $8.50 | 35.00 zł | 35.00 zł | Main controller, powered separately via USB-C |
| **2** | **PWM Servo Driver** | `PCA9685` 16-Channel 12-bit I2C Module | 1 | $4.50 | $4.50 | 18.00 zł | 18.00 zł | Connected via I2C (`GPIO8` SDA, `GPIO9` SCL, `3.3V`) |
| **3** | **High-Torque Servos** | `MG996R` (Metal Gear, 180°) | 2 | $6.00 | $12.00 | 24.00 zł | 48.00 zł | Base rotation & shoulder joint (Channels `0–1`) |
| **4** | **Micro Servos** | `MG90S` (Metal Gear, 180°) | 4 | $3.50 | $14.00 | 14.00 zł | 56.00 zł | Upper arm, wrist & gripper (Channels `2–5`) |

## ⚡ Power & Circuit Protection

| Item | Component | Specification / Model | Qty | Unit Price (USD) | Total (USD) | Unit Price (PLN) | Total (PLN) | Notes / Connection |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **5** | **Power Supply** | `6V 5A` DC Adapter (30W, `5.5/2.1mm` plug) | 1 | $11.00 | $11.00 | 45.00 zł | 45.00 zł | Dedicated high-current power rail for servos (`V+`) |
| **6** | **DC Power Jack** | `5.5/2.1mm` Panel-Mount Female Socket | 1 | $1.00 | $1.00 | 4.00 zł | 4.00 zł | Mounted in base enclosure (`J1`) |
| **7** | **Fuse & Holder** | `5A` Glass Fuse (`5x20mm`) + Inline Holder | 1 | $1.50 | $1.50 | 6.00 zł | 6.00 zł | Overcurrent protection in series on `V+` (`F1`) |
| **8** | **Decoupling Capacitor** | `1000µF / 16V` Electrolytic Capacitor | 1 | $0.50 | $0.50 | 2.00 zł | 2.00 zł | Across `V+` and `GND` to prevent voltage drops (`C1`) |
| **9** | **Power Wiring** | `0.75mm²` Stranded Copper Wire (Red/Black, 1m) | 1 | $1.50 | $1.50 | 6.00 zł | 6.00 zł | High-current wiring from DC jack to `PCA9685` |
| **10** | **Signal Wiring** | Female-to-Female DuPont Jumper Wires (20cm) | 1 set | $1.50 | $1.50 | 6.00 zł | 6.00 zł | `3.3V`, `GND`, `SDA`, `SCL` connections |

## ⚙️ Mechanics & Hardware

| Item | Component | Specification / Model | Qty | Unit Price (USD) | Total (USD) | Unit Price (PLN) | Total (PLN) | Notes |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **11** | **3D Printing Filament** | `PLA / PETG` 1.75mm (1kg spool) | 1 | $15.00 | $15.00 | 60.00 zł | 60.00 zł | Custom FreeCAD arm, base, and gripper parts |
| **12** | **Fasteners & Bearings** | `M3 / M4` Bolts, Locknuts & Ball Bearings | 1 set | $5.00 | $5.00 | 20.00 zł | 20.00 zł | Fork-joint assembly and low-friction rotation |

---

## 💰 Estimated Total Cost

* **Total (USD):** **`$76.50`**
* **Total (PLN):** **`306.00 zł`**

*(Note: Prices are approximate retail prices in Poland from Botland/Allegro and will be updated with exact store links upon ordering).*
