# 📋 Bill of Materials (BOM) – KnightShift

Complete list of components required to build **KnightShift**. Items I already own (ESP32-S3, wiring, 3D printer/filament, and camera) are listed for completeness and marked as **$0.00** in the grant budget.

## 🛒 Components to Purchase (Grant Budget)

| Item | Component | Specification / Model | Qty | Unit Price (USD) | Total (USD) | Unit Price (PLN) | Total (PLN) | Notes / Connection |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **1** | **PWM Servo Driver** | `PCA9685` 16-Channel 12-bit I2C Module | 1 | $4.50 | $4.50 | 18.00 zł | 18.00 zł | Connected via I2C (`GPIO8` SDA, `GPIO9` SCL, `3.3V`) |
| **2** | **High-Torque Servos** | `MG996R` (Metal Gear, 180°) | 2 | $6.00 | $12.00 | 24.00 zł | 48.00 zł | Base rotation & shoulder joint (Channels `0–1`) |
| **3** | **Micro Servos** | `MG90S` (Metal Gear, 180°) | 4 | $3.50 | $14.00 | 14.00 zł | 56.00 zł | Upper arm, wrist & gripper (Channels `2–5`) |
| **4** | **Power Supply** | `6V 5A` DC Adapter (30W, `5.5/2.1mm` plug) | 1 | $11.00 | $11.00 | 45.00 zł | 45.00 zł | Dedicated high-current power rail for servos (`V+`) |
| **5** | **DC Power Jack** | `5.5/2.1mm` Panel-Mount Female Socket | 1 | $1.00 | $1.00 | 4.00 zł | 4.00 zł | Mounted in base enclosure (`J1`) |
| **6** | **Fuse & Holder** | `5A` Glass Fuse (`5x20mm`) + Inline Holder | 1 | $1.50 | $1.50 | 6.00 zł | 6.00 zł | Overcurrent protection in series on `V+` (`F1`) |
| **7** | **Decoupling Capacitor** | `1000µF / 16V` Electrolytic Capacitor | 1 | $0.50 | $0.50 | 2.00 zł | 2.00 zł | Across `V+` and `GND` to prevent voltage drops (`C1`) |
| **8** | **Fasteners & Bearings** | `M3 / M4` Bolts, Locknuts & Ball Bearings | 1 set | $5.00 | $5.00 | 20.00 zł | 20.00 zł | Fork-joint assembly and low-friction rotation |

## 🏠 Already Owned Components (Excluded from Grant Cost)

| Item | Component | Specification / Model | Qty | Cost to Grant | Notes |
| :---: | :--- | :--- | :---: | :---: | :--- |
| **9** | **Microcontroller** | `ESP32-S3-DevKitC-1` (USB-C) | 1 | **$0.00** *(Owned)* | Main controller, powered via USB-C |
| **10** | **Wiring & Jumper Cables** | `0.75mm²` Power Wire + DuPont Jumper Wires | 1 set | **$0.00** *(Owned)* | Power rail and I2C/3.3V signal connections |
| **11** | **3D Printing Filament** | `PLA / PETG` 1.75mm spool | 1 | **$0.00** *(Owned)* | Used on personal 3D printer for arm & gripper |
| **12** | **Webcam & Chessboard** | Standard USB Webcam + Physical Chess Set | 1 | **$0.00** *(Owned)* | Used for OpenCV/YOLO board recognition |

---

## 💰 Total Grant Cost

* **New Parts Total (USD):** **`$50.00`**
* **New Parts Total (PLN):** **`201.00 zł`**
