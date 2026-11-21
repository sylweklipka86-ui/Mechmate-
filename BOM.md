# 📋 Bill of Materials (BOM) – KnightShift

This document lists the components required to build **KnightShift**, a robotic chess player. It includes components to be purchased and equipment already owned.

## 🛒 Components to Purchase (Grant Budget)

| No. | Component | Specification / Model | Qty | Unit Price (USD) | Total (USD) | Unit Price (PLN) | Total (PLN) | Supplier / Product Link | Purpose |
|---:|---|---|---:|---:|---:|---:|---:|---|---|
| 1 | PWM Servo Driver | PCA9685, 16-channel, 12-bit, I2C | 1 | $4.50 | $4.50 | 18.00 zł | 18.00 zł |https://allegro.pl/oferta/pca9685-16-kanalowy-sterownik-serw-12-bit-pwm-i2c-13041186606?offerId=13041186606&inventoryUnitId=BcdPag2dPC5Rfqsn_SjPQQ&adGroupId=ODM0YTVkMTQtMjYwMy00MTgxLTkyMGEtZTgyOTM1MTZlODk1AA&campaignId=NTNkYjBmMWMtODQ0My00MzVkLWEwODMtNDg4Y2EyZWEyMTgxAA&clientId=Nzk3NDY1OTYANzA2NzcxNzgA&sig=79827cae954a972cba71276668f686c1&utm_feed=cba59b59-8d0f-48d0-98a0-e9d1127523e2&utm_source=google&utm_medium=ads&gad_source=1&gad_campaignid=23224962948&gclid=CjwKCAiAn4XYBhA-EiwA8176FaxygAxxOXNVLGv_gqEs8CHUIJQ9yv_pv5c1c1f-NCz1M4uCgyWvJhoCjFwQAvD_BwE  | Controls servo signals via I2C |
| 2 | High-Torque Servos | MG996R, metal gear, 180° | 2 | $6.00 | $12.00 | 24.00 zł | 48.00 zł |[ Add link](https://allegro.pl/produkt/msalamon-serwo-mg996r-360-13kg-956fd44d-6965-46b6-a60a-19d21e2e93bf?offerId=17988777370) | Base rotation and shoulder joint |
| 3 | Micro Servos | MG90S, metal gear, 180° | 4 | $3.50 | $14.00 | 14.00 zł | 56.00 zł | [Add link](https://allegro.pl/oferta/serwo-mg90s-towerpro-metalowe-zebatki-orczyki-16620118876?bi_s=ads&bi_m=productlisting:desktop:query&bi_c=MTUxNDUwZmQtMjNiYy00NWM2LTgyN2MtOTk0OGE4MWFmZmJmAA&bi_t=ape&referrer=proxy&emission_unit_id=3d12f2cc-aace-4b7a-9a69-6e21098f41d5) | Upper arm, wrist and gripper |
| 4 | Power Supply | 12V, 3A DC desktop adapter, 5.5 × 2.1 mm | 1 | TBD | TBD | TBD | TBD | Add link | Input power for the servo supply converter |
| 5 | DC-DC Buck Converter | XL4015 adjustable step-down module, set to 6.0 V output | 1 | TBD | TBD | TBD | TBD | Add link | Steps 12V input down to 6V for the servos |
| 6 | DC Power Jack | 5.5 × 2.1 mm, panel-mount female socket | 1 | $1.00 | $1.00 | 4.00 zł | 4.00 zł | Add link | External power connection |
| 7| Fuse and Holder | 5 × 20 mm fuse and inline holder | 1 set | $1.50 | $1.50 | 6.00 zł | 6.00 zł | Add link | Power-line protection |
| 8 | Electrolytic Capacitor | 1000 µF, 16 V | 1 | $0.50 | $0.50 | 2.00 zł | 2.00 zł | Add link | Filtering on the servo power rail |
| 9 | Fasteners and Bearings | M3/M4 bolts, locknuts and ball bearings | 1 set | $5.00 | $5.00 | 20.00 zł | 20.00 zł | Add link | Mechanical assembly and joint rotation |

## 🏠 Already Owned Components

These components are already available and are excluded from the grant budget.

| No. | Component | Specification | Qty | Cost to Grant | Purpose |
|---:|---|---|---:|---:|---|
| 10 | Microcontroller | ESP32-S3-DevKitC-1 (USB-C) | 1 | $0.00 | Main controller |
| 11 | Wiring | Power wires and jumper cables | 1 set | $0.00 | Electrical connections |
| 12 | 3D Printing Equipment | 3D printer and PLA/PETG filament | 1 set | $0.00 | Manufacturing mechanical parts |
| 13 | Camera and Chessboard | USB webcam and physical chess set | 1 set | $0.00 | Chessboard monitoring and testing |

## 💰 Total Grant Cost

New Parts Total (PLN): 207.80 zł
New Parts Total (USD): approximately $52.00

*Prices are preliminary estimates and may change depending on the supplier.*

## ⚠️ Technical Notes

- The PCA9685 communicates with the ESP32-S3 through I2C.
- The PCA9685 generates servo control signals; servos require a separate power supply.
- The ESP32-S3 and servo controller must share a common ground with the servo power supply.
- The capacitor is connected across the servo power rail (V+ and GND), with correct polarity.
- The 12V, 3A adapter supplies the XL4015 converter; the converter output is adjusted to 6.0V for the servo power rail.
- Set and measure the XL4015 output to 6.0V before connecting the PCA9685 and servos.
- Exact fastener and bearing dimensions will be finalized according to the mechanical design.
