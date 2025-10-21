---
title: "E1a – Poljot 3133 Chronograph: Exploded Diagram and Functional Map"
watch_used: "Poljot 3133 / Valjoux 7734-derived"
difficulty: "Reference"
tags:
  - chronograph
  - exploded_diagram
  - mechanism
---

# E1a – Poljot 3133 Chronograph: Exploded Diagram and Functional Map

> *This document functions as a textual “service drawing.”  
> Each component group is described as if viewed dial-down, movement-up, crown to the right.*

---

## 🔩 1 – Bridge Layer Overview

| Bridge | Function | Underneath |
|---------|-----------|------------|
| **Chronograph Bridge** | Holds clutch, coupling wheel, intermediate wheel, brake lever. | Train bridge + chrono wheels. |
| **Minute-Recording Bridge** | Supports minute-recording wheel and hammer post. | Heart cam on minute wheel. |
| **Coupling Clutch Bridge** | Guides coupling yoke travel. | 4th wheel and chrono driving wheel. |
| **Train Bridge** | Standard gear-train pivots. | Barrel + 3rd, 4th, escape wheels. |
| **Barrel Bridge** | Barrel arbor, click (hidden). | Mainspring barrel. |

When the chrono bridge is lifted, the click and barrel ratchet are exposed—this is why the movement must be partly dismantled to let down power safely.

---

## ⚙️ 2 – Base Train (Timekeeping Path)

`Barrel → Center → 3rd → 4th → Escape → Pallet → Balance`

- The **4th wheel** carries the **driving finger** for the chronograph clutch.  
- When the clutch engages, the chrono wheel’s teeth mesh with the 4th wheel’s driving wheel.

---

## 🧩 3 – Operating System (Start / Stop / Reset)

### A. Pushers and Levers
- **Start/Stop Pusher (2 o’clock)** actuates the **operating lever**.
- **Reset Pusher (4 o’clock)** drives the **hammer** directly.

### B. Operating Cam (Heart-Shaped Cam)
- Central hub with two notches: *high* and *low* positions correspond to *start* and *stop*.
- Connected to the operating lever by a stud; one rotation of ~60 ° toggles the state.

### C. Operating Lever Spring
- Flat steel spring anchored to main plate; maintains positive toggle pressure on the cam.

**Sequence:**
1. Pusher pressed → lever pivots → cam rotates to “run” → clutch engaged.  
2. Pusher pressed again → cam returns → clutch disengaged, brake applied.  
3. Reset pusher → hammer falls on heart cams → hands return to zero.

---

## 🧮 4 – Coupling & Chronograph Train

### Components
| Part | Description | Key Detail |
|------|--------------|------------|
| **Coupling Yoke** | Long steel fork sliding laterally; carries clutch wheel. | Spring-loaded against operating cam. |
| **Clutch Wheel (Driving Wheel)** | Small double gear connecting 4th wheel and chrono wheel. | Engages/disengages by yoke motion. |
| **Chrono Center Wheel** | Carries central chronograph seconds hand. | Pivoted in chrono bridge + main plate. |
| **Intermediate Chrono Wheel** | Transmits motion to minute recorder. | Runs between chrono center & minute wheel. |
| **Minute Recording Wheel** | 30-minute counter. | Advanced by finger on chrono center wheel once per revolution. |

### Engagement Geometry
- At *start*: operating cam lifts clutch yoke → clutch wheel meshes with 4th wheel and chrono center wheel simultaneously.  
- At *stop*: cam drops → clutch disengages, brake lever presses on chrono center wheel rim.  
- Teeth backlash is minimal; if amplitude drop exceeds 30 °, check clutch side-shake or lubrication (9010).

---

## 🧱 5 – Reset Mechanism

| Component | Function | Notes |
|------------|-----------|-------|
| **Hammer** | Dual-headed lever; strikes both heart cams. | Should rest 0.1 mm off hearts when “run.” |
| **Heart Cam (Chrono Center)** | Returns seconds hand to 12 o’clock. | Mounted friction-fit on post. |
| **Heart Cam (Minute Recorder)** | Returns minute hand to zero. | Mounted on minute recording wheel. |
| **Hammer Spring** | Flat spring anchored to main plate; provides return force. | Adjust tension for crisp reset. |
| **Brake Lever** | Contacts chrono center wheel rim during stop. | Releases before hammer falls. |

**Timing Logic:**
1. Reset pusher depressed.  
2. Brake lever lifts first (via coupling with hammer tail).  
3. Hammer falls; both hearts strike zero simultaneously.  
4. Spring returns hammer to rest; brake reapplies if chrono still “stopped.”

---

## 🔩 6 – Blocking System and Safety Interlocks

The 3133 uses a **cam-controlled blocking lever** to prevent reset while running:

- Lever tail rides on cam edge; when cam is in “run,” reset hammer is physically blocked.  
- On “stop,” cam recess frees hammer tail → allows reset.  
- This interlock prevents tooth shearing and is critical to correct chrono timing.

---

## 🧷 7 – Keyless & Click System

Hidden under chrono layer:
- **Ratchet Wheel** + Click + Click Spring = standard manual-wind setup.  
- **Setting Works** identical to Valjoux 7734 pattern.  
- The click’s inaccessibility explains why mainspring release requires upper-bridge removal.

---

## ⚖️ 8 – Regulation & Power Transmission

- Normal amplitude DU ≈ 270–300°, BE < 0.5 ms.  
- Chronograph engaged: amplitude drop ≤ 30°.  
- Excess drop → clutch drag, dried 4th-wheel jewel, or brake tension too high.

---

## 🧠 9 – Mental Model Exercise

Trace motion in your head:

